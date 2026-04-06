document.addEventListener("DOMContentLoaded", () => {
  // секция с трейлером фильма
  const section = document.querySelector("#movieInfo");
  // заголовок страницы
  const header = document.querySelector("header");
  // все кнопки навигации в заголовке
  const links = document.querySelectorAll(".a-text");
  // кнопки на заголовке
  const burgerBtn = document.querySelector("#burgerBtn");
  const glassesBtn = document.querySelector("#glassesBtn");

  // проверка нахождения секции с трейлером на экране пользователя
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
              header.classList.remove("header-fixed");
              header.classList.add("header-opacity");

              burgerBtn.classList.remove("burger-btn-black");
              burgerBtn.classList.add("burger-btn");

              glassesBtn.classList.remove("icon-black");
              glassesBtn.classList.add("icon");

              links.forEach(link => {
                  link.classList.remove("a-text-black");
                  link.classList.add("a-text");
                });
          }
      });
  }, {
      threshold: 0,
      rootMargin: "-100px 0px 0px 0px",
  });

  observer.observe(section);

  // элемент для проигрыша трейлера на фоне
  const video = document.getElementById("trailer-video");
  // кнопка открытия трейлера на полный экран
  const fsBtn = document.getElementById("fullscreen-btn");

  // загружаем HLS-источник из data-src
  const hlsSrc = video.dataset.src;
  if (Hls.isSupported()) {
    const hls = new Hls();
    hls.loadSource(hlsSrc);
    hls.attachMedia(video);
  } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
    video.src = hlsSrc;
  }

  // автозапуск трейлера без звука
  video.play().catch(() => {});

  // после первого проигрыша трейлера накидываем на него блюр
  video.addEventListener("ended", () => {
    video.classList.add("blurred");
  });

  // обработка открытия трейлера в полный экран
  if (fsBtn) {
    fsBtn.addEventListener("click", () => {
      video.classList.remove("blurred");
      video.currentTime = 0;
      video.muted = false;
      video.play();

      if (video.requestFullscreen) video.requestFullscreen();
      else if (video.webkitRequestFullscreen) video.webkitRequestFullscreen();
      else if (video.msRequestFullscreen) video.msRequestFullscreen();
    });
  }

  // после выхода из режима полного экрана накидываем на трейлер блюр
  document.addEventListener("fullscreenchange", () => {
    if (!document.fullscreenElement) {
      video.muted = true;
      video.classList.add("blurred");
    }
  });
});
