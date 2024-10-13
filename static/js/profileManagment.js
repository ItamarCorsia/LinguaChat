document.getElementById('updateProfile').addEventListener('click', (e) => {
    e.preventDefault();  // Prevent the default form submission

    // Redirect to faceDet.html without reloading the page
    window.history.pushState({}, '', '/faceDet.html');

    var userIndex = document.querySelector('.user-info').textContent.split(' ')[0];
    var email = document.getElementById('email').value.trim();
    var password = document.getElementById('password').value.trim();
    const profilePictureInput = document.getElementById('profilePicture');
    const file = profilePictureInput.files[0];

    // Prepare form data to send to server
    const formData = new FormData();
    if (email) {
        formData.append('email', email);
    }
    if (password) {
        formData.append('password', password);
    }
    if (file) {
        formData.append('profilePicture', file);
    }
    formData.append('userIndex', userIndex);

    // Send the form data to the server using fetch API
    fetch('/update_profile', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.text(); // Get HTML response
    })
    .then(html => {
        // Replace the current page content with the response HTML
        document.documentElement.innerHTML = html;
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
