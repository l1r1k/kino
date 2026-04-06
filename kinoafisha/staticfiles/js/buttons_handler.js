(() => {
  const viewport = document.getElementById('weekViewport');
  const track = document.getElementById('weekContainer');
  const prevBtn = document.getElementById('weekPrev');
  const nextBtn = document.getElementById('weekNext');

  // Если уже инициализировано — выходим (защита от дублей)
  if (!viewport || viewport.dataset.initialized === '1') return;
  viewport.dataset.initialized = '1';

  // Шаг прокрутки: ширина первой карточки + gap (надёжнее, чем "магическое число")
  function getScrollStep() {
    const first = track.querySelector('.day-item');
    if (!first) return viewport.clientWidth * 0.8;
    const itemW = Math.ceil(first.getBoundingClientRect().width);
    // Пытаемся вытащить gap из вычисленных стилей
    const gap = parseInt(getComputedStyle(track).columnGap || getComputedStyle(track).gap || '0', 10) || 0;
    return itemW + gap;
  }

  function updateButtons() {
    const fits = viewport.scrollWidth <= viewport.clientWidth + 1; // +1 на всякий случай
    if (fits) {
      prevBtn.classList.add('d-none');
      nextBtn.classList.add('d-none');
      return;
    }
    // По умолчанию показываем обе
    prevBtn.classList.remove('d-none');
    nextBtn.classList.remove('d-none');

    // Крайние положения
    if (viewport.scrollLeft <= 0) prevBtn.classList.add('d-none');
    const atRight = viewport.scrollLeft + viewport.clientWidth >= viewport.scrollWidth - 1;
    if (atRight) nextBtn.classList.add('d-none');
  }

  function scrollByStep(dir = 1) {
    viewport.scrollBy({ left: getScrollStep() * dir, behavior: 'smooth' });
  }

  prevBtn.addEventListener('click', () => scrollByStep(-1));
  nextBtn.addEventListener('click', () => scrollByStep(1));

  viewport.addEventListener('scroll', updateButtons);
  window.addEventListener('resize', () => {
    // при сильном ресайзе вернёмся к началу, чтобы кнопки обновились корректно
    viewport.scrollLeft = 0;
    updateButtons();
  });

  // Старт
  updateButtons();
})();
