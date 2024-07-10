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

const moonIcon = document.querySelector('#moon-icon');
const sunIcon = document.querySelector('#sun-icon');
const body = document.body;

// Function to toggle theme
function toggleTheme() {
    // Toggle theme classes on the body
    body.classList.toggle('dark-theme');
    body.classList.toggle('light-theme');

    // Determine if dark theme is active after toggle
    const isDarkTheme = body.classList.contains('dark-theme');

    // Toggle icon visibility based on theme
    moonIcon.classList.toggle('shown', isDarkTheme);
    moonIcon.classList.toggle('hidden', !isDarkTheme);
    sunIcon.classList.toggle('shown', !isDarkTheme);
    sunIcon.classList.toggle('hidden', isDarkTheme);

    // Store the current theme in local storage
    localStorage.setItem('theme', isDarkTheme ? 'dark-theme' : 'light-theme');
}

// Add event listeners to icons
moonIcon.addEventListener('click', toggleTheme);
sunIcon.addEventListener('click', toggleTheme);

window.onload = function () {
    const storedTheme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark-theme' : 'light-theme');
    body.classList.add(storedTheme);
    localStorage.setItem('theme', storedTheme); // Ensure theme is stored if it was based on system preference

    // Simplify icon visibility toggle
    const isDarkTheme = storedTheme === 'dark-theme';
    moonIcon.classList.toggle('shown', isDarkTheme);
    moonIcon.classList.toggle('hidden', !isDarkTheme);
    sunIcon.classList.toggle('shown', !isDarkTheme);
    sunIcon.classList.toggle('hidden', isDarkTheme);

    // Apply initial animation to certain elements
    document.querySelectorAll('body > *:not(footer):not(script):not(header)').forEach(element => element.classList.add('animate'));
};