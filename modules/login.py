from flask import render_template, request
from firebase_admin import storage
from firebase_admin import db
import numpy as np
import cv2
import base64
from flask_socketio import emit

def handle_login(app,socketio,player_data):
    # Renders the login page for the first user.
    @app.route('/loginAsFirst')
    def loginAsFirst():
        userIndex = "first"
        return render_template('login.html', userIndex=userIndex)

    # Renders the login page for the second user.
    @app.route('/loginAsSecond')
    def loginAsSecond():
        userIndex = "second"    
        return render_template('login.html', userIndex=userIndex)

    # Function to find a player ID by email from Firebase
    def find_player_id_by_email(target_email):
        # Get a reference to the 'players' node in the database
        ref = db.reference('players')

        # Get all players' data
        players = ref.get()

        # Check if players is a list and search for the player with the target email
        if isinstance(players, list):
            for player in players:
                if player is not None and player.get('email') == target_email:
                    return player.get('id')
            else:
                print(f"No player found with email: {target_email}")
        else:
            print("The 'players' variable is not a list.")

        return None

    # Function to retrieve and show a player's picture from Firebase storage
    def ShowPic(id):
        # Get the Firebase storage bucket
        bucket = storage.bucket()

        # Retrieve the image blob from the bucket using the player's id
        blob = bucket.get_blob(f'Images/{id}.png')
        # Convert the blob to a NumPy array
        array = np.frombuffer(blob.download_as_string(), np.uint8)
        # Decode the image array to an OpenCV image
        imPlayer = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

        # Encode the image to Base64
        _, buffer = cv2.imencode('.png', imPlayer)
        img_base64 = base64.b64encode(buffer).decode('utf-8')

        return img_base64

    # Update the global dictionary with the player's data
    def updatePlayerData(user_index, id, name, img_base64):
        player_data[f'id{user_index}'] = id
        player_data[f'name{user_index}'] = name
        player_data[f'img_data{user_index}'] = img_base64

        # Broadcast the updated player data to all connected clients
        socketio.emit('updateUser', {
            'userIndex': user_index,    
            'id': id,
            'name': name,
            'img_data': img_base64
        })

    # Handles profile login with image upload and player data update.
    @app.route('/upload_profile_login', methods=['POST'])
    def upload_profile_login():

        user_index = request.form.get('userIndex')
        email = request.form['email']

        # Find the player's ID based on their email
        id = find_player_id_by_email(email)

        file = ShowPic(id)

        # Determine the player index based on "first" or "second" user
        result = 1 if (user_index == "first") else 2
    
        # Update player data with the new information
        updatePlayerData(result, id, email, file)

        # Render the face detection page with the updated player data
        return render_template('faceDet.html', **player_data)

