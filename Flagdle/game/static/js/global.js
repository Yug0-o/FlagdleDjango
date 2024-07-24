// Global variables for scroll and theme management
let lastScrollTop = 0;
const header = document.getElementById('header');
const body = document.body;

let intervalId
 
// Function to toggle the theme
function toggleTheme() {
    body.classList.toggle('dark-mode');
    body.classList.toggle('light-mode');

    const isDarkTheme = body.classList.contains('dark-mode');
    const moonIcon = document.querySelector('#moon-icon');
    const sunIcon = document.querySelector('#sun-icon');
    moonIcon.classList.toggle('shown', isDarkTheme);
    moonIcon.classList.toggle('hidden', !isDarkTheme);
    sunIcon.classList.toggle('shown', !isDarkTheme);
    sunIcon.classList.toggle('hidden', isDarkTheme);

    localStorage.setItem('theme', isDarkTheme ? 'dark-mode' : 'light-mode');
}

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
    if (window.location.pathname.includes('homepage')) {
        $.ajax({
            type: 'POST',
            url: "/reset_current_score",
            data: {
                'category': '{{ selected_category }}',
                'csrfmiddlewaretoken': '{{ csrf_token }}'
            },
            async: false,
            success: function (response) {
                if (response === 'success') {
                    console.log('Score reset successfully');
                }
            },
            error: function (xhr, status, error) {
                console.log('Error resetting score: ' + error);
            }
        });
    }
}

// Function to add event listeners to theme icons
function addThemeEventListeners() {
    const moonIcon = document.querySelector('#moon-icon');
    const sunIcon = document.querySelector('#sun-icon');

    if (moonIcon && sunIcon) {
        console.log('Theme icons available');
        // Event listeners for theme icons
        moonIcon.addEventListener('click', toggleTheme);
        sunIcon.addEventListener('click', toggleTheme);

        // Theme management
        const storedTheme = localStorage.getItem('theme') || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark-mode' : 'light-mode') || "light-mode";
        localStorage.setItem('theme', storedTheme);

        const isDarkTheme = storedTheme === 'dark-mode';
        moonIcon.classList.toggle('shown', isDarkTheme);
        moonIcon.classList.toggle('hidden', !isDarkTheme);
        sunIcon.classList.toggle('shown', !isDarkTheme);
        sunIcon.classList.toggle('hidden', isDarkTheme);
        body.classList.toggle('dark-mode', isDarkTheme);
        body.classList.toggle('light-mode', !isDarkTheme);

        // Clear the interval once the event listeners are added
        clearInterval(intervalId);
    }
}

// Initial page load
window.onload = function () {
    // Polling mechanism to add event listeners once elements are available
    intervalId = setInterval(addThemeEventListeners, 100);

    // Initial animation for certain elements
    document.querySelectorAll('body > *:not(footer):not(script):not(header)').forEach(element => element.classList.add('animate'));

    // Reset score (conditional call)
    resetScore();

    // $('img').mousedown(function (e) {
    //     if (e.button == 2) { // right click
    //         return false; // do nothing!
    //     }
    // });
};