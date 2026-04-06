// ════════════════════════════════════════════════════════════════
// ║          GESTION CENTRALISÉE DU HEADER & NAVIGATION           ║
// ════════════════════════════════════════════════════════════════

(function(){
    // Le code HTML du header est directement intégré ici pour éviter 
    // les problèmes de chargement (CORS) en local.
    const headerHTML = `
    <div class="h-[10vh] flex flex-col shadow-md z-50 relative">
        <div class="h-[9vh] bg-white flex items-center justify-center">
            <h1 class="m-0 text-3xl text-indigo-900 font-bold">PRONOTE V2 TEST</h1>
        </div>
        <div class="h-[6vh] bg-indigo-900 flex items-center justify-between">
            <nav class="flex items-center" role="tablist" aria-label="Onglets principaux">
                
                <button role="tab" data-tab="accueil" data-href="index.html" aria-selected="true"
                    class="tab-btn px-3 py-3 text-sm font-bold text-white border-b-4 border-indigo-900 hover:transition hover:bg-white hover:text-indigo-900 hover:border-b-4 hover:border-red-500">
                    Accueil
                </button>
                
                <button role="tab" data-tab="edt" data-href="edt.html" aria-selected="false"
                    class="tab-btn px-3 py-3 text-sm font-bold text-white border-b-4 border-indigo-900 hover:transition hover:bg-white hover:text-indigo-900 hover:border-b-4 hover:border-red-500">
                    Emploi du temps
                </button>

                <div class="relative">
                    <button id="resultats-btn" role="tab" data-tab="resultats" data-href="resultats.html" aria-selected="false" aria-expanded="false"
                        class="tab-btn px-3 py-3 text-sm font-bold text-white border-b-4 border-indigo-900 hover:transition hover:bg-white hover:text-indigo-900 hover:border-b-4 hover:border-red-500">
                        Résultats
                    </button>
                    <div id="resultats-menu" class="hidden absolute top-full left-0 w-[200%] bg-white shadow-lg rounded-b-lg py-2 z-50">
                        <div class="px-0 py-2 border-b border-slate-200">
                            <button data-href="notes.html" class="menu-link block w-full px-4 py-2 text-sm font-semibold text-indigo-900 border-l-4 border-transparent hover:border-red-500 hover:bg-indigo-50 transition-colors text-left">Mes notes</button>
                            <button data-href="releve.html" class="menu-link block w-full px-4 py-2 text-sm font-semibold text-indigo-900 border-l-4 border-transparent hover:border-red-500 hover:bg-indigo-50 transition-colors text-left">Mon relevé</button>
                        </div>
                        <div class="px-0 py-2">
                            <button data-href="bulletin.html" class="menu-link block w-full px-4 py-2 text-sm font-semibold text-indigo-900 border-l-4 border-transparent hover:border-red-500 hover:bg-indigo-50 transition-colors text-left">Mon Bulletin</button>
                        </div>
                    </div>
                </div>
                
                <div class="relative">
                    <button id="cahier-textes-btn" role="tab" data-tab="cahier-textes" data-href="travail.html" aria-selected="false" aria-expanded="false"
                        class="tab-btn px-3 py-3 text-sm font-bold text-white border-b-4 border-indigo-900 hover:transition hover:bg-white hover:text-indigo-900 hover:border-b-4 hover:border-red-500">
                        Cahier de textes
                    </button>
                    <div id="cahier-textes-menu" class="hidden absolute top-full left-0 w-[200%] bg-white shadow-lg rounded-b-lg py-2 z-50">
                        <div class="px-0 py-2">
                            <button data-href="contenu.html" class="menu-link block w-full px-4 py-2 text-sm font-semibold text-indigo-900 border-l-4 border-transparent hover:border-red-500 hover:bg-indigo-50 transition-colors text-left">Contenus & Ressources</button>
                            <button data-href="travail.html" class="menu-link block w-full px-4 py-2 text-sm font-semibold text-indigo-900 border-l-4 border-transparent hover:border-red-500 hover:bg-indigo-50 transition-colors text-left">Travail à faire</button>
                        </div>
                    </div>
                </div>
                
                <button role="tab" data-tab="cartne-correspondance" data-href="assiduity.html" aria-selected="false"
                    class="tab-btn px-3 py-3 text-sm font-bold text-white border-b-4 border-indigo-900 hover:transition hover:bg-white hover:text-indigo-900 hover:border-b-4 hover:border-red-500">
                    Carnet de correspondance
                </button>
                
                <button role="tab" data-tab="communication" data-href="communication.html" aria-selected="false"
                    class="tab-btn px-3 py-3 text-sm font-bold text-white border-b-4 border-indigo-900 hover:transition hover:bg-white hover:text-indigo-900 hover:border-b-4 hover:border-red-500">
                    Communication
                </button>
            </nav>
        </div>
    </div>`;

    let activePage = null;
    let hoverTimeout = null;

    function detectCurrentPage() {
        const currentFile = window.location.pathname.split('/').pop() || 'index.html';
        const pageMap = {
            'index.html': 'accueil',
            'edt.html': 'edt',
            'edt-semaine.html': 'edt',
            'edt-jour.html': 'edt',
            'edt-mois.html': 'edt',
            'resultats.html': 'resultats',
            'notes.html': 'resultats',
            'mes-notes.html': 'resultats',
            'releve.html': 'resultats',
            'bulletin.html': 'resultats',
            'travail.html': 'cahier-textes',
            'travail-donne.html': 'cahier-textes',
            'travail-effectue.html': 'cahier-textes',
            'ressources.html': 'cahier-textes',
            'assiduity.html': 'cartne-correspondance',
            'communication.html': 'communication'
        };
        return pageMap[currentFile] || 'accueil';
    }

    function initializeHeader() {
        const tabs = Array.from(document.querySelectorAll('.tab-btn'));
        const resultatBtn = document.getElementById('resultats-btn');
        const resultatMenu = document.getElementById('resultats-menu');
        const cahierBtn = document.getElementById('cahier-textes-btn');
        const cahierMenu = document.getElementById('cahier-textes-menu');

        activePage = detectCurrentPage();

        function activateTab(btn, isPermanent = false) {
            tabs.forEach(t => {
                if (t.dataset.tab !== activePage) {
                    t.classList.remove('bg-white','text-indigo-900','shadow-sm', 'border-red-500');
                    t.classList.add('text-white');
                    t.setAttribute('aria-selected','false');
                }
            });
            btn.classList.add('bg-white','text-indigo-900','shadow-sm','border-red-500');
            btn.classList.remove('text-white');
            btn.setAttribute('aria-selected','true');

            if (isPermanent) activePage = btn.dataset.tab;
        }

        // Configuration générique pour les menus déroulants
        function setupDropdownMenu(btn, menu) {
            if (!btn || !menu) return;
            
            btn.addEventListener('mouseenter', () => {
                clearTimeout(hoverTimeout);
                // Cacher tous les autres menus (il ne reste plus que Résultats et Cahier de textes)
                [resultatMenu, cahierMenu].forEach(m => {
                    if(m && m !== menu) m.classList.add('hidden');
                });
                menu.classList.remove('hidden');
                btn.setAttribute('aria-expanded','true');
                activateTab(btn, false);
            });
            
            btn.addEventListener('mouseleave', () => {
                clearTimeout(hoverTimeout);
                hoverTimeout = setTimeout(() => {
                    if (!menu.matches(':hover')) {
                        menu.classList.add('hidden');
                        btn.setAttribute('aria-expanded','false');
                        const activeBtn = document.querySelector(`[data-tab="${activePage}"]`);
                        if (activeBtn) activateTab(activeBtn, false);
                    }
                }, 150);
            });
            
            btn.addEventListener('click', (e) => {
                e.preventDefault(); e.stopPropagation();
            });

            menu.addEventListener('mouseenter', () => clearTimeout(hoverTimeout));
            menu.addEventListener('mouseleave', () => {
                clearTimeout(hoverTimeout);
                hoverTimeout = setTimeout(() => {
                    menu.classList.add('hidden');
                    btn.setAttribute('aria-expanded','false');
                    const activeBtn = document.querySelector(`[data-tab="${activePage}"]`);
                    if (activeBtn) activateTab(activeBtn, false);
                }, 150);
            });
            
            menu.querySelectorAll('.menu-link').forEach(link => {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    if (link.dataset.href) window.location.href = link.dataset.href;
                });
            });
        }

        setupDropdownMenu(resultatBtn, resultatMenu);
        setupDropdownMenu(cahierBtn, cahierMenu);

        // Tabs simples sans menu (Accueil, Emploi du temps, Carnet, Communication)
        tabs.forEach(t => {
            if (!['resultats-btn', 'cahier-textes-btn'].includes(t.id)) {
                t.addEventListener('mouseenter', () => {
                    [resultatMenu, cahierMenu].forEach(m => { if(m) m.classList.add('hidden') });
                    if (t.dataset.tab !== activePage) activateTab(t, false);
                });
                
                t.addEventListener('mouseleave', () => {
                    clearTimeout(hoverTimeout);
                    hoverTimeout = setTimeout(() => {
                        const activeBtn = document.querySelector(`[data-tab="${activePage}"]`);
                        if (activeBtn) activateTab(activeBtn, false);
                    }, 150);
                });
                
                t.addEventListener('click', () => {
                    if (t.dataset.href) window.location.href = t.dataset.href;
                });
            }
        });

        // Initialize with detected page
        const detectedBtn = document.querySelector(`[data-tab="${activePage}"]`);
        if (detectedBtn) activateTab(detectedBtn, true);
    }

    // Injection automatique au chargement
    document.addEventListener('DOMContentLoaded', () => {
        const temp = document.createElement('div');
        temp.innerHTML = headerHTML;
        document.body.insertBefore(temp.firstElementChild, document.body.firstChild);
        initializeHeader();
    });

})();