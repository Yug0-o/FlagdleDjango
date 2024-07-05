let lastScrollTop = 0;
const header = document.getElementById('header');

window.addEventListener('scroll', function () {
    let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    if (scrollTop > lastScrollTop && scrollTop > 50) {
        header.classList.add('header-hide');
    } else if (scrollTop < lastScrollTop) {
        header.classList.remove('header-hide');
    }
    lastScrollTop = scrollTop;
});

const themeSwitcher = document.getElementById('theme-switcher');
const moonIcon = document.querySelector('#moon-icon');
const sunIcon = document.querySelector('#sun-icon');
const body = document.body;

themeSwitcher.addEventListener('click', () => {
    if (body.classList.contains('dark-theme')) {
        body.classList.remove('dark-theme');
        body.classList.add('light-theme');
        moonIcon.classList.remove('shown');
        moonIcon.classList.add('hidden');
        sunIcon.classList.remove('hidden');
        sunIcon.classList.add('shown');
    } else {
        body.classList.remove('light-theme');
        body.classList.add('dark-theme');
        moonIcon.classList.remove('hidden');
        moonIcon.classList.add('shown');
        sunIcon.classList.remove('shown');
        sunIcon.classList.add('hidden');
    }
});

window.onload = function () {
    const elements = document.querySelectorAll('body > *:not(footer):not(script):not(header)');
    elements.forEach(element => element.classList.add('animate'));
};