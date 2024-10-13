let selectedFace = null;

document.getElementById('signUp').addEventListener('click', (e) => {
    e.preventDefault();
    var email = document.getElementById('email').value;
    var password = document.getElementById('password').value;
    const profilePictureInput = document.getElementById('profilePicture');
    const file = profilePictureInput.files[0];

    if (!file) {
        alert('Please select a profile picture.');
        return;
    }

    const formData = new FormData();
    formData.append('profilePicture', file);
    formData.append('email', email);
    formData.append('password', password);

    // Upload profile picture and receive base64 faces
    fetch('/upload_profile', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayFaces(data.faces); // Display the faces for the user to choose from
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred during registration.');
    });
});

// Function to display detected faces from base64 strings
function displayFaces(faces) {
    const faceSelectionDiv = document.getElementById('faceSelection');
    const facesContainer = document.getElementById('facesContainer');
    facesContainer.innerHTML = ''; // Clear any previous faces
    faceSelectionDiv.style.display = 'block'; // Show face selection section

    faces.forEach((faceBase64, index) => {
        const img = document.createElement('img');
        img.src = `data:image/png;base64,${faceBase64}`;
        img.width = 100;
        img.height = 100;
        img.style.cursor = 'pointer';
        img.onclick = () => {
            document.getElementById('confirmFace').style.display = 'block';
            document.querySelectorAll('img').forEach(el => el.style.border = '');
            img.style.border = '3px solid green'; // Highlight selected face
            selectedFace = faceBase64;
        };
        facesContainer.appendChild(img);
    });

    document.getElementById('confirmFace').addEventListener('click', () => {
        const confirmButton = document.getElementById('confirmFace'); // Reference to the button

        if (selectedFace) {
            alert("Face selected!");

            // Disable the button to prevent multiple submissions
            confirmButton.disabled = true;

            fetch('/finalize_registration', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image: selectedFace // Send the base64 string
                })
            })
            .then(response => response.json()) // Parse the JSON response
            .then(data => {
                if (data.success) {
                    alert("Registration successful!"); // Alert on success
                } else {
                    alert("Registration failed. Please try again."); // Alert on failure
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert("An error occurred during registration.");
            })                
        }
    });
}
