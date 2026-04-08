function escName(str) {
    return String(str || '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
}

function initUserMenu(user) {
    const ROLE_LABELS = {
        'administrateur': { label: 'Admin',   cls: 'bg-purple-500' },
        'employé':        { label: 'Employe', cls: 'bg-blue-500'   },
        'élève':          { label: 'Eleve',   cls: 'bg-green-500'  },
        'parent':         { label: 'Parent',  cls: 'bg-orange-500' },
    };
    const role = ROLE_LABELS[user.type] || { label: user.type, cls: 'bg-slate-500' };

    const bar = document.querySelector('.bg-indigo-900.flex.items-center.justify-between');
    if (!bar) return;

    const menu = document.createElement('div');
    menu.className = 'relative flex items-center mr-3';
    menu.innerHTML = `
        <button id="user-menu-btn"
            class="flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-white/10 transition text-white text-xs font-semibold">
            <span class="w-6 h-6 rounded-full bg-white/20 flex items-center justify-center text-[10px] font-bold uppercase">
                ${(user.prenom?.[0] || '') + (user.nom?.[0] || '')}
            </span>
            <span class="hidden sm:inline">${escName(user.prenom)} ${escName(user.nom)}</span>
            <i class="fa-solid fa-chevron-down text-[9px] opacity-70"></i>
        </button>

        <div id="user-dropdown"
            class="hidden absolute right-0 top-full mt-1 w-52 bg-white rounded-xl shadow-xl border border-slate-100 z-50 py-1 overflow-hidden">

            <div class="px-4 py-2.5 border-b border-slate-100">
                <p class="text-xs font-bold text-slate-800">${escName(user.prenom)} ${escName(user.nom)}</p>
                <p class="text-[10px] text-slate-500 mt-0.5">${escName(user.mail_interne || '')}</p>
                <span class="inline-block mt-1 px-2 py-0.5 rounded-full text-[10px] font-semibold text-white ${role.cls}">
                    ${role.label}
                </span>
            </div>

            ${user.type === 'administrateur' ? `
            <a href="/admin"
                class="flex items-center gap-2 px-4 py-2 text-xs font-semibold text-indigo-900 hover:bg-indigo-50 transition">
                <i class="fa-solid fa-users-gear w-3.5 text-center text-indigo-400"></i>
                Administration
            </a>` : ''}

            <div class="border-t border-slate-100 mt-1"></div>

            <button id="btn-logout"
                class="w-full flex items-center gap-2 px-4 py-2 text-xs font-semibold text-red-600 hover:bg-red-50 transition">
                <i class="fa-solid fa-right-from-bracket w-3.5 text-center"></i>
                Deconnexion
            </button>
        </div>
    `;

    bar.appendChild(menu);

    const btn = document.getElementById('user-menu-btn');
    const dropdown = document.getElementById('user-dropdown');

    btn.addEventListener('click', (e) => {
        e.stopPropagation();
        dropdown.classList.toggle('hidden');
    });

    document.addEventListener('click', () => dropdown.classList.add('hidden'));
    dropdown.addEventListener('click', (e) => e.stopPropagation());

    document.getElementById('btn-logout').addEventListener('click', async () => {
        await fetch('/auth/logout', { method: 'POST' });
        window.location.replace('/login');
    });

    // Marquer le lien admin actif sur /admin
    if (window.location.pathname === '/admin' && user.type === 'administrateur') {
        const adminLink = menu.querySelector('a[href="/admin"]');
        if (adminLink) adminLink.classList.add('bg-indigo-50');
    }

    // Navigation nav-btn (admin n'inclut pas script.js)
    document.querySelectorAll('.nav-btn[data-href]').forEach(b => {
        b.addEventListener('click', () => { window.location.href = b.dataset.href; });
    });

    // Désactiver les liens vers des pages non implémentées
    const DISPONIBLES = new Set(['/', '/edt', '/notes', '/travail', '/admin', '/login', '/setup-password']);
    document.querySelectorAll('[data-href]').forEach(el => {
        const href = el.dataset.href;
        if (!href || DISPONIBLES.has(href)) return;
        el.removeAttribute('data-href');
        el.style.opacity = '0.45';
        el.style.cursor = 'not-allowed';
        el.title = 'Bientot disponible';
        el.addEventListener('click', e => e.stopImmediatePropagation());
    });
}

// Resilient : fonctionne que l'event ait déjà été dispatché ou pas encore
if (window.__currentUser) {
    initUserMenu(window.__currentUser);
} else {
    document.addEventListener('auth-ready', (e) => initUserMenu(e.detail));
}
