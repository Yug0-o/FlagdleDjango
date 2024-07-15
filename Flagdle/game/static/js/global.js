// Global variables for scroll and theme management
let lastScrollTop = 0;
const header = document.getElementById('header');
const moonIcon = document.querySelector('#moon-icon');
const sunIcon = document.querySelector('#sun-icon');
const body = document.body;

// Function to toggle the theme
function toggleTheme() {
    body.classList.toggle('dark-theme');
    body.classList.toggle('light-theme');

    const isDarkTheme = body.classList.contains('dark-theme');
    moonIcon.classList.toggle('shown', isDarkTheme);
    moonIcon.classList.toggle('hidden', !isDarkTheme);
    sunIcon.classList.toggle('shown', !isDarkTheme);
    sunIcon.classList.toggle('hidden', isDarkTheme);

    localStorage.setItem('theme', isDarkTheme ? 'dark-theme' : 'light-theme');
}

// Event listeners for theme icons
moonIcon.addEventListener('click', toggleTheme);
sunIcon.addEventListener('click', toggleTheme);

// Scroll event to hide the header
window.addEventListener('scroll', function () {
    let scrollTop = document.documentElement.scrollTop;
    if (scrollTop > lastScrollTop && scrollTop > 50) {
        header.classList.add('header-hide');
    } else if (scrollTop < lastScrollTop) {
        header.classList.remove('header-hide');
    }
    lastScrollTop = scrollTop;
});

// Function to reset the score, only called if it's not country_game.html or flag_game.html
function resetScore() {
    if (!window.location.pathname.includes('country_game', 'flag_game')) {
        $.ajax({
            type: 'POST',
            url: "/reset_current_score",
            data: {
                'category': '{{ selected_category }}',
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            async: false,
            success: function(response) {
                if (response === 'success'){
                    console.log('Score reset successfully');
                }
            },
            error: function(xhr, status, error) {
                console.log('Error resetting score: ' + error);
            }
        });
    }
}

// Initial page load
window.onload = function () {
    // Theme management
    const storedTheme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark-theme' : 'light-theme');
    body.classList.add(storedTheme);
    localStorage.setItem('theme', storedTheme);

    const isDarkTheme = storedTheme === 'dark-theme';
    moonIcon.classList.toggle('shown', isDarkTheme);
    moonIcon.classList.toggle('hidden', !isDarkTheme);
    sunIcon.classList.toggle('shown', !isDarkTheme);
    sunIcon.classList.toggle('hidden', isDarkTheme);

    // Initial animation for certain elements
    document.querySelectorAll('body > *:not(footer):not(script):not(header)').forEach(element => element.classList.add('animate'));

    // Reset score (conditional call)
    resetScore();
};
