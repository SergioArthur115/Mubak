/**
 * produto-carrossel.js
 * Carrossel de imagens da página de detalhe do produto.
 * Permite navegar entre as imagens com as setas, pelos indicadores (dots)
 * ou clicando nas miniaturas.
 */
(function () {
    let slideAtual = 0;

    function totalSlides() {
        const trilho = document.getElementById('produto-trilho');
        return trilho ? trilho.children.length : 0;
    }

    function atualizarCarrossel() {
        const trilho = document.getElementById('produto-trilho');
        if (!trilho) return;

        const total = totalSlides();
        if (total === 0) return;

        // Mantém o índice sempre dentro do intervalo válido (efeito "loop").
        slideAtual = ((slideAtual % total) + total) % total;
        trilho.style.transform = `translateX(-${slideAtual * 100}%)`;

        document.querySelectorAll('.carrossel_dot').forEach(function (dot, i) {
            dot.classList.toggle('ativo', i === slideAtual);
        });
        document.querySelectorAll('.produto_miniaturas .miniatura').forEach(function (min, i) {
            min.classList.toggle('ativa', i === slideAtual);
        });
    }

    window.mudarSlideProduto = function (delta) {
        slideAtual += delta;
        atualizarCarrossel();
    };

    window.irParaSlideProduto = function (indice) {
        slideAtual = indice;
        atualizarCarrossel();
    };

    document.addEventListener('DOMContentLoaded', atualizarCarrossel);

    document.addEventListener('keydown', function (e) {
        if (!document.getElementById('produto-carrossel')) return;
        if (e.key === 'ArrowLeft') window.mudarSlideProduto(-1);
        if (e.key === 'ArrowRight') window.mudarSlideProduto(1);
    });
})();
