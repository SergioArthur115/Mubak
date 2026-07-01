/**
 * menu-ativo.js
 * Marca o link do menu correspondente à página atual com a classe "ativo".
 */
(function () {
    const links = document.querySelectorAll('.menu_principal a');
    const paginaAtual = window.location.pathname;

    links.forEach(function (link) {
        const href = link.getAttribute('href');
        if (href && paginaAtual.endsWith(href.replace('../', '').replace('./', ''))) {
            link.classList.add('ativo');
        }
        if (
            (href === '#' || href === '../index.html' || href === './index.html') &&
            (paginaAtual.endsWith('index.html') || paginaAtual.endsWith('/'))
        ) {
            link.classList.add('ativo');
        }
    });
})();
