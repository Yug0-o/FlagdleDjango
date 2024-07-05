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
    // Store the current theme in local storage
    localStorage.setItem('theme', body.classList.contains('dark-theme') ? 'dark-theme' : 'light-theme');
});

window.onload = function () {
    const storedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    if (storedTheme) {
        body.classList.add(storedTheme);
        if (storedTheme === 'dark-theme') {
            moonIcon.classList.remove('hidden');
            moonIcon.classList.add('shown');
            sunIcon.classList.remove('shown');
            sunIcon.classList.add('hidden');
        } else {
            moonIcon.classList.remove('shown');
            moonIcon.classList.add('hidden');
            sunIcon.classList.remove('hidden');
            sunIcon.classList.add('shown');
        }
    } else if (prefersDark) {
        body.classList.add('dark-theme');
        moonIcon.classList.remove('hidden');
        moonIcon.classList.add('shown');
        sunIcon.classList.remove('shown');
        sunIcon.classList.add('hidden');
        localStorage.setItem('theme', 'dark-theme');
    } else {
        body.classList.add('light-theme');
        moonIcon.classList.remove('shown');
        moonIcon.classList.add('hidden');
        sunIcon.classList.remove('hidden');
        sunIcon.classList.add('shown');
        localStorage.setItem('theme', 'light-theme');
    }

    const elements = document.querySelectorAll('body > *:not(footer):not(script):not(header)');
    elements.forEach(element => element.classList.add('animate'));
};