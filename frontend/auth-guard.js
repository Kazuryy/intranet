// Cache la page le temps de verifier la session
document.documentElement.style.visibility = 'hidden';

(async () => {
    try {
        const res = await fetch('/auth/me');
        if (!res.ok) {
            window.location.replace('/login.html');
        } else {
            document.documentElement.style.visibility = 'visible';
        }
    } catch {
        window.location.replace('/login.html');
    }
})();
