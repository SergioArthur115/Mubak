/**
 * menu-ativo.js
 * Marca automaticamente o link do menu correspondente
 * à página atual com a classe "ativo".
 */
(function () {
    const links = document.querySelectorAll('.menu_principal a');
    const paginaAtual = window.location.pathname;

    links.forEach(function (link) {
        const href = link.getAttribute('href');

        // Verifica se o href bate com o final da URL atual
        if (href && paginaAtual.endsWith(href.replace('../', '').replace('./', ''))) {
            link.classList.add('ativo');
        }

        // Caso especial: "Início" ativo quando estiver em index.html ou na raiz
        if (
            (href === '#' || href === '../index.html' || href === './index.html') &&
            (paginaAtual.endsWith('index.html') || paginaAtual.endsWith('/'))
        ) {
            link.classList.add('ativo');
        }
    });
})();
