// ════════════════════════════════════════════════════════════════
// ║                    DONNÉES & CONFIGURATION                    ║
// ════════════════════════════════════════════════════════════════

// ─── EDT API ────────────────────────────────────────────────────
const JOUR_NAMES = ['dimanche', 'lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi'];

function apiToMock(c) {
    const debut = new Date(c.debut);
    const fin   = new Date(c.fin);
    return {
        _id:     c.id,
        _raw:    c,
        jour:    JOUR_NAMES[debut.getDay()],
        debut:   debut.getHours() + debut.getMinutes() / 60,
        fin:     fin.getHours()   + fin.getMinutes()   / 60,
        matiere: c.matiere?.nom || 'Inconnu',
        prof:    (c.prof?.prenom && c.prof?.nom) ? `${c.prof.prenom} ${c.prof.nom}` : '',
        salle:   c.salle?.nom || '',
        etat:    c.etat,
        _annule: c.etat === 'annulé',
    };
}

async function loadCours(startDate) {
    const debut = new Date(startDate);
    debut.setHours(0, 0, 0, 0);
    const fin = new Date(startDate);
    fin.setDate(fin.getDate() + 6);
    fin.setHours(23, 59, 59, 999);
    try {
        const params = new URLSearchParams({ debut: debut.toISOString(), fin: fin.toISOString() });
        const res = await fetch('/edt/cours?' + params.toString());
        if (!res.ok) return;
        const data = await res.json();
        MOCK_COURS.splice(0, MOCK_COURS.length, ...data.map(apiToMock));
        renderCours();
    } catch (e) {
        console.error('Erreur chargement EDT:', e);
    }
}

// ─── MOCK SQL DATA / API CALLS ─────────────────────────────────
const MOCK_COURS = [
    { jour: 'lundi',    debut: 8.0,  fin: 9.0,  matiere: 'Mathématiques',    prof: 'M. Dupont',    salle: 'A101' },
    { jour: 'lundi',    debut: 10.0, fin: 12.0, matiere: 'Physique-Chimie',  prof: 'Mme. Leroy',   salle: 'Labo 2' },
    { jour: 'lundi',    debut: 10.5, fin: 13.5, matiere: 'SVT',              prof: 'M. Darwin',    salle: 'Labo 1' },
    // --------------------------------------------------------------
    { jour: 'lundi',    debut: 14.0, fin: 15.0, matiere: 'Histoire-Géo',     prof: 'M. Martin',    salle: 'B203' },
    { jour: 'mardi',    debut: 8.0,  fin: 9.0,  matiere: 'Anglais',          prof: 'Mme. Smith',   salle: 'C105' },
    { jour: 'mardi',    debut: 9.08,  fin: 10.5, matiere: 'Mathématiques',    prof: 'M. Dupont',    salle: 'A101' },
    { jour: 'mardi',    debut: 9.08, fin: 10.5, matiere: 'Informatique',     prof: 'M. Bernard',   salle: 'Salle Info' },
    { jour: 'mercredi', debut: 8.0,  fin: 10.0, matiere: 'Français',         prof: 'Mme. Moreau',  salle: 'B104' },
    { jour: 'mercredi', debut: 10.0, fin: 11.0, matiere: 'Philosophie',      prof: 'M. Rousseau',  salle: 'C201' },
    { jour: 'jeudi',    debut: 8.5,  fin: 10.0, matiere: 'Physique-Chimie',  prof: 'Mme. Leroy',   salle: 'Labo 2' },
    { jour: 'jeudi',    debut: 10.0, fin: 11.0, matiere: 'Anglais',          prof: 'Mme. Smith',   salle: 'C105' },
    { jour: 'jeudi',    debut: 14.0, fin: 15.5, matiere: 'Français',         prof: 'Mme. Moreau',  salle: 'B104' },
    { jour: 'jeudi',    debut: 15.5, fin: 18.0, matiere: 'EPS',              prof: 'M. Girard',    salle: 'Gymnase' },
    { jour: 'vendredi', debut: 9.0,  fin: 11.0, matiere: 'Histoire-Géo',     prof: 'M. Martin',    salle: 'B203' },
    { jour: 'vendredi', debut: 11.0, fin: 12.0, matiere: 'Philosophie',      prof: 'M. Rousseau',  salle: 'C201' },
    { jour: 'vendredi', debut: 14.0, fin: 15.0, matiere: 'Informatique',     prof: 'M. Bernard',   salle: 'Salle Info' },
    { jour: 'samedi',   debut: 8.0,  fin: 10.0, matiere: 'Mathématiques',    prof: 'M. Dupont',    salle: 'A101' },
    { jour: 'samedi',   debut: 10.0, fin: 11.0, matiere: 'EPS',              prof: 'M. Girard',    salle: 'Gymnase' },
];

const MATIERE_COLORS = {
    'Mathématiques':   { bg: '#e0e7ff', border: '#6366f1', text: '#3730a3' },
    'Physique-Chimie': { bg: '#e0f2fe', border: '#0ea5e9', text: '#0369a1' },
    'SVT':             { bg: '#dcfce7', border: '#16a34a', text: '#166534' }, // Vert foncé
    'Histoire-Géo':    { bg: '#fef3c7', border: '#f59e0b', text: '#92400e' },
    'Anglais':         { bg: '#d1fae5', border: '#10b981', text: '#065f46' },
    'Français':        { bg: '#fce7f3', border: '#ec4899', text: '#9d174d' },
    'Informatique':    { bg: '#ede9fe', border: '#8b5cf6', text: '#5b21b6' },
    'Philosophie':     { bg: '#ffedd5', border: '#fb923c', text: '#9a3412' },
    'EPS':             { bg: '#dcfce7', border: '#22c55e', text: '#14532d' },
};

const FALLBACK_COLORS = [
    { bg: '#fee2e2', border: '#ef4444', text: '#7f1d1d' },
    { bg: '#ccfbf1', border: '#14b8a6', text: '#134e4a' },
    { bg: '#fef08a', border: '#eab308', text: '#713f12' },
];
let fallbackIdx = 0;

