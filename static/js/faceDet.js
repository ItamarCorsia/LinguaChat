function checkUserSignIn(id, message, event) {
    if (id == 0) {
        event.preventDefault(); // Prevent the form from submitting
        alert(message);
    }
    // If the ID is not 0, the form will be submitted as usual.
}

document.getElementById('findRoomBtn1').addEventListener('click', function(event) {
    checkUserSignIn("{{ id1 }}", "Please sign in as the first user before finding a room.", event);
});

document.getElementById('findRoomBtn2').addEventListener('click', function(event) {
    checkUserSignIn("{{ id2 }}", "Please sign in as the second user before finding a room.", event);
});

document.getElementById('btnProfileManagementAsFirst').addEventListener('click', function(event) {
    checkUserSignIn("{{ id1 }}", "Please sign in as the first user before managing the profile.", event);
});

document.getElementById('btnProfileManagementAsSecond').addEventListener('click', function(event) {
    checkUserSignIn("{{ id2 }}", "Please sign in as the second user before managing the profile.", event);
});

// Socket.IO connection setup
var socket = io();

socket.on('connect', function() {
    console.log('Connected to server');
});

socket.on('updateUser', function(data) {
    console.log('Received updatePlayer event with data:', data);
    if (data.userIndex == 1) {
        // Update the first user card with the correct data
        document.querySelector('.user-card:nth-of-type(1) .user-id').innerText = "Id: " + data.id;
        document.querySelector('.user-card:nth-of-type(1) .user-name').innerText = "User Name: " + data.name;
        document.querySelector('.user-card:nth-of-type(1) img').src = "data:image/jpeg;base64," + data.img_data;
    } else if (data.userIndex == 2) {
        // Update the second user card with the correct data
        document.querySelector('.user-card:nth-of-type(2) .user-id').innerText = "Id: " + data.id;
        document.querySelector('.user-card:nth-of-type(2) .user-name').innerText = "User Name: " + data.name;
        document.querySelector('.user-card:nth-of-type(2) img').src = "data:image/jpeg;base64," + data.img_data;
    }
});
