document.addEventListener("DOMContentLoaded", () => {
    // секция с промо роликомами к фильмам
    const sectionPromo = document.querySelector("#promoBlock");
    // секция с подробной информацией о фильме с фоновым трейлером
    const sectionMovieInfo = document.querySelector("#movieInfo");
    // секция киноафиши
    const kinoafisha = document.querySelector("#kinoafishaSection");
    // заголовок страницы
    const header = document.querySelector("header");
    // кнопки навигации по сайту
    const links = document.querySelectorAll(".a-text");
    // кнопка смены режима отображения текста
    const glassesBtn = document.querySelector("#glassesBtn");
    // смена работы кнопок навигации, если находимся не на главной страницы сайта
    if (!kinoafisha){
        document.querySelectorAll('a[href^="#"]').forEach(link => {
            const indexOfId = link.href.indexOf("#") - 1;
            const hrefLen = link.href.length;
            link.href = link.href.slice(indexOfId - hrefLen);
        });
    }
    // установка стилей для заголовка в зависимости от типа страницы
    if (!sectionPromo && !sectionMovieInfo){
        // если мы находимся не на главной и не на странице с подробной информацией о фильме, то
        // ставим непрозрачный стиль заголовка
        header.classList.add("header");
        header.classList.add("mb-3");

        burgerBtn.classList.add("burger-btn-black");
        glassesBtn.classList.remove("icon");
        glassesBtn.classList.add("icon-black");

        links.forEach(link => {
            link.classList.remove("a-text");
            link.classList.add("a-text-black");
        });
    }
    else{
        // если находимся на главной или на странице с подробной информацией о фильме, то
        // ставим прозрачный стиль заголовка
        header.classList.add("header-opacity")

        burgerBtn.classList.add("burger-btn");
        glassesBtn.classList.remove("icon-black");
        glassesBtn.classList.add("icon");

        links.forEach(link => {
            link.classList.remove("a-text-black");
            link.classList.add("a-text");
        });
    }
    // делаем плавный скролл до нужной секции
    if (window.location.hash) {
        setTimeout(() => {
            const target = document.querySelector(window.location.hash);
            const header = document.querySelector('header');

            if (target && header) {
                const headerHeight = header.offsetHeight;
                window.scrollTo({
                    top: target.offsetTop - headerHeight,
                    behavior: 'smooth'
                });
            }
        }, 50);
    }
});
// кнопка открытия бокового меню
const burgerBtn = document.querySelector('#burgerBtn');
// боковое меню
const mobileWrapper = document.querySelector('.mobile-menu-wrapper');
// кнопка закрытия бокового меню
const closeBtn = document.querySelector('.close-btn');
// оверлей, чтобы боковое меню можно было закрывать нажав по пустому месту
const mobileMenuOverlay = document.querySelector('.mobile-menu-overlay');
// функция открытия бокового меню
function openMenu() {
  mobileWrapper.classList.add('active');
}
// функция закрытия бокового меню
function closeMenu() {
  mobileWrapper.classList.remove('active');
}
// добавление обработчиков для открытия и закрытия бокового меню
burgerBtn.addEventListener('click', openMenu);

closeBtn.addEventListener('click', closeMenu);

mobileMenuOverlay.addEventListener('click', closeMenu);
// реализация добавления оверлея на яндекс карту
const overlay = document.querySelector('.map-overlay');
const mapContainer = document.querySelector('.map-container');

function isTouchDevice() {
    return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
}

overlay.addEventListener('click', () => {
    overlay.style.display = 'none';
});

mapContainer.addEventListener('mouseleave', () => {
    overlay.style.display = 'block';
});

if (isTouchDevice()) {
    let overlayActive = true;
    let restoreTimeout;

    overlay.addEventListener('touchstart', function (e) {
        e.stopPropagation();
        overlay.style.display = 'none';
        overlayActive = false;
    });

    mapContainer.addEventListener('touchstart', () => {
        if (!overlayActive && restoreTimeout) {
            clearTimeout(restoreTimeout);
        }
    });

    mapContainer.addEventListener('touchend', () => {
        restoreTimeout = setTimeout(() => {
            overlay.style.display = 'block';
            overlayActive = true;
        }, 1500);
    });

    document.addEventListener('touchstart', function (e) {
        if (!mapContainer.contains(e.target) && !overlayActive) {
            overlay.style.display = 'block';
            overlayActive = true;
            if (restoreTimeout) clearTimeout(restoreTimeout);
        }
    });
}

document.querySelectorAll('a[href^="#"]').forEach(link => {
  link.addEventListener('click', function(e) {
    e.preventDefault();

    const sectionId = this.getAttribute('href').replace("/", "");

    if (document.querySelector(sectionId)){
        const target = document.querySelector(sectionId);
        const headerHeight = document.querySelector('header').offsetHeight;

        window.scrollTo({
            top: target.offsetTop - headerHeight,
            behavior: 'smooth'
        });
    } else {
        window.location.href = this.getAttribute('href');
    }

  });
});

const chooseSession = document.getElementById('chooseSession');

if (chooseSession){
    chooseSession.addEventListener('click', function(e) {
        e.preventDefault();

        const sectionId = '#movieSessions';

        const target = document.querySelector(sectionId);
        const headerHeight = document.querySelector('header').offsetHeight;

        window.scrollTo({
            top: target.offsetTop - headerHeight,
            behavior: 'smooth'
        });
    });
}