// ════════════════════════════════════════════════════════════════
// ║              UTILITAIRES & FONCTIONS GLOBALES                 ║
// ════════════════════════════════════════════════════════════════

function getColor(matiere) {
    if (!MATIERE_COLORS[matiere]) {
        MATIERE_COLORS[matiere] = FALLBACK_COLORS[fallbackIdx % FALLBACK_COLORS.length];
        fallbackIdx++;
    }
    return MATIERE_COLORS[matiere];
}

function formatHeure(decimal) {
    const h = Math.floor(decimal);
    const m = Math.round((decimal - h) * 60);
    return `${h}h${m > 0 ? m.toString().padStart(2,'0') : '00'}`;
}

// ─── NOUVEL ALGORITHME DE RENDU (Gère les superpositions) ────────
function renderCours() {
    const START_HOUR = 8;
    const TOTAL_HOURS = 10;
    const joursDeLaSemaine = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi'];
    
    // Détecter si on est sur la page emploi du temps
    const isEdtPage = document.body.classList.contains('edt-page') || 
                      window.location.pathname.includes('edt') || 
                      document.getElementById('weeks-container') !== null;

    joursDeLaSemaine.forEach(jour => {
        const container = document.querySelector(`[data-jour="${jour}"] #sql-courses-container-${jour}`);
        if (!container) return;

        // 1. Filtrer les cours du jour et les trier chronologiquement
        let coursDuJour = MOCK_COURS
            .filter(c => c.jour === jour)
            .sort((a, b) => a.debut - b.debut);

        // 2. Créer des grappes (clusters) de cours qui se chevauchent
        let clusters = [];
        let currentCluster = [];
        let clusterEnd = -1;

        coursDuJour.forEach(cours => {
            if (currentCluster.length === 0) {
                currentCluster.push(cours);
                clusterEnd = cours.fin;
            } else if (cours.debut < clusterEnd) {
                currentCluster.push(cours);
                clusterEnd = Math.max(clusterEnd, cours.fin);
            } else {
                clusters.push(currentCluster);
                currentCluster = [cours];
                clusterEnd = cours.fin;
            }
        });
        if (currentCluster.length > 0) {
            clusters.push(currentCluster);
        }

        // 3. Assigner les colonnes pour chaque grappe
        clusters.forEach(cluster => {
            let colonnes = [];
            
            cluster.forEach(cours => {
                let placeTrouvee = false;
                for (let i = 0; i < colonnes.length; i++) {
                    let dernierCoursDeLaColonne = colonnes[i][colonnes[i].length - 1];
                    if (cours.debut >= dernierCoursDeLaColonne.fin) {
                        colonnes[i].push(cours);
                        placeTrouvee = true;
                        break;
                    }
                }
                if (!placeTrouvee) {
                    colonnes.push([cours]); // Crée une nouvelle colonne
                }
            });

            let nombreDeColonnes = colonnes.length; // Ex: 2 ou 3

            // 4. Dessiner les cours avec leur nouvelle largeur
            colonnes.forEach((colonne, colIndex) => {
                colonne.forEach(cours => {
                    const color = getColor(cours.matiere);
                    const topPct    = ((cours.debut - START_HOUR) / TOTAL_HOURS) * 100;
                    const heightPct = ((cours.fin - cours.debut) / TOTAL_HOURS) * 100;
                    
                    // CALCUL DU SPLIT 50/50, 33/33/33, etc.
                    const widthPct = 100 / nombreDeColonnes;
                    const leftPct = colIndex * widthPct;

                    const block = document.createElement('div');
                    block.className = 'cours-block';
                    if (cours._id) block.dataset.coursId = cours._id;
                    
                    // On injecte left et width en % au lieu de forcer à 4px du bord
                    block.style.cssText = `
                        top: ${topPct}%;
                        height: ${heightPct}%;
                        left: calc(${leftPct}% + 1px);
                        width: calc(${widthPct}% - 2px);
                        background: ${color.bg};
                        border: 1.5px solid ${color.border};
                        border-left: 3px solid ${color.border};
                        border-radius: 0; /* Suppression des arrondis demandée */
                    `;

                    // Format d'affichage différent selon la page
                    if (isEdtPage) {
                        // Format pour la page emploi du temps (avec prof et salle)
                        block.innerHTML = `
                            <div class="cours-inner" style="border-radius: 0; gap: 2px; padding: 2px;">
                                <span class="cours-nom" style="color: ${color.text}">${cours.matiere}</span>
                                <span class="cours-infos" style="color: black">${cours.prof}</span>
                                <span class="cours-infos" style="color: black">${cours.salle}</span>
                            </div>
                            <div class="cours-tooltip">
                                <div style="font-weight:700; font-size:11px; margin-bottom:3px; color:${color.border}">${cours.matiere}</div>
                                <div>🕐 ${formatHeure(cours.debut)} – ${formatHeure(cours.fin)}</div>
                                <div>👨‍🏫 ${cours.prof}</div>
                                <div>📍 ${cours.salle}</div>
                            </div>
                        `;
                    } else {
                        // Format pour la page accueil (matière seulement + tooltip complet)
                        block.innerHTML = `
                            <div class="cours-inner" style="border-radius: 0;">
                                <span class="cours-nom" style="color: ${color.text}">${cours.matiere}</span>
                            </div>
                            <div class="cours-tooltip">
                                <div style="font-weight:700; font-size:11px; margin-bottom:3px; color:${color.border}">${cours.matiere}</div>
                                <div>🕐 ${formatHeure(cours.debut)} – ${formatHeure(cours.fin)}</div>
                                <div>👨‍🏫 ${cours.prof}</div>
                                <div>📍 ${cours.salle}</div>
                            </div>
                        `;
                    }

                    container.appendChild(block);
                });
            });
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
    // ════════════════════════════════════════════════════════════════
    // ║                 INITIALISATION & SETUP                        ║
    // ════════════════════════════════════════════════════════════════

    const months = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'];
    
    const now = new Date();
    let currentDayIndex = now.getDay();
    if (currentDayIndex === 0) currentDayIndex = 7; 

    const monday = new Date(now);
    monday.setDate(now.getDate() - currentDayIndex + 1);

    document.querySelectorAll('.jour-container').forEach(container => {
        const dayIndex = parseInt(container.getAttribute('data-index')); 
        const jour = container.getAttribute('data-jour');
        const hasCourses = MOCK_COURS.some(c => c.jour === jour);
        
        const dayDate = new Date(monday);
        dayDate.setDate(monday.getDate() + (dayIndex - 1));
        
        container.querySelector('.jour-date').textContent = `${dayDate.getDate()} ${months[dayDate.getMonth()]}`;
        
        const sqlDate = dayDate.toISOString().split('T')[0];
        container.setAttribute('data-date', sqlDate);

        const baseHeaderClass = "en-tete-jour py-1 flex flex-col items-center border-b border-slate-300/50 rounded-t-xl transition-colors flex-shrink-0";
        
        // Vérifier si c'est aujourd'hui (même jour et même date)
        const isToday = dayIndex === currentDayIndex && 
                       dayDate.getDate() === now.getDate() && 
                       dayDate.getMonth() === now.getMonth() && 
                       dayDate.getFullYear() === now.getFullYear();
        
        if (isToday) {
            container.className = "jour-container flex-1 h-full bg-white shadow-md rounded-xl flex flex-col relative z-20 transition-all";
            if (!container.querySelector('.today-border-overlay')) {
                const overlay = document.createElement('div');
                overlay.className = 'today-border-overlay absolute inset-0 rounded-xl pointer-events-none z-50';
                overlay.style.boxShadow = 'inset 0 0 0 2px #818cf8';
                container.appendChild(overlay);
            }
            container.querySelector('.en-tete-jour').className = `${baseHeaderClass} bg-indigo-100 border-indigo-200`;
            container.querySelector('.jour-nom').className = "jour-nom text-[10px] font-bold text-indigo-800 uppercase";
            container.querySelector('.jour-date').className = "jour-date text-[8px] text-indigo-600 font-medium";
        } else {
            // Gris seulement si c'est samedi ET qu'il n'y a pas de cours
            let extraClass = (dayIndex === 6 && !hasCourses) ? "opacity-70 grayscale-[0.5]" : "";
            container.className = `jour-container flex-1 h-full bg-white/60 shadow-sm rounded-xl flex flex-col hover:bg-white/80 transition-all z-20 ${extraClass}`;
            container.querySelector('.en-tete-jour').className = `${baseHeaderClass} bg-slate-50/50`;
            container.querySelector('.jour-nom').className = "jour-nom text-[10px] font-bold text-slate-600 uppercase";
            container.querySelector('.jour-date').className = "jour-date text-[8px] text-slate-400";
        }
    });

    // ════════════════════════════════════════════════════════════════
    // ║              RÉCUPÉRATION DES DONNÉES (API)                   ║
    // ════════════════════════════════════════════════════════════════
    // TODO: Remplacer MOCK_NOTES par: await fetch('/api/notes')
    // TODO: Remplacer MOCK_TRAVAIL par: await fetch('/api/travail')
    // TODO: Remplacer MOCK_ASSIDUITY par: await fetch('/api/assiduity')

    // --- DONNÉES DE TEST POUR LES NOTES (À lier à SQL plus tard) ---
    const MOCK_NOTES = [
        { matiere: 'Mathématiques', date: '25/03/2026', note: 18.5, max: 20 },
        { matiere: 'Anglais', date: '24/03/2026', note: 14.0, max: 20 },
        { matiere: 'Physique-Chimie', date: '20/03/2026', note: 9.5, max: 20 },
        { matiere: 'Physique-Chimie', date: '20/03/2026', note: 9.5, max: 20 },
        { matiere: 'Physique-Chimie', date: '20/03/2026', note: 9.5, max: 20 },
        { matiere: 'Physique-Chimie', date: '20/03/2026', note: 9.5, max: 20 },
        { matiere: 'Physique-Chimie', date: '20/03/2026', note: 9.5, max: 20 },
    ];

    // --- DONNÉES DE TEST POUR LES DEVOIRS ET DS ---
    const MOCK_TRAVAIL = {
        ds: [
            { matiere: 'Mathématiques', date: '30/03/2026', salle: 'A101', duree: '2h', programme: 'Chapitres 1-5' },
            { matiere: 'Français', date: '02/04/2026', salle: 'B104', duree: '3h', programme: 'Poésie' }
        ],
        devoirs: [
            { date: '27/03/2026', items: [
                { matiere: 'Mathématiques', description: 'Exercices 1-10 page 45', type: 'sans_rendu' },
                { matiere: 'Français', description: 'Résumé du chapitre 3', type: 'sans_rendu' }
            ]},
            { date: '28/03/2026', items: [
                { matiere: 'Anglais', description: 'Dialogue à enregistrer', type: 'avec_rendu', lien: '/travail/anglais' },
                { matiere: 'Informatique', description: 'Projet Python', type: 'avec_rendu', lien: '/travail/informatique' }
            ]},
            { date: '29/03/2026', items: [
                { matiere: 'Histoire-Géo', description: 'Fiche de révision', type: 'sans_rendu' }
            ]}
        ]
    };

    // --- DONNÉES DE TEST POUR L'ASSIDUITÉ ---
    const MOCK_ASSIDUITY = {
        retards_absences: [
            { type: 'Retard', date: '25/03/2026', heure: '08h15' },
            { type: 'Absence justifiée', date: '24/03/2026', debut: '10h00', fin: '12h00' },
            { type: 'Absence non justifiée', date: '20/03/2026', debut: '14h00', fin: '15h00' }
        ],
        punitions: [
            { type: 'Retenue', date: '28/03/2026', heure: '17h00', salle: 'A101', par: 'M. Dupont' },
            { type: 'Retenue', date: '01/04/2026', heure: '17h30', salle: 'B204', par: 'Mme. Leroy' }
        ]
    };

    // Fonction pour déterminer la couleur du carré selon la note
    function getGradeColor(note, max) {
        const ratio = note / max;
        if (ratio >= 0.6) return 'bg-emerald-100 text-emerald-700 border-emerald-200'; // Vert (Bonne note)
        return 'bg-amber-100 text-amber-700 border-amber-200';                         // Rouge (Insuffisant)
    }

    // ════════════════════════════════════════════════════════════════
    // ║                  GESTION DES NOTES                           ║
    // ════════════════════════════════════════════════════════════════

    let notesVisible = true;

    function renderNotes() {
        const container = document.getElementById('notes-list');
        if (!container) return;

        MOCK_NOTES.slice(0, 5).forEach((item, itemIndex) => {
            const colorClass = getGradeColor(item.note, item.max);
            const row = document.createElement('div');
            // Structure de la ligne : Infos à gauche, Carré à droite
            row.className = 'flex justify-between items-center border-b border-slate-50 pb-2 last:border-0 last:pb-0';
            
            const scoreBox = document.createElement('div');
            scoreBox.className = `w-10 h-10 rounded-lg border ${colorClass} flex flex-col items-center justify-center shadow-sm notes-score cursor-pointer`;
            scoreBox.setAttribute('data-note-index', itemIndex);
            scoreBox.setAttribute('data-hidden', 'false');
            scoreBox.setAttribute('data-color-class', colorClass);
            scoreBox.innerHTML = `
                <span class="text-xs font-bold note-value">${item.note}</span>
                <span class="text-[8px] opacity-70">/${item.max}</span>
            `;
            
            const infoPart = document.createElement('div');
            infoPart.className = 'flex-1';
            infoPart.innerHTML = `
                <span class="text-[11px] font-bold text-slate-700">${item.matiere}</span><br>
                <span class="text-[9px] text-slate-400 font-medium">${item.date}</span>
            `;
            
            row.appendChild(infoPart);
            row.appendChild(scoreBox);
            container.appendChild(row);
            
            // Event pour cliquer sur la note
            scoreBox.addEventListener('click', function(e) {
                e.stopPropagation();
                const isHidden = this.getAttribute('data-hidden') === 'true';
                const colorClass = this.getAttribute('data-color-class');
                
                if (isHidden) {
                    // Afficher la note
                    this.className = `w-10 h-10 rounded-lg border ${colorClass} flex flex-col items-center justify-center shadow-sm notes-score cursor-pointer`;
                    this.innerHTML = `
                        <span class="text-xs font-bold note-value">${item.note}</span>
                        <span class="text-[8px] opacity-70">/${item.max}</span>
                    `;
                    this.setAttribute('data-hidden', 'false');
                } else {
                    // Cacher la note et afficher l'oeil barré sans couleur
                    this.className = 'w-10 h-10 rounded-lg border border-slate-200 bg-slate-50 flex items-center justify-center shadow-sm notes-score cursor-pointer';
                    this.innerHTML = '<i class="fas fa-eye-slash text-slate-400 text-sm"></i>';
                    this.setAttribute('data-hidden', 'true');
                }
            });
        });
    }

    function toggleNotesVisibility() {
        notesVisible = !notesVisible;
        const noteScores = document.querySelectorAll('.notes-score');
        const eyeIcon = document.getElementById('notes-eye-icon');
        
        noteScores.forEach((score) => {
            const noteIndex = score.getAttribute('data-note-index');
            const item = MOCK_NOTES[noteIndex];
            const colorClass = score.getAttribute('data-color-class');
            
            if (notesVisible) {
                // Afficher toutes les notes
                score.className = `w-10 h-10 rounded-lg border ${colorClass} flex flex-col items-center justify-center shadow-sm notes-score cursor-pointer`;
                score.innerHTML = `
                    <span class="text-xs font-bold note-value">${item.note}</span>
                    <span class="text-[8px] opacity-70">/${item.max}</span>
                `;
                score.setAttribute('data-hidden', 'false');
            } else {
                // Cacher toutes les notes
                score.className = 'w-10 h-10 rounded-lg border border-slate-200 bg-slate-50 flex items-center justify-center shadow-sm notes-score cursor-pointer';
                score.innerHTML = '<i class="fas fa-eye-slash text-slate-400 text-sm"></i>';
                score.setAttribute('data-hidden', 'true');
            }
        });

        eyeIcon.className = notesVisible ? 'fas fa-eye' : 'fas fa-eye-slash';
    }

    renderNotes();
    
    // Ajouter l'écouteur au bouton œil
    const eyeButton = document.getElementById('notes-eye-btn');
    if (eyeButton) {
        eyeButton.addEventListener('click', toggleNotesVisibility);
    }

    // ════════════════════════════════════════════════════════════════
    // ║              GESTION DES DEVOIRS ET DS                        ║
    // ════════════════════════════════════════════════════════════════

    function renderTravail() {
        const container = document.getElementById('travail-list');
        if (!container) return;

        // Afficher les DS
        if (MOCK_TRAVAIL.ds.length > 0) {
            const dsTitle = document.createElement('div');
            dsTitle.className = 'text-[11px] font-bold text-indigo-900 mb-3 uppercase';
            dsTitle.textContent = 'Prochains DS';
            container.appendChild(dsTitle);

            MOCK_TRAVAIL.ds.forEach(ds => {
                const dsItem = document.createElement('div');
                dsItem.className = 'bg-violet-100 border-l-4 border-violet-500 p-3 mb-2 flex gap-3 items-center justify-between';
                
                const datePart = document.createElement('div');
                datePart.className = 'flex flex-col items-center text-center';
                const [day, month, year] = ds.date.split('/');
                datePart.innerHTML = `
                    <div class="text-[12px] font-bold text-violet-700">${day}</div>
                    <div class="text-[8px] text-violet-600 uppercase">janv.</div>
                `;
                
                const infoPart = document.createElement('div');
                infoPart.className = 'flex-1';
                infoPart.innerHTML = `
                    <div class="text-[11px] font-bold text-slate-900">${ds.matiere}</div>
                    <div class="text-[9px] font-semibold text-slate-700 mb-1">${ds.salle}</div>
                    <div class="text-[8px] font-semibold text-slate-700">Réviser le chapitre 4 à 9</div>
                `;
                
                const buttonPart = document.createElement('a');
                buttonPart.href = '/cours/' + ds.matiere.toLowerCase().replace(/\s+/g, '-');
                buttonPart.className = 'bg-violet-500 hover:bg-violet-600 text-white text-[10px] font-bold px-2 py-1 rounded transition-colors whitespace-nowrap';
                buttonPart.textContent = 'Se rendre sur le cours';
                
                dsItem.appendChild(datePart);
                dsItem.appendChild(infoPart);
                dsItem.appendChild(buttonPart);
                container.appendChild(dsItem);
            });
        }

        // Afficher les devoirs regroupés par date
        MOCK_TRAVAIL.devoirs.forEach(dateGroup => {
            // Afficher le titre une seule fois avant le premier groupe de devoirs
            if (MOCK_TRAVAIL.devoirs.indexOf(dateGroup) === 0) {
                const devoirTitle = document.createElement('div');
                devoirTitle.className = 'text-[11px] font-bold text-indigo-900 mb-2 uppercase';
                devoirTitle.textContent = 'Travail à faire';
                container.appendChild(devoirTitle);
            }
            
            // En-tête de la date avec flèche déroulante
            const dateHeader = document.createElement('div');
            dateHeader.className = 'bg-indigo-100 text-indigo-900 text-[10px] font-bold p-2 mb-1 rounded flex items-center justify-between cursor-pointer hover:bg-indigo-200 transition-colors';
            
            const dateObj = new Date(dateGroup.date.split('/').reverse().join('-'));
            const days = ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'];
            const months = ['janvier', 'février', 'mars', 'avr', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'];
            const dayName = days[dateObj.getDay()];
            const dayNum = dateObj.getDate();
            const monthName = months[dateObj.getMonth()];
            
            const dateText = document.createElement('span');
            dateText.textContent = `Pour le ${dayName} ${dayNum} ${monthName}`;
            
            const toggleIcon = document.createElement('i');
            toggleIcon.className = 'fas fa-chevron-down text-[8px]';
            
            dateHeader.appendChild(dateText);
            dateHeader.appendChild(toggleIcon);
            container.appendChild(dateHeader);

            // Conteneur des devoirs du jour
            const devoirsDayContainer = document.createElement('div');
            devoirsDayContainer.className = 'devoirs-day-container';
            devoirsDayContainer.style.display = 'block';
            
            // Devoirs regroupés par matière
            const matiereGroups = {};
            dateGroup.items.forEach(item => {
                if (!matiereGroups[item.matiere]) {
                    matiereGroups[item.matiere] = [];
                }
                matiereGroups[item.matiere].push(item);
            });

            Object.keys(matiereGroups).forEach(matiere => {
                matiereGroups[matiere].forEach(devoir => {
                    const devoirItem = document.createElement('div');
                    devoirItem.className = 'flex items-center justify-between gap-2 pl-3 py-1 border-l-2 border-indigo-300';
                    
                    const textPart = document.createElement('div');
                    textPart.className = 'flex-1';
                    textPart.innerHTML = `
                        <div class="text-[10px] font-bold text-slate-800">• ${matiere}</div>
                        <div class="text-[9px] font-semibold text-slate-700">${devoir.description}</div>
                    `;
                    
                    if (devoir.type === 'sans_rendu') {
                        const checkboxPart = document.createElement('div');
                        checkboxPart.className = 'flex items-center gap-2';
                        checkboxPart.innerHTML = `
                            <input type="checkbox" class="devoir-checkbox w-4 h-4 cursor-pointer" title="Marquer comme fait">
                        `;
                        devoirItem.appendChild(textPart);
                        devoirItem.appendChild(checkboxPart);
                    } else {
                        const button = document.createElement('a');
                        button.href = devoir.lien;
                        button.className = 'bg-indigo-200 hover:bg-indigo-300 text-indigo-900 text-[9px] font-bold px-3 py-1 rounded transition-colors';
                        button.textContent = 'Déposer ma copie';
                        devoirItem.appendChild(textPart);
                        devoirItem.appendChild(button);
                    }
                    
                    devoirsDayContainer.appendChild(devoirItem);
                });
            });

            container.appendChild(devoirsDayContainer);
            
            // Ajouter l'événement de toggle
            dateHeader.addEventListener('click', () => {
                const isHidden = devoirsDayContainer.style.display === 'none';
                devoirsDayContainer.style.display = isHidden ? 'block' : 'none';
                toggleIcon.style.transform = isHidden ? 'rotate(180deg)' : 'rotate(0deg)';
                toggleIcon.style.transition = 'transform 0.3s ease';
            });
        });
    }

    renderTravail();

    // ════════════════════════════════════════════════════════════════
    // ║              GESTION DE L'ASSIDUITÉ                           ║
    // ════════════════════════════════════════════════════════════════

    function renderAssiduity() {
        const retardContainer = document.getElementById('assiduity-retard');
        const punitionContainer = document.getElementById('assiduity-punition');
        
        if (!retardContainer || !punitionContainer) return;

        // Afficher Retard/Absence (max 3 éléments)
        MOCK_ASSIDUITY.retards_absences.slice(0, 3).forEach((item, index) => {
            const item_element = document.createElement('div');
            
            // Déterminer la couleur selon le type
            let bgColor = 'bg-orange-50';
            let borderColor = 'border-orange-400';
            let textColor = 'text-orange-700';
            
            if (item.type === 'Absence non justifiée') {
                bgColor = 'bg-red-50';
                borderColor = 'border-red-400';
                textColor = 'text-red-700';
            } else if (item.type === 'Absence justifiée') {
                bgColor = 'bg-emerald-50';
                borderColor = 'border-emerald-400';
                textColor = 'text-emerald-700';
            }
            
            item_element.className = `flex flex-col gap-0.5 p-1.5 ${bgColor} rounded border-l-2 ${borderColor} mb-1`;
            
            const typeSpan = document.createElement('span');
            typeSpan.className = `text-[8.5px] font-bold ${textColor}`;
            typeSpan.textContent = item.type;
            
            const dateSpan = document.createElement('span');
            dateSpan.className = 'text-[7.5px] font-semibold text-slate-700';
            dateSpan.textContent = item.date;
            
            item_element.appendChild(typeSpan);
            item_element.appendChild(dateSpan);
            
            if (item.type === 'Retard') {
                const heureSpan = document.createElement('span');
                heureSpan.className = 'text-[7.5px] font-semibold text-slate-700';
                heureSpan.textContent = `Arrivée: ${item.heure}`;
                item_element.appendChild(heureSpan);
            } else {
                const heuresSpan = document.createElement('span');
                heuresSpan.className = 'text-[7.5px] font-semibold text-slate-700';
                heuresSpan.textContent = `${item.debut} - ${item.fin}`;
                item_element.appendChild(heuresSpan);
            }
            
            retardContainer.appendChild(item_element);
        });

        // Afficher Punitions (max 3 éléments)
        MOCK_ASSIDUITY.punitions.slice(0, 3).forEach((item, index) => {
            const item_element = document.createElement('div');
            item_element.className = 'flex flex-col gap-0.5 p-1.5 bg-orange-50 rounded border-l-2 border-orange-400 mb-1';
            
            const typeSpan = document.createElement('span');
            typeSpan.className = 'text-[8.5px] font-bold text-orange-700';
            typeSpan.textContent = item.type;
            
            const dateSpan = document.createElement('span');
            dateSpan.className = 'text-[7.5px] font-semibold text-slate-700';
            dateSpan.textContent = item.date;
            
            // Heure et personne sur la même ligne
            const infoLine = document.createElement('div');
            infoLine.className = 'text-[7.5px] font-semibold text-slate-700 flex items-center gap-1';
            infoLine.textContent = `${item.heure} • ${item.salle} • ${item.par}`;
            
            item_element.appendChild(typeSpan);
            item_element.appendChild(dateSpan);
            item_element.appendChild(infoLine);
            
            punitionContainer.appendChild(item_element);
        });
    }

    renderAssiduity();

    renderCours();

    // ════════════════════════════════════════════════════════════════
    // ║                   FIN DU SCRIPT                               ║
    // ════════════════════════════════════════════════════════════════

    // ════════════════════════════════════════════════════════════════
    // ║        GESTION DE LA NAVIGATION PAR ONGLETS                  ║
    // ════════════════════════════════════════════════════════════════

    (function(){
        const tabs = Array.from(document.querySelectorAll('.tab-btn'));
        const resultatBtn = document.getElementById('resultats-btn');
        const resultatMenu = document.getElementById('resultats-menu');
        let hoverTimeout = null;
        
        // Détecter automatiquement la page actuelle en fonction du pathname
        function detectCurrentPage() {
            const pageMap = {
                '/': 'accueil',
                '/edt': 'edt',
                '/notes': 'notes',
                '/travail': 'cahier-textes',
            };
            return pageMap[window.location.pathname] || 'accueil';
        }
        
        let activePage = detectCurrentPage();
        
        function activateTab(btn, isPermanent = false) {
            tabs.forEach(t => {
                // Ne pas désactiver le bouton de la page active
                if (t.dataset.tab !== activePage) {
                    t.classList.remove('bg-white','text-indigo-900','shadow-sm', 'border-red-500');
                    t.classList.add('text-white');
                    t.setAttribute('aria-selected','false');
                }
            });
            btn.classList.add('bg-white','text-indigo-900','shadow-sm','border-red-500');
            btn.classList.remove('text-white');
            btn.setAttribute('aria-selected','true');

            if (isPermanent) {
                activePage = btn.dataset.tab;
            }

            // Event for other scripts to react to tab change
            document.body.dispatchEvent(new CustomEvent('tab-change', { detail: { tab: btn.dataset.tab } }));
        }

        // Gestion du hover sur tous les tabs (sauf Résultats)
        tabs.forEach(t => {
            if (t.id !== 'resultats-btn') {
                t.addEventListener('mouseenter', () => {
                    // Fermer le menu Résultats si ouvert
                    if (resultatMenu) {
                        resultatMenu.classList.add('hidden');
                        if (resultatBtn) resultatBtn.setAttribute('aria-expanded','false');
                    }
                    // Ne pas changer le style si c'est la page active
                    if (t.dataset.tab !== activePage) {
                        clearTimeout(hoverTimeout);
                        activateTab(t, false);
                    }
                });
                
                t.addEventListener('mouseleave', () => {
                    clearTimeout(hoverTimeout);
                    hoverTimeout = setTimeout(() => {
                        // Retourner à la page active
                        const activeBtn = document.querySelector(`[data-tab="${activePage}"]`);
                        if (activeBtn) activateTab(activeBtn, false);
                    }, 150);
                });
                
                t.addEventListener('click', (e) => {
                    clearTimeout(hoverTimeout);
                    resultatMenu.classList.add('hidden');
                    if (resultatBtn) resultatBtn.setAttribute('aria-expanded','false');
                    activateTab(t, true);
                    // if a target href is provided, navigate to it
                    if (t.dataset.href) {
                        setTimeout(() => { window.location.href = t.dataset.href; }, 50);
                    }
                });
            }
            
            t.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') { 
                    e.preventDefault();
                    activateTab(t, true);
                    if (t.dataset.href) {
                        setTimeout(() => { window.location.href = t.dataset.href; }, 50);
                    }
                }
            });
        });
        
        // Gestion du menu Résultats - HOVER ONLY
        if (resultatBtn) {
            resultatBtn.addEventListener('mouseenter', () => {
                clearTimeout(hoverTimeout);
                resultatMenu.classList.remove('hidden');
                resultatBtn.setAttribute('aria-expanded','true');
                // Afficher le bouton en actif sans le rendre permanent
                activateTab(resultatBtn, false);
            });
            
            resultatBtn.addEventListener('mouseleave', () => {
                clearTimeout(hoverTimeout);
                hoverTimeout = setTimeout(() => {
                    if (!resultatMenu.matches(':hover')) {
                        resultatMenu.classList.add('hidden');
                        resultatBtn.setAttribute('aria-expanded','false');
                        // Retourner à la page active
                        const activeBtn = document.querySelector(`[data-tab="${activePage}"]`);
                        if (activeBtn) activateTab(activeBtn, false);
                    }
                }, 150);
            });
            
            // Pas de clic sur le bouton lui-même - le bouton ne navigue pas
            resultatBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        }

        // Keep menu visible while hovering it
        if (resultatMenu) {
            resultatMenu.addEventListener('mouseenter', () => {
                clearTimeout(hoverTimeout);
            });
            resultatMenu.addEventListener('mouseleave', () => {
                clearTimeout(hoverTimeout);
                hoverTimeout = setTimeout(() => {
                    resultatMenu.classList.add('hidden');
                    if (resultatBtn) resultatBtn.setAttribute('aria-expanded','false');
                    const activeBtn = document.querySelector(`[data-tab="${activePage}"]`);
                    if (activeBtn) activateTab(activeBtn, false);
                }, 150);
            });
            
            // Gestion des clics sur les liens du menu
            const menuLinks = resultatMenu.querySelectorAll('.menu-link');
            menuLinks.forEach(link => {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    resultatMenu.classList.add('hidden');
                    if (resultatBtn) resultatBtn.setAttribute('aria-expanded','false');
                    const activeBtn = document.querySelector(`[data-tab="${activePage}"]`);
                    if (activeBtn) activateTab(activeBtn, false);
                    
                    // Navigate using data-href like tabs do
                    if (link.dataset.href) {
                        setTimeout(() => { window.location.href = link.dataset.href; }, 50);
                    }
                });
            });
        }
        
        // Fermer le menu en cliquant ailleurs
        document.addEventListener('click', (e) => {
            if (resultatBtn && resultatMenu && !resultatBtn.contains(e.target) && !resultatMenu.contains(e.target)) {
                resultatMenu.classList.add('hidden');
                if (resultatBtn) resultatBtn.setAttribute('aria-expanded','false');
                const activeBtn = document.querySelector(`[data-tab="${activePage}"]`);
                if (activeBtn) activateTab(activeBtn, false);
            }
        });
        
        // Initialize with detected page
        const detectedBtn = document.querySelector(`[data-tab="${activePage}"]`);
        if (detectedBtn) {
            activateTab(detectedBtn, true);
        }
    })();

    // ════════════════════════════════════════════════════════════════
    // ║        GESTION DE LA SÉLECTION DES SEMAINES (CALENDRIER)     ║
    // ════════════════════════════════════════════════════════════════

    // Dates de référence: du 1er juillet 2026 au 30 juin 2027
    const REFERENCE_DATE = new Date(2025, 6, 1); // 1er juillet 2026

    // Trouver le lundi de la semaine contenant le 1er juillet 2026
    function getMondayOfWeek(date) {
        const d = new Date(date);
        const day = d.getDay();
        const diff = d.getDate() - day + (day === 0 ? -6 : 1); // Ajuster quand dimanche
        return new Date(d.setDate(diff));
    }

    const WEEK1_MONDAY = getMondayOfWeek(REFERENCE_DATE);

    function getWeekNumberForRange(date) {
        // Calculer le nombre de jours écoulés depuis le lundi de la semaine 1
        const timeDiff = date - WEEK1_MONDAY;
        const daysDiff = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
        const weekNumber = Math.floor(daysDiff / 7) + 1;
        
        // Vérifier que c'est dans la plage 1-53
        if (weekNumber < 1 || weekNumber > 53) return -1;
        return weekNumber;
    }

    function getWeekStartDate(weekNumber) {
        const startOfWeek = new Date(WEEK1_MONDAY);
        startOfWeek.setDate(WEEK1_MONDAY.getDate() + (weekNumber - 1) * 7);
        return startOfWeek;
    }

    function getWeekType(weekNumber) {
        // Semaine 1, 3, 5, 7... = A
        // Semaine 2, 4, 6, 8... = B
        return weekNumber % 2 === 1 ? 'A' : 'B';
    }

    function formatDateFR(date) {
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        return `${day}/${month}/${year}`;
    }

    function generateWeeks() {
        const container = document.getElementById('weeks-container');
        if (!container) return; // Si le conteneur n'existe pas, ne rien faire
        
        container.innerHTML = '';
        
        const today = new Date();
        const currentWeek = getWeekNumberForRange(today);
        
        // Générer 53 semaines
        for (let week = 1; week <= 53; week++) {
            const weekStartDate = getWeekStartDate(week);
            const weekType = getWeekType(week);
            
            const btn = document.createElement('button');
            const bgColor = weekType === 'A' ? 'bg-slate-200' : 'bg-slate-300';
            const activeBgColor = weekType === 'A' ? 'bg-blue-600' : 'bg-purple-600';
            
            btn.className = `flex flex-col items-center justify-center py-1 text-[10px] font-bold transition-all flex-1 ${
                week === currentWeek 
                    ? `${activeBgColor} text-white shadow-md` 
                    : `${bgColor} text-slate-700 hover:opacity-80`
            }`;
            btn.dataset.week = week;
            
            // Déterminer le mois (on prend le mois du lundi de la semaine)
            const monthNames = ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.'];
            const monthName = monthNames[weekStartDate.getMonth()];
            
            btn.innerHTML = `${week}<br>${monthName}`;
            
            btn.addEventListener('click', () => selectWeek(week));
            container.appendChild(btn);
        }
    }

    function selectWeek(week) {
        const container = document.getElementById('weeks-container');
        if (!container) return;
        
        // Mettre à jour le style des boutons
        document.querySelectorAll('#weeks-container button').forEach(btn => {
            const btnWeek = parseInt(btn.dataset.week);
            const btnType = getWeekType(btnWeek);
            const bgColor = btnType === 'A' ? 'bg-slate-200' : 'bg-slate-300';
            const activeBgColor = btnType === 'A' ? 'bg-blue-600' : 'bg-purple-600';
            
            if (btnWeek === week) {
                btn.className = `flex flex-col items-center justify-center py-1 text-[10px] font-bold transition-all flex-1 ${activeBgColor} text-white shadow-md`;
            } else {
                btn.className = `flex flex-col items-center justify-center py-1 text-[10px] font-bold transition-all flex-1 ${bgColor} text-slate-700 hover:opacity-80`;
            }
        });
        
        // Calculer la date du lundi de cette semaine
        const startOfWeek = getWeekStartDate(week);
        const endOfWeek = new Date(startOfWeek);
        endOfWeek.setDate(startOfWeek.getDate() + 6); // Dimanche
        
        // Mettre à jour l'affichage des dates
        const weekDatesSpan = document.getElementById('week-dates');
        if (weekDatesSpan) {
            weekDatesSpan.textContent = `du ${formatDateFR(startOfWeek)} au ${formatDateFR(endOfWeek)}`;
        }
        
        // Mettre à jour le type de semaine (A ou B)
        const weekTypeSpan = document.getElementById('week-type');
        const weekType = getWeekType(week);
        if (weekTypeSpan) {
            weekTypeSpan.textContent = `Semaine ${weekType}`;
            // Appliquer la couleur en fonction du type
            if (weekType === 'A') {
                weekTypeSpan.className = 'px-3 py-2 text-white bg-blue-600 font-bold';
            } else {
                weekTypeSpan.className = 'px-3 py-2 text-white bg-purple-600 font-bold';
            }
        }
        
        // Mettre à jour l'affichage des jours
        updateDaysDisplay(startOfWeek);

        // Exposer la semaine courante et charger les cours depuis l'API
        window.currentWeekStart = startOfWeek;
        loadCours(startOfWeek);

        // Émettre un événement personnalisé
        document.body.dispatchEvent(new CustomEvent('week-selected', { detail: { week, startDate: startOfWeek } }));
    }

    function updateDaysDisplay(startOfWeek) {
        const jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche'];
        const months = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'];
        const now = new Date();
        
        jours.forEach((jour, index) => {
            const container = document.querySelector(`[data-jour="${jour}"]`);
            if (container) {
                const dayDate = new Date(startOfWeek);
                dayDate.setDate(startOfWeek.getDate() + index);
                
                const dateSpan = container.querySelector('.jour-date');
                if (dateSpan) {
                    dateSpan.textContent = `${dayDate.getDate()} ${months[dayDate.getMonth()]}`;
                }
                
                // Vérifier si c'est aujourd'hui (même jour et même date)
                const isToday = dayDate.getDate() === now.getDate() && 
                               dayDate.getMonth() === now.getMonth() && 
                               dayDate.getFullYear() === now.getFullYear();
                
                const baseHeaderClass = "en-tete-jour py-1 flex flex-col items-center border-b border-slate-300/50 rounded-t-xl transition-colors flex-shrink-0";
                const hasCourses = true; // À adapter si besoin
                
                if (isToday) {
                    container.className = "jour-container flex-1 h-full bg-white shadow-md rounded-xl flex flex-col relative z-20 transition-all";
                    if (!container.querySelector('.today-border-overlay')) {
                        const overlay = document.createElement('div');
                        overlay.className = 'today-border-overlay absolute inset-0 rounded-xl pointer-events-none z-50';
                        overlay.style.boxShadow = 'inset 0 0 0 2px #818cf8';
                        container.appendChild(overlay);
                    }
                    container.querySelector('.en-tete-jour').className = `${baseHeaderClass} bg-indigo-100 border-indigo-200`;
                    container.querySelector('.jour-nom').className = "jour-nom text-[10px] font-bold text-indigo-800 uppercase";
                    container.querySelector('.jour-date').className = "jour-date text-[8px] text-indigo-600 font-medium";
                } else {
                    // Retirer l'overlay si présent
                    const overlay = container.querySelector('.today-border-overlay');
                    if (overlay) overlay.remove();
                    
                    let extraClass = (index === 5 && !hasCourses) ? "opacity-70 grayscale-[0.5]" : "";
                    container.className = `jour-container flex-1 h-full bg-white/60 shadow-sm rounded-xl flex flex-col hover:bg-white/80 transition-all z-20 ${extraClass}`;
                    container.querySelector('.en-tete-jour').className = `${baseHeaderClass} bg-slate-50/50`;
                    container.querySelector('.jour-nom').className = "jour-nom text-[10px] font-bold text-slate-600 uppercase";
                    container.querySelector('.jour-date').className = "jour-date text-[8px] text-slate-400";
                }
            }
        });
    }

    // Initialiser les semaines au chargement
    window.addEventListener('load', () => {
        generateWeeks();
        const today = new Date();
        const currentWeek = getWeekNumberForRange(today);
        if (currentWeek > 0 && currentWeek <= 53) {
            selectWeek(currentWeek);
        } else {
            // Si on est pas dans la plage, afficher la semaine 1
            selectWeek(1);
        }
    });
});