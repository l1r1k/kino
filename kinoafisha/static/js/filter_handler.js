// реализация открытия фильтрации фильмов в полный экран на мобильных устройствах
const filterAside = document.getElementById('filterAside');
const filterToggleBtn = document.getElementById('filterToggleBtn');
const filterCloseBtn = document.getElementById('filterCloseBtn');

filterToggleBtn.addEventListener('click', () => {
  filterAside.classList.add('active');
  document.body.style.overflow = 'hidden';
});

filterCloseBtn.addEventListener('click', () => {
  filterAside.classList.remove('active');
  filterAside.classList.add('closing');
  setTimeout(() => {
    filterAside.classList.remove('closing');
    document.body.style.overflow = '';
  }, 300);
});

document.addEventListener('click', (e) => {
  if (
    filterAside.classList.contains('active') &&
    !filterAside.contains(e.target) &&
    e.target !== filterToggleBtn
  ) {
    filterCloseBtn.click();
  }
});

const filterInputs = document.querySelectorAll('#filterForm input[type=checkbox]');
function checkFilters() {
  let hasFilters = false;
  filterInputs.forEach(input => {
    if (input.checked) hasFilters = true;
  });
  if (hasFilters) {
    filterToggleBtn.classList.add('active-filters');
  } else {
    filterToggleBtn.classList.remove('active-filters');
  }
}
checkFilters();
filterInputs.forEach(input => input.addEventListener('change', checkFilters));
