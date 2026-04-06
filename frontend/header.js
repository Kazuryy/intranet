// ════════════════════════════════════════════════════════════════
// ║          GESTION CENTRALISÉE DU HEADER & NAVIGATION           ║
// ════════════════════════════════════════════════════════════════

(function () {

    // ── Tabs par rôle ────────────────────────────────────────────
    const NAV_BY_ROLE = {
        'élève': [
            { tab: 'accueil',       href: '/',        label: 'Accueil' },
            { tab: 'edt',           href: '/edt',     label: 'Emploi du temps' },
            { tab: 'notes',         href: '/notes',   label: 'Notes' },
            { tab: 'cahier-textes', href: '/travail', label: 'Cahier de textes' },
        ],
        'parent': [
            { tab: 'accueil',       href: '/',        label: 'Accueil' },
            { tab: 'edt',           href: '/edt',     label: 'Emploi du temps' },
            { tab: 'notes',         href: '/notes',   label: 'Notes' },
            { tab: 'cahier-textes', href: '/travail', label: 'Cahier de textes' },
        ],
        'employé': [
            { tab: 'edt',           href: '/edt',     label: 'Emploi du temps' },
            { tab: 'notes',         href: '/notes',   label: 'Notes' },
            { tab: 'cahier-textes', href: '/travail', label: 'Cahier de textes' },
        ],
        'administrateur': [
            { tab: 'edt',           href: '/edt',     label: 'Emploi du temps' },
            { tab: 'admin',         href: '/admin',   label: 'Administration' },
        ],
    };

    const TAB_BASE     = 'px-3 py-3 text-sm font-bold border-b-4 transition-colors';
    const TAB_INACTIVE = 'text-white border-transparent hover:bg-white hover:text-indigo-900 hover:border-red-500';
    const TAB_ACTIVE   = 'bg-white text-indigo-900 border-red-500';

    // ── Détection de la page active ──────────────────────────────
    function detectCurrentPage() {
        const path = window.location.pathname;
        const file = path.split('/').pop() || '';
        if (path === '/' || path === '/index' || file === 'index.html') return 'accueil';
        if (path === '/edt'     || file === 'edt.html')     return 'edt';
        if (path === '/notes'   || file === 'notes.html')   return 'notes';
        if (path === '/travail' || file === 'travail.html') return 'cahier-textes';
        if (path === '/admin'   || file === 'admin.html')   return 'admin';
        return 'accueil';
    }

    // ── Injection du header shell (immédiate, sans attendre auth) ─
    function injectShell() {
        const wrapper = document.createElement('div');
        wrapper.id = 'main-header';
        wrapper.className = 'h-[10vh] flex flex-col shadow-md z-50 relative';
        wrapper.innerHTML = `
            <div class="h-[9vh] bg-white flex items-center justify-center">
                <h1 class="m-0 text-3xl text-indigo-900 font-bold">PRONOTE V2 TEST</h1>
            </div>
            <div id="header-bar" class="h-[6vh] bg-indigo-900 flex items-center justify-between">
                <nav id="main-nav" class="flex items-center h-full"></nav>
            </div>`;

        if (document.body) {
            document.body.insertBefore(wrapper, document.body.firstChild);
        } else {
            document.addEventListener('DOMContentLoaded', () => {
                document.body.insertBefore(wrapper, document.body.firstChild);
            });
        }
    }

    // ── Remplissage du nav une fois le rôle connu ────────────────
    function fillNav(user) {
        const nav = document.getElementById('main-nav');
        if (!nav) return;

        const tabs = NAV_BY_ROLE[user.type] || NAV_BY_ROLE['élève'];
        const activePage = detectCurrentPage();

        tabs.forEach(({ tab, href, label }) => {
            const btn = document.createElement('button');
            btn.className = `${TAB_BASE} ${tab === activePage ? TAB_ACTIVE : TAB_INACTIVE}`;
            btn.dataset.tab = tab;
            btn.textContent = label;
            btn.addEventListener('click', () => { window.location.href = href; });
            nav.appendChild(btn);
        });
    }

    // ── Init ─────────────────────────────────────────────────────
    injectShell();

    if (window.__currentUser) {
        fillNav(window.__currentUser);
    } else {
        document.addEventListener('auth-ready', (e) => fillNav(e.detail), { once: true });
    }

})();
