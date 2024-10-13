from firebase_admin import storage
from flask import render_template
from firebase_admin import db
import face_recognition
import numpy as np
import pickle
import cv2
import cvzone
import base64

def handle_home(app,player_data):
    # Function to capture video, detect faces, and return the player's ID
    def Gen():
        # Open the default camera
        cap = cv2.VideoCapture(0)
        # Set the width of the video capture window
        cap.set(3, 640)
        # Set the height of the video capture window
        cap.set(4, 480)

        counter = 0  # Initialize frame counter
        id = -1  # Initialize player ID
        # Load the encoding file
        file = open('EncodeFile.p', 'rb')  # Open the pickle file in read mode
        # Load encodings and player IDs
        encodeListKnownFacesWithId = pickle.load(file)
        file.close()

        # Separate encodings and player IDs
        encodeListKnownFaces, playersId = encodeListKnownFacesWithId
        
        while True and id == -1:
            # Capture a frame from the camera
            success, img = cap.read()

            # Resize the frame to 1/4 size for faster processing
            imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
            # Convert the frame from BGR to RGB
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

            # Detect face locations in the current frame
            faceCurrentFrame = face_recognition.face_locations(imgS)
            # Find face encodings in the current frame
            encodeCurrFrame = face_recognition.face_encodings(imgS, faceCurrentFrame)

            # Loop through each detected face encoding and location
            for encodeFace, faceLoc in zip(encodeCurrFrame, faceCurrentFrame):
                # Compare the detected face with known faces
                matches = face_recognition.compare_faces(encodeListKnownFaces, encodeFace)
                # Calculate the face distance (similarity)
                faceDis = face_recognition.face_distance(encodeListKnownFaces, encodeFace)

                # Get the index of the best match
                matchIndex = np.argmin(faceDis)
                # Retrieve the ID of the matched player
                id = playersId[matchIndex]

                # If a match is found, draw a rectangle around the face
                if matches[matchIndex]:
                    y1, x2, y2, x1 = faceLoc
                    # Scale up the face coordinates to match the original image size
                    y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                    bbox = x1, y1, x2 - x1, y2 - y1
                    # Draw a rectangle with rounded corners around the face
                    img = cvzone.cornerRect(img, bbox, rt=0)
                    id = playersId[matchIndex]

                    if counter == 0:
                        cv2.waitKey(1)
                        counter = 1

            # Display the video feed with detected faces
            cv2.imshow('Camera', img)

            # Break the loop on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # Release the camera and close windows
        cap.release()
        cv2.destroyAllWindows()

        return id  # Return the ID of the detected player

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

    def updatePlayerData(user_index,id,name,img_base64):
    # Update the global dictionary with the player's data
        player_data[f'id{user_index}'] = id
        player_data[f'name{user_index}'] = name
        player_data[f'img_data{user_index}'] = img_base64

    def getPlayerData(user_index):
        id = Gen()
        playerInfo = db.reference(f'players/{id}').get()
        name = playerInfo['email']
        img_base64 = ShowPic(id)
        
        updatePlayerData(user_index,id,name,img_base64)

    # Renders profile management page for the first user.
    @app.route('/refresh')
    def refresh():
        return render_template('faceDet.html', **player_data)

    # Resets player data for both players to their initial states.
    @app.route('/Reset')
    def reset():
        global player_data
        player_data = {
            'id1': 0,
            'name1': None,
            'img_data1': None,
            'id2': 0,
            'name2': None,
            'img_data2': None,
        }
        # Render the face detection page with the reset player data
        return render_template('faceDet.html', **player_data)

    # Resets player data and renders the face detection page.
    @app.route('/faceDet')
    def faceDet():
        return render_template('faceDet.html', **player_data)

    # Retrieves the first player's data and renders th  e face detection page.
    @app.route('/GetFirstUser')
    def firstPlayerData():
        getPlayerData(1)
        return render_template('faceDet.html', **player_data)

    # Retrieves the second player's data and renders the face detection page.
    @app.route('/GetSecondUser')
    def secondPlayerData():
        getPlayerData(2)
        return render_template('faceDet.html', **player_data)
