/**
 * carrosel.js — Carrossel infinito automático.
 */
function iniciarCarrosel(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const faixa = container.querySelector('.carrosel_faixa');
    if (!faixa) return;

    const larguraOriginal = faixa.scrollWidth;
    faixa.innerHTML += faixa.innerHTML;

    const velocidade = 0.8;
    let posicao = 0;
    let pausado = false;

    function animar() {
        if (!pausado) {
            posicao += velocidade;
            if (posicao >= larguraOriginal) posicao = 0;
            faixa.style.transform = `translateX(-${posicao}px)`;
        }
        requestAnimationFrame(animar);
    }

    container.addEventListener('mouseenter', () => { pausado = true; });
    container.addEventListener('mouseleave', () => { pausado = false; });

    requestAnimationFrame(animar);
}

iniciarCarrosel('carrosel-promocoes');
iniciarCarrosel('carrosel-vistos');
