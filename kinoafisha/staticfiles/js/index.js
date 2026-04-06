document.addEventListener("DOMContentLoaded", () => {
    // секция с выводом промо страниц фильмов
    const section = document.querySelector("#promoBlock");
    // заголовок страницы
    const header = document.querySelector("header");
    // кнопки навигации по сайту
    const links = document.querySelectorAll(".a-text");
    // кнопки на заголовке
    const burgerBtn = document.querySelector("#burgerBtn");
    const glassesBtn = document.querySelector("#glassesBtn");
    
    // наблюдатель за расположением секции с промо фильмов на экране пользователя
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (!entry.isIntersecting) {
                // секция с трейлером ушла за экран - меняем стили с прозрачным фоном и белыми кнопками
                // на белый фон заголовка и черные кнопки
                header.classList.remove("header-opacity");
                header.classList.add("header-fixed");

                burgerBtn.classList.remove("burger-btn");
                burgerBtn.classList.add("burger-btn-black");

                glassesBtn.classList.remove("icon");
                glassesBtn.classList.add("icon-black");

                links.forEach(link => {
                  link.classList.remove("a-text");
                  link.classList.add("a-text-black");
                });
            } else {
                // секция с трейлером вновь видна на экране - меняем все обратно под прозрачный стиль
                // заголовка
                header.classList.add("header-opacity");
                header.classList.remove("header-fixed");

                burgerBtn.classList.add("burger-btn");
                burgerBtn.classList.remove("burger-btn-black");

                glassesBtn.classList.add("icon");
                glassesBtn.classList.remove("icon-black");

                links.forEach(link => {
                  link.classList.remove("a-text-black");
                  link.classList.add("a-text");
                });
            }
        });
    }, {
        threshold: 0, // срабатывает, когда section хоть чуть-чуть виден
        rootMargin: "-100px 0px 0px 0px",
    });

    observer.observe(section);
});


// настройки таймингов
const POSTER_DELAY_MS = 5000;   // 5 сек постер перед стартом трейлера фильма
const OVERLAY_DELAY_MS = 5000;  // 5 сек информация о фильме поверх трейлера

// DOM
const slidesContainer = document.querySelector('.slides');
const slides = Array.from(document.querySelectorAll('.slide'));
const prevBtn = document.querySelector('.prev');
const nextBtn = document.querySelector('.next');
const indicatorsContainer = document.querySelector('.indicators');

// служебные переменные
let currentIndex = 0;
let posterTimer = null;
let overlayTimer = null;

// состояние звука трейлеров
const slideSoundState = slides.map(() => false); // false = muted, true = sound on

// индикаторы слайдов промо
const dots = slides.map((_, i) => {
  const dot = document.createElement('div');
  if (i === 0) dot.classList.add('active');
  dot.addEventListener('click', () => goToSlide(i));
  indicatorsContainer.appendChild(dot);
  return dot;
});

// утилиты для получения элементов связанных с промо фильмов
function getPosterEl(slide) { return slide.querySelector('.poster') || slide.querySelector('img'); }
function getVideo(slide) { return slide.querySelector('video'); }
function getOverlay(slide) { return slide.querySelector('.text-overlay'); }
function getInfoCard(slide) { return slide.querySelector('.redirect-card'); }
function getMuteBtn(slide) { return slide.querySelector('.mute-btn') || slide.querySelector('.sound-toggle'); }
function getFsBtn(slide) { return slide.querySelector('.fullscreen-btn') || slide.querySelector('.fullscreen-toggle'); }

function clearTimers() {
  if (posterTimer) { clearTimeout(posterTimer); posterTimer = null; }
  if (overlayTimer) { clearTimeout(overlayTimer); overlayTimer = null; }
}

function updateDots() {
  dots.forEach((d, i) => d.classList.toggle('active', i === currentIndex));
}

function resetOverlayAnimation(overlay) {
  overlay.style.opacity = '0';
  overlay.style.animation = 'none';
  overlay.offsetHeight; // force reflow
  overlay.style.animation = '';
  overlay.style.removeProperty('animation');
}

// функции для работы с выводом изображения через HLS-сегментацию
function destroyHls(video) {
  if (!video) return;
  if (video.hlsInstance) {
    try { video.hlsInstance.destroy(); } catch (_) {}
    video.hlsInstance = null;
  }
  try {
    video.pause();
    video.removeAttribute('src');
    video.load();
  } catch (_) {}
}

