/**
 * carrosel.js
 * Carrossel com scroll infinito automático.
 * - Calcula a largura ANTES de duplicar os cards.
 * - Para ao hover no container; retoma ao sair.
 */
function iniciarCarrosel(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const faixa = container.querySelector('.carrosel_faixa');
    if (!faixa) return;

    // Calcula a largura ANTES de duplicar
    const larguraOriginal = faixa.scrollWidth;

    // Duplica os cards para o loop infinito
    faixa.innerHTML += faixa.innerHTML;

    const velocidade = 0.8; // px por frame — aumente para mais rápido
    let posicao = 0;
    let pausado = false;

    function animar() {
        if (!pausado) {
            posicao += velocidade;

            // Quando percorreu a largura original, volta ao início sem pulo visível
            if (posicao >= larguraOriginal) {
                posicao = 0;
            }

            faixa.style.transform = `translateX(-${posicao}px)`;
        }
        requestAnimationFrame(animar);
    }

    // Pausa ao entrar no container, retoma ao sair
    container.addEventListener('mouseenter', () => { pausado = true; });
    container.addEventListener('mouseleave', () => { pausado = false; });

    requestAnimationFrame(animar);
}

iniciarCarrosel('carrosel-promocoes');
iniciarCarrosel('carrosel-vistos');
