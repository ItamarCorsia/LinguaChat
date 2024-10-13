from flask import render_template, request
from firebase_admin import storage
from firebase_admin import db
import base64
import os

def handle_update_profile(app,player_data):
    # Renders profile management page for the first user.
    @app.route('/profileManagementAsFirst')
    def profileManagementAsFirst():
        # Render profile management page for the first user
        userIndexSt = "First"
        userIndex = 1
        # Retrieve name and image data for the first player
        name_placeholder = player_data.get('name1')
        img_data = player_data.get('img_data1')
        # Render the profile management template with the corresponding data
        return render_template('profileManagement.html', name_placeholder=name_placeholder, img_data=img_data, userIndex=userIndex, userIndexSt=userIndexSt)

    # Renders profile management page for the second user.
    @app.route('/profileManagementAsSecond')
    def profileManagementAsSecond():
        # Render profile management page for the second user
        userIndexSt = "Second"
        userIndex = 2
        # Retrieve name and image data for the second player
        name_placeholder = player_data.get('name2')
        img_data = player_data.get('img_data2')
        # Render the profile management template with the corresponding data
        return render_template('profileManagement.html', name_placeholder=name_placeholder, img_data=img_data, userIndex=userIndex, userIndexSt=userIndexSt)

    # Updates the profile information, including handling profile picture changes.
    @app.route('/update_profile', methods=['POST'])
    def update_profile():
        # Get the user's index, email, and password from the form submission
        user_index = request.form.get('userIndex')
        email = request.form.get('email')
        password = request.form.get('password')
        # Determine user index based on string value ("First" or "Second")
        user_index = 1 if (user_index == "First") else 2
        # Get the player's ID using the user index
        id = player_data[f'id{user_index}']

        # Handle profile picture update if provided in the form
        if 'profilePicture' in request.files and request.files['profilePicture'].filename != '':
            file = request.files['profilePicture']
            # Ensure the Images directory exists
            if not os.path.exists('Images'):
                os.makedirs('Images')

            # Save the profile picture locally with the player's ID as the filename
            file.filename = f"{id}.png"
            local_file_path = os.path.join('Images', file.filename)
            file.save(local_file_path)

            # Upload the file to Firebase storage
            bucket = storage.bucket()
            blob = bucket.blob(f'Images/{file.filename}')
            blob.upload_from_filename(local_file_path)

            # Convert the image to base64 format and store it in player_data
            with open(local_file_path, "rb") as image_file:
                img_data = base64.b64encode(image_file.read()).decode('utf-8')

            # Update player data with the new profile picture
            player_data[f'img_data{user_index}'] = img_data
        else:
            # If no new picture, use the existing one
            img_data = player_data.get(f'img_data{user_index}')

        # Reference the player's Firebase data
        user_ref = db.reference(f'players/{id}')

        # Prepare updates for Firebase
        updates = {}
        
        if email:
            # Update the player's name (email) locally and in Firebase
            player_data[f'name{user_index}'] = email
            updates['email'] = email

        if password:
            # Update the password in Firebase
            updates['password'] = password

        # Apply updates to Firebase
        if updates:
            user_ref.update(updates)

        # Render the updated face detection page
        return render_template('faceDet.html', **player_data)
