from firebase_admin import storage
from firebase_admin import db
from flask import request, jsonify,render_template
import face_recognition
import base64
import pickle
import cv2
import os

def handleregistration(app):
    global indexId

    # Initialize Firebase and get the current indexId
    def initialize_index():
        # Get a reference to 'indexId' in the database
        index_ref = db.reference('indexId')
        # Retrieve the current value of 'indexId'
        index_value = index_ref.get()
        # If 'indexId' is not set, initialize it to 1
        if index_value is None:
            index_ref.set(1)
            return 1
        return index_value

    # Initialize indexId from Firebase
    indexId = initialize_index()

    # Function to find and return face encodings for a list of images
    def findEncoding(imagesList):
        encodeList = []
        for img in imagesList:
            # Convert the image from BGR to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # Find the encoding of the image
            encode = face_recognition.face_encodings(img)[0]
            # Append the encoding to the list
            encodeList.append(encode)

        return encodeList

    # Function to encode face images and save them with their corresponding IDs
    def encode():
        # Define the path to the folder containing player images
        folderPlayersPath = 'Images'
        # Get the list of player image filenames
        lsPlayersName = os.listdir(folderPlayersPath)
        imgList = []  # List to store player images
        playersIds = []  # List to store player IDs

        # Loop through each player image
        for player in lsPlayersName:
            # Read the image and append it to the list
            imgList.append(cv2.imread(os.path.join(folderPlayersPath, player)))
            # Extract and append the player ID (filename without extension)
            playersIds.append(os.path.splitext(player)[0])

            # Define the full file path
            fileName = f'{folderPlayersPath}/{player}'
            # Get the Firebase storage bucket
            bucket = storage.bucket()
            # Create a blob and upload the file to Firebase storage
            blob = bucket.blob(fileName)
            blob.upload_from_filename(fileName)

        # Find the encodings for all player images
        encodeListKnownFaces = findEncoding(imgList)
        # Combine encodings and player IDs into a list
        encodeListKnownFacesWithId = [encodeListKnownFaces, playersIds]

        # Save the encodings and IDs to a pickle file
        file = open("EncodeFile.p", 'wb')
        pickle.dump(encodeListKnownFacesWithId, file)
        file.close()

        # Renders the registration page.
    
    @app.route('/register')
    def register():
        # Render the registration page
        return render_template('register.html')

    # Handles profile upload, saves image locally and uploads to Firebase.
    @app.route('/upload_profile', methods=['POST'])
    def upload_profile():
        if 'profilePicture' not in request.files:
            return jsonify(success=False, message="No file uploaded"), 400

        file = request.files['profilePicture']
        email = request.form['email']
        password = request.form['password']

        if file.filename == '':
            return jsonify(success=False, message="No selected file"), 400

        # Save the uploaded file temporarily
        file_path = os.path.join('Images', f'{indexId}.png')
        file.save(file_path)

        # Detect faces using face_recognition
        image = cv2.imread(file_path)
        face_locations = face_recognition.face_locations(image)

        if len(face_locations) == 0:
            return jsonify(success=False, message="No faces detected"), 400

        faces_base64 = []   
        for (top, right, bottom, left) in face_locations:
            face_image = image[top:bottom, left:right]
            resized_face = cv2.resize(face_image, (300, 300))

            # Encode the resized face as a base64 string
            _, buffer = cv2.imencode('.png', resized_face)
            face_base64 = base64.b64encode(buffer).decode('utf-8')
            faces_base64.append(face_base64)

        # Save the selected face in the user's record (for demonstration purposes)
        user_ref = db.reference(f'players/{indexId}')
        user_ref.set({
            'email': email,
            'id': indexId,
            'password': password
        })

        return jsonify(success=True, faces=faces_base64)

    @app.route('/finalize_registration', methods=['POST'])
    def finalize_registration():
        global indexId
        data = request.get_json()  # Get the JSON data from the request
        image_data = data.get('image')
        fileName = f'{indexId}.png'
        
        if image_data:
            # Decode the Base64 string back to binary image data
            selected_face = base64.b64decode(image_data)
            
            # Create the file path with the indexId
            file_path = os.path.join("Images", fileName)
            
            # Save the image data to the file
            with open(file_path, 'wb') as file:
                file.write(selected_face)

        # Upload the file to Firebase storage
        bucket = storage.bucket()
        blob = bucket.blob(f'Images/{fileName}')
        blob.upload_from_filename(file_path)

        indexId += 1
        db.reference('indexId').set(indexId)
        encode()
        return jsonify(success=True)
