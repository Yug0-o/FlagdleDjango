document.getElementById('loginForm').addEventListener('submit', async function(event) {
    event.preventDefault();

    let username = document.getElementById('username').value;
    let password = document.getElementById('password').value;

    let response = await fetch('/Flagdle/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username: username, password: password }),
    });

    let data = await response.json();

    if (response.ok) {
        localStorage.setItem('access', data.access);
        localStorage.setItem('refresh', data.refresh);
        document.getElementById('message').innerText = "Login successful!";
        // Redirect or load a new page after successful login
        window.location.href = '/Flagdle';
    } else {
        document.getElementById('message').innerText = "Login failed: " + data.detail;
    }
});
