# Rapport OWASP ZAP Baseline Scan

**Cible :** https://temp2.guardiaroot.fr  
**Date :** 06/04/2026  
**Run GitHub Actions :** 24051864463  
**Résultat :** 0 FAIL — 9 WARN — 58 PASS

---

## Résumé

| Niveau   | Nombre |
|----------|--------|
| High     | 0      |
| Medium   | 0      |
| Low      | 9      |
| PASS     | 58     |

---

## Alertes (WARN)

| ID    | Alerte                                              | Occurrences |
|-------|-----------------------------------------------------|-------------|
| 10017 | Cross-Domain JavaScript Source File Inclusion       | x1          |
| 10019 | Content-Type Header Missing                         | x3          |
| 10020 | Missing Anti-clickjacking Header                    | x1          |
| 10021 | X-Content-Type-Options Header Missing               | x1          |
| 10038 | Content Security Policy (CSP) Header Not Set        | x1          |
| 10049 | Non-Storable Content                                | x2          |
| 10063 | Permissions Policy Header Not Set                   | x1          |
| 90003 | Sub Resource Integrity Attribute Missing            | x2          |
| 90004 | Cross-Origin-Embedder-Policy Header Missing         | x3          |

---

## Analyse

### Headers de sécurité manquants (10020, 10021, 10038, 10063, 90004)
Ces alertes sont gérées par **Flask-Talisman** en mode production.  
Cause : le scan a ciblé les pages statiques servies par nginx, qui ne passent pas par Flask.  
**Correction :** ajouter les headers manquants dans la config nginx.

### Sub Resource Integrity (90003)
Les CDN externes (Tailwind CSS, Font Awesome) chargés dans les HTML n'ont pas d'attribut `integrity`.  
Risque faible dans ce contexte académique.

### Cross-Domain JS Inclusion (10017)
Chargement de scripts depuis des CDN tiers (cdn.tailwindcss.com, cdnjs.cloudflare.com).  
Attendu et non exploitable en soi.

### Content-Type Header Missing (10019)
Certaines réponses statiques n'ont pas de header Content-Type explicite côté nginx.

---

## Checks passés notables (PASS)

- Cookie No HttpOnly Flag ✓
- Cookie Without Secure Flag ✓
- Cookie without SameSite Attribute ✓
- Strict-Transport-Security Header ✓
- Absence of Anti-CSRF Tokens ✓
- XSS (User Controllable HTML/JS) ✓
- SQL Injection / Application Error Disclosure ✓
- Information Disclosure (URL, Referrer, Debug) ✓
- Directory Browsing ✓
- Heartbleed ✓
- Private IP Disclosure ✓
- Session ID in URL ✓
- Weak Authentication Method ✓
