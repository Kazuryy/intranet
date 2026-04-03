// Verifie si l'utilisateur est connecte, sinon redirige vers login.html
(async () => {
    try {
        const res = await fetch('/auth/me');
        if (!res.ok) {
            window.location.replace('/login.html');
        }
    } catch {
        window.location.replace('/login.html');
    }
})();
