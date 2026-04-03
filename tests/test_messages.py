import pytest
from datetime import datetime, timedelta


# ─── GET /api/messages ───────────────────────────────────────────────────────

def test_get_messages_suid_manquant(client):
    response = client.get("/api/messages")
    assert response.status_code == 401


def test_get_messages_suid_invalide(client):
    response = client.get("/api/messages?suid=faux")
    assert response.status_code == 401


def test_get_messages_eleve(client, eleve_suid):
    """Un élève peut consulter les messages"""
    suid, *_ = eleve_suid
    response = client.get(f"/api/messages?suid={suid}")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_get_messages_prof(client, prof_suid):
    """Un prof peut consulter les messages"""
    suid, *_ = prof_suid
    response = client.get(f"/api/messages?suid={suid}")
    assert response.status_code == 200


def test_get_messages_direction(client, direction_suid):
    """La direction peut consulter les messages"""
    suid, *_ = direction_suid
    response = client.get(f"/api/messages?suid={suid}")
    assert response.status_code == 200


def test_get_messages_filtre_cible_eleves(client, message_fixture, eleve_suid):
    """Un élève voit les messages ciblant 'élève' ou 'tous'"""
    suid, *_ = eleve_suid
    response = client.get(f"/api/messages?suid={suid}")
    data = response.get_json()
    assert any(m["objet"] == "Avis aux élèves" for m in data)


def test_get_messages_filtre_cible_profs(client, message_fixture_profs, prof_suid):
    """Un prof voit les messages ciblant 'prof' ou 'tous'"""
    suid, *_ = prof_suid
    response = client.get(f"/api/messages?suid={suid}")
    data = response.get_json()
    assert any(m["objet"] == "Avis aux profs" for m in data)


def test_eleve_ne_voit_pas_message_profs(client, message_fixture_profs, eleve_suid):
    """Un élève ne voit PAS un message ciblant uniquement 'prof'"""
    suid, *_ = eleve_suid
    response = client.get(f"/api/messages?suid={suid}")
    data = response.get_json()
    assert not any(m["objet"] == "Avis aux profs" for m in data)


# ─── GET /api/messages/<id> ──────────────────────────────────────────────────

