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

async function loadCours(startDate, classeId) {
    const debut = new Date(startDate);
    debut.setHours(0, 0, 0, 0);
    const fin = new Date(startDate);
    fin.setDate(fin.getDate() + 6);
    fin.setHours(23, 59, 59, 999);
    try {
        const params = new URLSearchParams({ debut: debut.toISOString(), fin: fin.toISOString() });
        if (classeId) params.set('classe_id', classeId);
        const res = await fetch('/edt/cours?' + params.toString());
        if (!res.ok) return;
        const data = await res.json();
        MOCK_COURS.splice(0, MOCK_COURS.length, ...data.map(apiToMock));
        renderCours();
    } catch (e) {
        console.error('Erreur chargement EDT:', e);
    }
}

// ─── DONNÉES EDT (remplies depuis l'API) ────────────────────────
const MOCK_COURS = [];

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

        container.innerHTML = '';

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

    let currentNotes = [];

    function formatDateFR(isoDate) {
        if (!isoDate) return '';
        const [y, m, d] = isoDate.split('-');
        return `${d}/${m}/${y}`;
    }

    function transformDevoirs(apiDevoirs) {
        const TYPES_RENDU = ['expose', 'projet', 'soutenance'];
        const ds = apiDevoirs.filter(d => d.type === 'controle');
        const devoirs = apiDevoirs.filter(d => d.type !== 'controle');

        const grouped = {};
        devoirs.forEach(d => {
            const date = formatDateFR(d.date_limite);
            if (!grouped[date]) grouped[date] = { date, items: [] };
            grouped[date].items.push({
                matiere: d.matiere,
                description: d.consigne || '',
                type: TYPES_RENDU.includes(d.type) ? 'avec_rendu' : 'sans_rendu',
            });
        });

        return {
            ds: ds.map(d => ({
                matiere: d.matiere,
                date: formatDateFR(d.date_limite),
                salle: '',
                duree: '',
                programme: d.consigne || '',
            })),
            devoirs: Object.values(grouped),
        };
    }

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

        currentNotes.slice(0, 5).forEach((item, itemIndex) => {
            const noteMax = item.note_max ?? item.max;
            const dateStr = item.date_evaluation ?? item.date ?? '';
            const colorClass = getGradeColor(item.note, noteMax);
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
                <span class="text-[8px] opacity-70">/${noteMax}</span>
            `;

            const infoPart = document.createElement('div');
            infoPart.className = 'flex-1';
            infoPart.innerHTML = `
                <span class="text-[11px] font-bold text-slate-700">${item.matiere}</span><br>
                <span class="text-[9px] text-slate-400 font-medium">${dateStr}</span>
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
                        <span class="text-[8px] opacity-70">/${item.note_max ?? item.max}</span>
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
            const item = currentNotes[noteIndex];
            const colorClass = score.getAttribute('data-color-class');
            const noteMax = item.note_max ?? item.max;

            if (notesVisible) {
                // Afficher toutes les notes
                score.className = `w-10 h-10 rounded-lg border ${colorClass} flex flex-col items-center justify-center shadow-sm notes-score cursor-pointer`;
                score.innerHTML = `
                    <span class="text-xs font-bold note-value">${item.note}</span>
                    <span class="text-[8px] opacity-70">/${noteMax}</span>
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

    // Ajouter l'écouteur au bouton œil
    const eyeButton = document.getElementById('notes-eye-btn');
    if (eyeButton) {
        eyeButton.addEventListener('click', toggleNotesVisibility);
    }

    // ════════════════════════════════════════════════════════════════
    // ║              GESTION DES DEVOIRS ET DS                        ║
    // ════════════════════════════════════════════════════════════════

    function renderTravail(travail) {
        const container = document.getElementById('travail-list');
        if (!container) return;

        // Afficher les DS
        if (travail.ds.length > 0) {
            const dsTitle = document.createElement('div');
            dsTitle.className = 'text-[11px] font-bold text-indigo-900 mb-3 uppercase';
            dsTitle.textContent = 'Prochains DS';
            container.appendChild(dsTitle);

            travail.ds.forEach(ds => {
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
        travail.devoirs.forEach(dateGroup => {
            // Afficher le titre une seule fois avant le premier groupe de devoirs
            if (travail.devoirs.indexOf(dateGroup) === 0) {
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

    (async () => {
        const onTravailPage = !!document.querySelector('[data-page="travail"]');
        const userType = window.__currentUser?.type;

        if (onTravailPage) {
            await initTravailPage();
        } else if (userType === 'élève' || userType === 'parent') {
            try {
                const res = await fetch('/api/notes');
                currentNotes = res.ok ? await res.json() : [];
            } catch (e) {
                currentNotes = [];
            }
            renderNotes();

            try {
                const res = await fetch('/api/devoirs/');
                const devoirs = res.ok ? await res.json() : [];
                renderTravail(transformDevoirs(devoirs));
            } catch (e) {
                renderTravail({ ds: [], devoirs: [] });
            }

            renderCours();
        } else {
            renderCours();
        }
    })();

    // ════════════════════════════════════════════════════════════════
    // ║              PAGE TRAVAIL — LOGIQUE DÉDIÉE                   ║
    // ════════════════════════════════════════════════════════════════

    let allDevoirs = [];
    let activeCategory = 'tous';
    let showAllDates = false;

    async function initTravailPage() {
        let user = null;
        try {
            const res = await fetch('/auth/me');
            if (res.ok) user = await res.json();
        } catch (e) {}

        if (user && user.type === 'employé') {
            const addBtn = document.getElementById('add-travail-btn');
            if (addBtn) addBtn.classList.remove('hidden');
            await loadModalSelects();
            setupAddTravailModal();
        }

        await loadTravailData();
        setupTravailFilters();
    }

    async function loadTravailData() {
        const container = document.getElementById('travail-list');
        if (!container) return;
        container.innerHTML = '<div class="text-center text-slate-400 text-xs py-4">Chargement...</div>';

        try {
            const url = showAllDates ? '/api/devoirs/' : '/api/devoirs/tri/a_venir';
            const res = await fetch(url);
            allDevoirs = res.ok ? await res.json() : [];
        } catch (e) {
            allDevoirs = [];
        }
        renderTravailPage();
    }

    function renderTravailPage() {
        const container = document.getElementById('travail-list');
        const evalsSection = document.getElementById('evals-section');
        if (!container) return;

        const TYPES_RENDU = ['expose', 'projet', 'soutenance'];

        let filtered = allDevoirs;
        if (activeCategory === 'evaluation') {
            filtered = allDevoirs.filter(d => d.type === 'controle');
        } else if (activeCategory === 'rendu') {
            filtered = allDevoirs.filter(d => TYPES_RENDU.includes(d.type));
        } else if (activeCategory === 'exercice') {
            filtered = allDevoirs.filter(d => d.type === 'exercice' || d.type === 'autre');
        }

        const devoirs = filtered.filter(d => d.type !== 'controle');
        const evals = allDevoirs.filter(d => d.type === 'controle');

        // Colonne milieu : devoirs
        container.innerHTML = '';
        if (devoirs.length === 0) {
            container.innerHTML = '<div class="text-center text-slate-400 text-xs py-4">Aucun devoir à faire</div>';
        } else {
            const grouped = {};
            devoirs.forEach(d => {
                const date = formatDateFR(d.date_limite);
                if (!grouped[date]) grouped[date] = [];
                grouped[date].push(d);
            });

            Object.entries(grouped).forEach(([date, items]) => {
                const dateObj = new Date(date.split('/').reverse().join('-'));
                const jours = ['Dimanche', 'Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'];
                const mois = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'];

                const header = document.createElement('div');
                header.className = 'bg-indigo-100 text-indigo-900 text-xs font-bold p-2 rounded flex items-center justify-between cursor-pointer hover:bg-indigo-200 transition-colors';
                header.innerHTML = `<span>Pour le ${jours[dateObj.getDay()]} ${dateObj.getDate()} ${mois[dateObj.getMonth()]}</span><i class="fas fa-chevron-down text-xs"></i>`;
                container.appendChild(header);

                const body = document.createElement('div');
                body.className = 'flex flex-col gap-1';
                items.forEach(d => {
                    const item = document.createElement('div');
                    item.className = 'flex items-center justify-between gap-2 pl-3 py-1 border-l-2 border-indigo-300';
                    const rendu = TYPES_RENDU.includes(d.type);
                    item.innerHTML = `
                        <div class="flex-1">
                            <div class="text-sm font-bold text-slate-800">• ${d.matiere}</div>
                            <div class="text-xs text-slate-600">${d.consigne || ''}</div>
                        </div>
                        ${rendu
                            ? `<span class="bg-indigo-200 text-indigo-900 text-xs font-bold px-2 py-1 rounded">Rendu</span>`
                            : `<input type="checkbox" class="w-4 h-4 cursor-pointer" title="Marquer comme fait">`
                        }
                    `;
                    body.appendChild(item);
                });
                container.appendChild(body);

                header.addEventListener('click', () => {
                    const hidden = body.style.display === 'none';
                    body.style.display = hidden ? 'flex' : 'none';
                    header.querySelector('i').style.transform = hidden ? 'rotate(180deg)' : '';
                });
            });
        }

        // Colonne droite : évaluations
        if (evalsSection) {
            evalsSection.innerHTML = '';
            if (evals.length === 0) {
                evalsSection.innerHTML = '<div class="text-center text-slate-400 text-xs py-4">Aucune évaluation</div>';
            } else {
                evals.forEach(d => {
                    const item = document.createElement('div');
                    item.className = 'bg-violet-100 border-l-4 border-violet-500 p-2 rounded';
                    item.innerHTML = `
                        <div class="text-sm font-bold text-violet-800">${d.matiere}</div>
                        <div class="text-xs text-violet-600">${formatDateFR(d.date_limite)}</div>
                        ${d.consigne ? `<div class="text-xs text-slate-600 mt-1">${d.consigne}</div>` : ''}
                    `;
                    evalsSection.appendChild(item);
                });
            }
        }
    }

    function setupTravailFilters() {
        const aFaireBtn = document.getElementById('filter-a-faire-btn');
        const toutBtn = document.getElementById('filter-tout-btn');
        const catBtns = {
            'tous': document.getElementById('cat-tous-btn'),
            'evaluation': document.getElementById('cat-evaluation-btn'),
            'rendu': document.getElementById('cat-rendu-btn'),
            'exercice': document.getElementById('cat-exercice-btn'),
        };

        if (aFaireBtn) aFaireBtn.addEventListener('click', async () => {
            showAllDates = false;
            aFaireBtn.className = 'px-4 py-1.5 text-xs font-semibold text-white bg-indigo-600 rounded transition-colors';
            if (toutBtn) toutBtn.className = 'px-4 py-1.5 text-xs font-semibold text-slate-700 bg-slate-200 hover:bg-slate-300 rounded transition-colors';
            await loadTravailData();
        });

        if (toutBtn) toutBtn.addEventListener('click', async () => {
            showAllDates = true;
            toutBtn.className = 'px-4 py-1.5 text-xs font-semibold text-white bg-indigo-600 rounded transition-colors';
            if (aFaireBtn) aFaireBtn.className = 'px-4 py-1.5 text-xs font-semibold text-slate-700 bg-slate-200 hover:bg-slate-300 rounded transition-colors';
            await loadTravailData();
        });

        Object.entries(catBtns).forEach(([cat, btn]) => {
            if (!btn) return;
            btn.addEventListener('click', () => {
                activeCategory = cat;
                Object.values(catBtns).forEach(b => {
                    if (!b) return;
                    b.className = 'px-3 py-2 text-xs font-semibold text-indigo-900 hover:bg-indigo-50 rounded transition-colors text-left';
                });
                btn.className = 'px-3 py-2 text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 rounded transition-colors text-left';
                renderTravailPage();
            });
        });
    }

    async function loadModalSelects() {
        try {
            const res = await fetch('/api/notes/classes');
            if (!res.ok) return;
            const data = await res.json();

            const classeSelect = document.getElementById('devoir-classe');
            const matiereSelect = document.getElementById('devoir-matiere');
            if (!classeSelect || !matiereSelect) return;

            const combinaisons = data.combinaisons || [];
            const toutesLesMatieres = data.matieres || [];

            data.classes.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.id;
                opt.textContent = c.nom;
                classeSelect.appendChild(opt);
            });

            function filtrerMatieres() {
                matiereSelect.innerHTML = '<option value="">-- Sélectionner une matière --</option>';
                const idClasse = parseInt(classeSelect.value);
                if (!idClasse) return;
                const idsAutorises = combinaisons
                    .filter(c => c.id_classe === idClasse)
                    .map(c => c.id_matiere);
                toutesLesMatieres
                    .filter(m => idsAutorises.includes(m.id))
                    .forEach(m => {
                        const opt = document.createElement('option');
                        opt.value = m.id;
                        opt.textContent = m.nom;
                        matiereSelect.appendChild(opt);
                    });
            }

            classeSelect.addEventListener('change', filtrerMatieres);
        } catch (e) {}
    }

    function setupAddTravailModal() {
        const addBtn = document.getElementById('add-travail-btn');
        const closeBtn = document.getElementById('close-modal-btn');
        const createBtn = document.getElementById('create-devoir-btn');
        const modal = document.getElementById('add-travail-modal');

        if (addBtn) addBtn.addEventListener('click', () => modal && modal.classList.remove('hidden'));
        if (closeBtn) closeBtn.addEventListener('click', () => modal && modal.classList.add('hidden'));
        if (modal) modal.addEventListener('click', e => { if (e.target === modal) modal.classList.add('hidden'); });
        if (createBtn) createBtn.addEventListener('click', createDevoir);
    }

    async function createDevoir() {
        const classeId = document.getElementById('devoir-classe')?.value;
        const matiereId = document.getElementById('devoir-matiere')?.value;
        const type = document.getElementById('devoir-type')?.value;
        const consigne = document.getElementById('devoir-consigne')?.value;
        const dateLimite = document.getElementById('devoir-date-limite')?.value;
        const errorDiv = document.getElementById('modal-error');

        if (!classeId || !matiereId || !consigne || !dateLimite) {
            if (errorDiv) {
                errorDiv.textContent = 'Tous les champs sont requis.';
                errorDiv.classList.remove('hidden');
            }
            return;
        }
        if (errorDiv) errorDiv.classList.add('hidden');

        try {
            const res = await fetch('/api/devoirs/creer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    id_classe: parseInt(classeId),
                    id_matiere: parseInt(matiereId),
                    type: type,
                    consigne: consigne,
                    date_limite: dateLimite,
                }),
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.error || 'Erreur serveur');
            }

            document.getElementById('add-travail-modal')?.classList.add('hidden');
            document.getElementById('devoir-consigne').value = '';
            document.getElementById('devoir-date-limite').value = '';
            await loadTravailData();
        } catch (err) {
            if (errorDiv) {
                errorDiv.textContent = err.message;
                errorDiv.classList.remove('hidden');
            }
        }
    }

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
                    if (resultatMenu) resultatMenu.classList.add('hidden');
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

    function formatDateObjFR(date) {
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
            weekDatesSpan.textContent = `du ${formatDateObjFR(startOfWeek)} au ${formatDateObjFR(endOfWeek)}`;
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
        const classeSelect = document.getElementById('edt-classe-select');
        loadCours(startOfWeek, classeSelect ? classeSelect.value || null : null);

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

    // Sélecteur de classe pour admin/direction sur la page EDT
    async function initEdtClasseSelect() {
        const select = document.getElementById('edt-classe-select');
        if (!select) return;

        try {
            const res = await fetch('/edt/classes');
            if (!res.ok) return;
            const classes = await res.json();
            classes.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.id;
                opt.textContent = c.label;
                select.appendChild(opt);
            });
            select.classList.remove('hidden');

            const title = document.getElementById('edt-page-title');
            if (title) title.textContent = 'Emploi du temps';

            select.addEventListener('change', () => {
                if (window.currentWeekStart) {
                    loadCours(window.currentWeekStart, select.value || null);
                }
            });
        } catch (e) {
            // Non admin/direction : le sélecteur reste caché
        }
    }

    // Initialiser les semaines au chargement
    window.addEventListener('load', async () => {
        generateWeeks();
        const today = new Date();
        const currentWeek = getWeekNumberForRange(today);
        await initEdtClasseSelect();
        if (currentWeek > 0 && currentWeek <= 53) {
            selectWeek(currentWeek);
        } else {
            selectWeek(1);
        }
    });
});