function attachHls(video) {
  const src = video.dataset.src;
  if (!src) return;

  const index = slides.indexOf(video.closest('.slide'));
  video.muted = !slideSoundState[index];
  video.playsInline = true;

  destroyHls(video);

  if (window.Hls && Hls.isSupported()) {
    const hls = new Hls({
      maxBufferLength: 10,
      maxMaxBufferLength: 30,
      liveSyncDuration: 3,
      lowLatencyMode: true
    });
    video.hlsInstance = hls;
    hls.loadSource(src);
    hls.attachMedia(video);
    hls.on(Hls.Events.MANIFEST_PARSED, () => playVideo(video));
    hls.on(Hls.Events.ERROR, (evt, data) => {
      if (data && data.fatal) {
        switch (data.type) {
          case Hls.ErrorTypes.NETWORK_ERROR: hls.startLoad(); break;
          case Hls.ErrorTypes.MEDIA_ERROR: hls.recoverMediaError(); break;
          default: hls.destroy(); attachHls(video); break;
        }
      }
    });
  } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
    video.src = src;
    video.addEventListener('loadedmetadata', () => playVideo(video), { once: true });
  } else {
    console.warn('HLS не поддерживается и нативного HLS нет.');
  }
}

function playVideo(video) {
  const p = video.play();
  if (p && typeof p.then === 'function') { p.catch(() => {}); }
}

// подготовка слайдов промо к фильмам
function prepareSlide(slide, index) {
  const poster = getPosterEl(slide);
  const video  = getVideo(slide);
  const overlay = getOverlay(slide);
  const card   = getInfoCard(slide);

  clearTimers();
  destroyHls(video);

  // сброс состояний
  poster.style.opacity = '1';
  video.style.opacity = '0';
  video.currentTime = 0;

  overlay.style.opacity = '1';
  overlay.style.pointerEvents = 'auto';
  resetOverlayAnimation(overlay);
  overlay.style.animation = 'fadeInUp 1s forwards';

  if(card) card.classList.remove('active');

  // установка звука
  video.muted = !slideSoundState[index];

  // постер, через 5 секунд запуск трейлера
  posterTimer = setTimeout(() => {
    poster.style.opacity = '0';
    attachHls(video);
    video.style.opacity = '1';

    // информацию о фильме держим 5 секунд, потом одновременно скрываем и показываем лого фильма с кнопкой
    // перехода на страницу фильма
    overlayTimer = setTimeout(() => {
      if(card) card.classList.add('active');

      if(overlay){
        overlay.style.opacity = '0';
        overlay.style.animation = 'none';
        overlay.style.pointerEvents = 'none';
      }

    }, OVERLAY_DELAY_MS);

  }, POSTER_DELAY_MS);

  // кнопка переключения режима звука
  const muteBtn = getMuteBtn(slide);
  if(muteBtn && video){
    muteBtn.textContent = video.muted ? '🔇' : '🔊';
    muteBtn.onclick = () => {
      video.muted = !video.muted;
      slideSoundState[index] = !video.muted;
      muteBtn.textContent = video.muted ? '🔇' : '🔊';
    };
  }

  // кнопка переключения режима отображения фильма (фоновый трейлер / полноэкранный режим)
  const fsBtn = getFsBtn(slide);
  if(fsBtn && video){
    fsBtn.onclick = () => {
      if (video.requestFullscreen) video.requestFullscreen();
      else if (video.webkitRequestFullscreen) video.webkitRequestFullscreen();
      else if (video.msRequestFullscreen) video.msRequestFullscreen();
    };
  }

  // автопереход на следующий слайд после окончания трейлера
  if(video) video.addEventListener('ended', nextSlide, { once: true });
}

// сброс неактивного слайда
function resetInactiveSlide(slide, index){
  clearTimers();
  const video = getVideo(slide);
  const overlay = getOverlay(slide);
  const card = getInfoCard(slide);
  const poster = getPosterEl(slide);

  destroyHls(video);
  video.style.opacity = '0';
  video.currentTime = 0;
  video.muted = !slideSoundState[index];

  poster.style.opacity = '1';
  overlay.style.opacity = '0';
  overlay.style.animation = 'none';
  overlay.style.pointerEvents = 'none';
  if(card) card.classList.remove('active');
}

// переключение слайдов
function goToSlide(index){
  if(index<0) index = slides.length-1;
  if(index>=slides.length) index=0;

  slides.forEach((s,i)=>{ if(i!==index) resetInactiveSlide(s,i); });

  currentIndex = index;
  slidesContainer.style.transform = `translateX(-${index*100}%)`;
  updateDots();

  prepareSlide(slides[index], index);
}
function nextSlide(){ goToSlide(currentIndex+1); }
function prevSlide(){ goToSlide(currentIndex-1); }

// кнопки для смены слайдов
if(nextBtn) nextBtn.addEventListener('click', nextSlide);
if(prevBtn) prevBtn.addEventListener('click', prevSlide);

// запуск первого слайда
window.addEventListener('load', () => goToSlide(0));