def test_get_message_par_id_eleve(client, message_fixture, eleve_suid):
    """Un élève peut lire un message qui le concerne"""
    suid, *_ = eleve_suid
    msg_id = message_fixture["msg_id"]
    response = client.get(f"/api/messages/{msg_id}?suid={suid}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["objet"] == "Avis aux élèves"


def test_get_message_introuvable(client, eleve_suid):
    """ID inexistant → 404"""
    suid, *_ = eleve_suid
    response = client.get(f"/api/messages/9999?suid={suid}")
    assert response.status_code == 404


def test_get_message_interdit_mauvaise_cible(client, message_fixture_profs, eleve_suid):
    """Un élève ne peut pas accéder à un message ciblant uniquement 'prof'"""
    suid, *_ = eleve_suid
    msg_id = message_fixture_profs["msg_id"]
    response = client.get(f"/api/messages/{msg_id}?suid={suid}")
    assert response.status_code == 403


# ─── POST /api/messages (publier) ────────────────────────────────────────────

def test_publier_message_direction_ok(client, direction_suid):
    """La direction peut publier un message → 201"""
    suid, *_ = direction_suid
    response = client.post(
        f"/api/messages?suid={suid}",
        json={
            "objet": "Réunion parents",
            "contenu": "Réunion le 10 avril.",
            "cible": "parent"
        }
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "id" in data


def test_publier_message_cible_tous(client, direction_suid):
    """La direction peut cibler 'tous'"""
    suid, *_ = direction_suid
    response = client.post(
        f"/api/messages?suid={suid}",
        json={
            "objet": "Fermeture exceptionnelle",
            "contenu": "L'établissement sera fermé vendredi.",
            "cible": "tous"
        }
    )
    assert response.status_code == 201


def test_publier_message_prof_ok(client, prof_suid):
    """Un employé (prof) peut publier un message → 201"""
    suid, *_ = prof_suid
    response = client.post(
        f"/api/messages?suid={suid}",
        json={
            "objet": "Rappel devoir",
            "contenu": "Pensez à rendre votre devoir.",
            "cible": "élève"
        }
    )
    assert response.status_code == 201


def test_publier_message_eleve_interdit(client, eleve_suid):
    """Un élève ne peut PAS publier de message → 403"""
    suid, *_ = eleve_suid
    response = client.post(
        f"/api/messages?suid={suid}",
        json={"objet": "Test", "contenu": "Texte", "cible": "tous"}
    )
    assert response.status_code == 403


def test_publier_message_champ_manquant(client, direction_suid):
    """Champ obligatoire manquant → 400"""
    suid, *_ = direction_suid
    response = client.post(
        f"/api/messages?suid={suid}",
        json={"objet": "Sans contenu"}
    )
    assert response.status_code == 400


def test_publier_message_cible_invalide(client, direction_suid):
    """Cible inconnue → 400"""
    suid, *_ = direction_suid
    response = client.post(
        f"/api/messages?suid={suid}",
        json={"objet": "Test", "contenu": "Texte", "cible": "martiens"}
    )
    assert response.status_code == 400


def test_publier_message_suid_manquant(client):
    """Sans suid → 401"""
    response = client.post(
        "/api/messages",
        json={"objet": "Test", "contenu": "Texte", "cible": "tous"}
    )
    assert response.status_code == 401


def test_publier_message_xss(client, direction_suid):
    """Contenu XSS doit être assaini ou rejeté"""
    suid, *_ = direction_suid
    xss = "<script>alert('xss')</script>"
    response = client.post(
        f"/api/messages?suid={suid}",
        json={"objet": xss, "contenu": xss, "cible": "tous"}
    )
    if response.status_code == 201:
        msg_id = response.get_json()["id"]
        r2 = client.get(f"/api/messages/{msg_id}?suid={suid}")
        data = r2.get_json()
        assert "<script>" not in data.get("objet", "")
        assert "<script>" not in data.get("contenu", "")
    else:
        assert response.status_code == 400


# ─── PATCH /api/messages/<id> (modifier) ─────────────────────────────────────

def test_modifier_message_ok(client, direction_suid, message_fixture):
    """La direction peut modifier un message → 200"""
    suid, *_ = direction_suid
    msg_id = message_fixture["msg_id"]
    response = client.patch(
        f"/api/messages/{msg_id}?suid={suid}",
        json={"contenu": "Contenu modifié"}
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["contenu"] == "Contenu modifié"


def test_modifier_message_eleve_interdit(client, eleve_suid, message_fixture):
    """Un élève ne peut PAS modifier un message → 403"""
    suid, *_ = eleve_suid
    msg_id = message_fixture["msg_id"]
    response = client.patch(
        f"/api/messages/{msg_id}?suid={suid}",
        json={"contenu": "Tentative de modif"}
    )
    assert response.status_code == 403


def test_modifier_message_introuvable(client, direction_suid):
    """Modifier un message inexistant → 404"""
    suid, *_ = direction_suid
    response = client.patch(
        f"/api/messages/9999?suid={suid}",
        json={"contenu": "Test"}
    )
    assert response.status_code == 404


def test_modifier_message_aucun_champ(client, direction_suid, message_fixture):
    """Modifier sans aucun champ valide → 400"""
    suid, *_ = direction_suid
    msg_id = message_fixture["msg_id"]
    response = client.patch(
        f"/api/messages/{msg_id}?suid={suid}",
        json={}
    )
    assert response.status_code == 400


def test_modifier_message_suid_manquant(client, message_fixture):
    """Sans suid → 401"""
    msg_id = message_fixture["msg_id"]
    response = client.patch(
        f"/api/messages/{msg_id}",
        json={"contenu": "Test"}
    )
    assert response.status_code == 401


# ─── DELETE /api/messages/<id> ───────────────────────────────────────────────

def test_supprimer_message_ok(client, direction_suid, message_fixture):
    """La direction peut supprimer un message → 200"""
    suid, *_ = direction_suid
    msg_id = message_fixture["msg_id"]
    response = client.delete(f"/api/messages/{msg_id}?suid={suid}")
    assert response.status_code == 200


def test_supprimer_message_eleve_interdit(client, eleve_suid, message_fixture):
    """Un élève ne peut PAS supprimer → 403"""
    suid, *_ = eleve_suid
    msg_id = message_fixture["msg_id"]
    response = client.delete(f"/api/messages/{msg_id}?suid={suid}")
    assert response.status_code == 403


def test_supprimer_message_suid_manquant(client, message_fixture):
    """Sans suid → 401"""
    msg_id = message_fixture["msg_id"]
    response = client.delete(f"/api/messages/{msg_id}")
    assert response.status_code == 401


def test_supprimer_message_introuvable(client, direction_suid):
    """ID inexistant → 404"""
    suid, *_ = direction_suid
    response = client.delete(f"/api/messages/9999?suid={suid}")
    assert response.status_code == 404


# ─── MESSAGES AUTOMATIQUES ───────────────────────────────────────────────────

@pytest.mark.skip(reason="blueprint cours pas encore créé")
def test_message_auto_cours_annule(client, app, direction_suid, cours_fixture):
    suid, *_ = direction_suid
    cours_id = cours_fixture["cours_id"]
    client.patch(
        f"/api/cours/{cours_id}?suid={suid}",
        json={"statut": "annulé"}
    )
    from app.models import Communication
    with app.app_context():
        msgs = Communication.query.filter(
            Communication.contenu.contains("annulé")
        ).all()
        assert len(msgs) >= 1


@pytest.mark.skip(reason="blueprint cours pas encore créé")
def test_message_auto_cours_deplace(client, app, direction_suid, cours_fixture):
    suid, *_ = direction_suid
    cours_id = cours_fixture["cours_id"]
    nouvelle_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d %H:%M")
    client.patch(
        f"/api/cours/{cours_id}?suid={suid}",
        json={"statut": "déplacé", "nouvelle_date": nouvelle_date}
    )
    from app.models import Communication
    with app.app_context():
        msgs = Communication.query.filter(
            Communication.contenu.contains("déplacé")
        ).all()
        assert len(msgs) >= 1


@pytest.mark.skip(reason="blueprint evenements pas encore créé")
def test_message_auto_evenement_cree(client, app, direction_suid):
    suid, *_ = direction_suid
    date_ev = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d %H:%M")
    client.post(
        f"/api/evenements?suid={suid}",
        json={
            "titre": "Journée portes ouvertes",
            "description": "Venez nous rendre visite !",
            "date_debut": date_ev,
            "lieu": "Hall principal"
        }
    )
    from app.models import Communication
    with app.app_context():
        msgs = Communication.query.filter(
            Communication.contenu.contains("Journée portes ouvertes")
        ).all()
        assert len(msgs) >= 1