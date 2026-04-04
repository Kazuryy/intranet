// Cache la page le temps de verifier la session
document.documentElement.style.visibility = 'hidden';

(async () => {
    try {
        const res = await fetch('/auth/me');
        if (!res.ok) {
            window.location.replace('/login.html');
        } else {
            const user = await res.json();
            window.__currentUser = user;
            document.documentElement.style.visibility = 'visible';
            document.dispatchEvent(new CustomEvent('auth-ready', { detail: user }));
        }
    } catch {
        window.location.replace('/login.html');
    }
})();
