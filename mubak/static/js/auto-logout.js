/**
 * auto-logout.js
 * Desloga automaticamente o usuário após 5 minutos sem interação
 * (mouse, teclado, toque ou scroll).
 */
(function () {
    const TEMPO_LIMITE_MS = 5 * 60 * 1000; // 5 minutos
    let timer;

    function deslogar() {
        window.location.href = '/logout';
    }

    function resetarTimer() {
        clearTimeout(timer);
        timer = setTimeout(deslogar, TEMPO_LIMITE_MS);
    }

    ['mousemove', 'mousedown', 'keydown', 'scroll', 'touchstart'].forEach(function (evt) {
        document.addEventListener(evt, resetarTimer, { passive: true });
    });

    resetarTimer();
})();
