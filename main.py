from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase
import os
import signal
import subprocess
import pickle
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
import base64
from googletrans import Translator
import speech_recognition as sr
import threading

# Initialize Flask app
app = Flask(__name__)
# Set a secret key for session management
app.config["SECRET_KEY"] = "dss11"
# Initialize SocketIO with Flask app for real-time communication
socketio = SocketIO(app)

translator = Translator()

recognizer = sr.Recognizer()

latest_transcription = ""

# Load Firebase credentials from the JSON file
cred = credentials.Certificate("serviceAccountKey.json")
# Initialize Firebase app with credentials, database, and storage bucket
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://facerec-94461-default-rtdb.firebaseio.com/",
    'storageBucket': "facerec-94461.appspot.com"
})

# Global dictionary to store player data
player_data = {
    'id1': 0,
    'name1': None,
    'img_data1': None,
    'id2': 0,
    'name2': None,
    'img_data2': None,
}

# Dictionary to store active rooms
rooms = {}

# Function to generate a unique room code of a specified length
def generate_unique_code(length):
    while True:
        code = ""
        # Generate a random code using uppercase letters
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        
        # Ensure the generated code is not already in use
        if code not in rooms:
            break
    
    return code

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

# Function to upload profile picture and player details to Firebase
def upload_profile(file, email, password, id):
    # Set the filename to the player's ID with a .png extension
    file.filename = f"{id}.png"
    local_file_path = os.path.join('Images', file.filename)  # Define the local file path
    print(f"Saving file to: {local_file_path}")

# Function to kill a process running on a specific port
def kill_process_on_port(port):
    # Run a shell command to find the process using the specified port
    result = subprocess.run(
        f"netstat -ano | findstr :{port}",
        shell=True,
        capture_output=True,
        text=True
    )
    # Split the output into lines
    lines = result.stdout.splitlines()
    # Loop through the lines to find and kill the process
    for line in lines:
        parts = line.split()  # Split the line into parts
        pid = parts[-1]  # Get the process ID (PID)
        if pid:
            # Kill the process using the PID
            os.kill(int(pid), signal.SIGTERM)

# Function to handle form submission for creating or joining a room
def handle_form_submission():
    # Get the player's name from the form
    name = request.form.get("name")
    # Get the room code from the form
    code = request.form.get("code")
    # Get the join and create options from the form
    join = request.form.get("join", False)
    create = request.form.get("create", False)

    language = request.form.get("target_language")  # Get the user's selected language
    print("Here!!")
    print(language)

    # Validate the form data
    error_response = validate_form_data(name, code, join)
    if error_response:
        return error_response
    
    # Handle room creation or joining
    room = handle_room_creation_or_joining(name, code, create)
    if room is None:
        return render_template("home.html", error="Room does not exist.", code=code, name=name)
    
    # Store the room code and player name in the session
    session["room"] = room
    session["name"] = name
    session["language"] = language  # Store the language preference in the session

    # Redirect the player to the room page
    return redirect(url_for("room"))

# Validates the form data for player name and room code.
def validate_form_data(name, code, join):
    # Check if the name field is empty
    if not name:
        # If name is empty, render home page with an error message
        return render_template("home.html", error="Please enter a name.", code=code, name=name)
    
    # Check if joining a room and the room code is missing
    if join != False and not code:
        # If no room code provided, render home page with an error message
        return render_template("home.html", error="Please enter a room code.", code=code, name=name)
    
    # If all validations pass, return None (no error)
    return None

# Manages the logic for creating or joining a room.
def handle_room_creation_or_joining(name, code, create):
    if create != False:
        # Create a new room and return its code
        room = generate_unique_code(4)
        rooms[room] = {
            "members": {},   # Initialize as an empty dictionary to store member data
            "members_count": 0,  # Initialize a counter for the number of members
            "messages": []   # To store messages
        }
        return room
    
    if code in rooms:
        # Return the existing room code if it exists
        return code
    
    # Return None if the room doesn't exist
    return None

# Renders the home page with a player's name pre-filled.
def render_home_page(userIndex):
    # Render the home page with the player's name pre-filled
    return render_template("home.html", name=player_data[f'name{userIndex}'])

 # Update the global dictionary with the player's data

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

# Renders the face detection page with player data.
@app.route('/')
def home():
    # Render the index (home) page
    return render_template('index.html')

# Renders profile management page for the first user.
@app.route('/refresh')
def refresh():
    # Render the face detection page with player data
    return render_template('faceDet.html', **player_data)

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

# Resets player data for both players to their initial states.
@app.route('/Reset')
def reset():
    # Reset player data for both players to their initial states
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

# Renders the login page for the first user.
@app.route('/loginAsFirst')
def loginAsFirst():
    # Render the login page for the first user
    userIndex = "first"
    return render_template('login.html', userIndex=userIndex)

# Renders the login page for the second user.
@app.route('/loginAsSecond')
def loginAsSecond():
    # Render the login page for the second user
    userIndex = "second"    
    return render_template('login.html', userIndex=userIndex)

# Resets player data and renders the face detection page.
@app.route('/faceDet')
def faceDet():
    # Reset player data and render the face detection page
    # reset()
    return render_template('faceDet.html', **player_data)

# Renders the registration page.
@app.route('/register')
def register():
    # Render the registration page
    return render_template('register.html')

# Retrieves the first player's data and renders the face detection page.
@app.route('/GetFirstUser')
def firstPlayerData():
    # Retrieve the first player's data and render the face detection page
    getPlayerData(1)
    return render_template('faceDet.html', **player_data)

# Retrieves the second player's data and renders the face detection page.
@app.route('/GetSecondUser')
def secondPlayerData():
    # Retrieve the second player's data and render the face detection page
    getPlayerData(2)
    return render_template('faceDet.html', **player_data)

# Updates the profile information, including handling profile picture changes.
@app.route('/update_profile', methods=['POST'])
def update_profile():
    # Get the user's index, email, and password from the form submission
    user_index = request.form.get('userIndex')
    email = request.form.get('email')
    password = request.form.get('password')
    print(email)
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
        resized_face = cv2.resize(face_image, (400, 400))

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
    global indexId  # Declare indexId as a global variable
    
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

# Connects a user to the system and emits updated user data to all connected clients.
@app.route('/connect_user', methods=['POST'])
def connect_user():

    # Get the user data from the POST request (JSON format)
    user_index = request.json['userIndex']
    id = request.json['id']
    name = request.json['name']
    img_base64 = request.json['img_data']
    
    print(f"Emitting Data - Index: {user_index}, ID: {id}, Name: {name}")
    
    # Emit the updated user data to all clients via Socket.IO
    socketio.emit('updateUser', {
        'userIndex': user_index,
        'id': id,
        'name': name,
        'img_data': img_base64
    })
    
    return "User connected"

# Handles the home page for the first player
@app.route('/FirstPlayerRoom', methods=["POST", "GET"])
def firstPlayerRoom():
    session.clear()
    
    if request.method == "POST":
        # Handle the form submission process
        return handle_form_submission()
    
    # Handle GET requests: display the home page with the player's name pre-filled
    return render_home_page(1)

# Handles the home page for the second player.
@app.route('/SecondPlayerRoom',methods=["POST", "GET"])
def secondPlayerRoom():
    # Clear any existing session data to start fresh
    session.clear()
    
    if request.method == "POST":
        # Handle the form submission process
        return handle_form_submission()
    
    # Handle GET requests: display the home page with the player's name pre-filled
    return render_home_page(2)

# Renders the room page based on the session data.
@app.route('/room')
def room():
    
    # Get the room code from the session data
    room = session.get("room")
    
    # Check if room or name is missing from the session, or if the room doesn't exist in the rooms dictionary
    if room is None or session.get("name") is None or room not in rooms:
        # If any of the conditions above are true, redirect the user to the home page
        return redirect(url_for("home"))
    
    # Render the room template and pass the room code and the list of messages in that room
    return render_template("room.html", code=room, messages=rooms[room]["messages"])

# Translate text using googletrans between different language pairs.
def translate_multiple_languages(text: str, src_lang: str, tgt_lang: str):
    # Use googletrans to translate the text
    translation = translator.translate(text, src=src_lang, dest=tgt_lang)
    return translation.text

# Handles incoming messages from a client.
@socketio.on("message")
def message(data):
    # Get the room code from the session data
    room = session.get("room")
    SenderLanguage = session.get("language")
    senderName = session.get("name")
    reciverLanguge = []
    translated_en = []
    meesage = data["data"]

    for room, details in rooms.items():
                
        # Print members and their languages
        print("Members and their languages:")
        for name, info in details["members"].items():
            print(f"  Name: {name}, Language: {info['language']}")

            if(name != senderName):
                if(info['language'] != SenderLanguage): 
                    reciverLanguge = info['language']  
                    print("reciver lang")
                    print(reciverLanguge)
                    translated_en = translate_multiple_languages(meesage,SenderLanguage, reciverLanguge)

    # Create a dictionary containing the sender's name and the message content
    content = {
        "name": session.get("name"),
        "ogMessage": data["data"],
        "trMessage": translated_en
    }

    # Send the message content to all clients in the room
    send(content, to=room)
    
    # Append the message content to the list of messages in the room
    rooms[room]["messages"].append(content)

    # Print the message to the server console for debugging
    print(f"{session.get('name')} said: {data['data']}")
   
# Handles a client connecting to the server.
@socketio.on("connect")
def connect(auth):
    # Get the room code and name from the session data
    room = session.get("room")
    name = session.get("name")
    language = session.get("language")  # Get the user's language from the session
    
    # If the room or name is missing, exit the function
    if not room or not name:
        return
    
    # If the room is not in the rooms dictionary, leave the room and exit the function
    if room not in rooms:
        leave_room(room)
        return
    
    # Ensure the room has the 'members' dictionary and 'members_count'
    if "members" not in rooms[room]:
        rooms[room]["members"] = {}
    if "members_count" not in rooms[room]:
        rooms[room]["members_count"] = 0

    # Join the user to the room
    join_room(room)
    
        # Add the user's language preference to the room's data
    rooms[room]["members"][name] = {
        "language": language
    }
    originalMessage = "has entered the room"

    translated_en = []

    if(language != 'en'):
        translated_en = translate_multiple_languages(originalMessage,'en',language)

    # Send a message to all clients in the room notifying that the user has entered
    send({"name": name, "ogMessage": originalMessage, "trMessage": translated_en}, to=room)
    
    # Increment the number of members in the room by 1
    rooms[room]["members_count"] += 1
    
    # Print a message to the server console for debugging
    print(f"{name} joined room {room} with language preference: {language}")

# Update the global dictionary with the player's data
def updatePlayerData(user_index, id, name, img_base64):
    # Update the global dictionary with the player's data
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

# Handles a client disconnecting from the server.
@socketio.on("disconnect")
def disconnect():
    # Get the room code and name from the session data
    room = session.get("room")
    name = session.get("name")
    
    # Leave the room
    leave_room(room)

    # If the room exists in the rooms dictionary
    if room in rooms:
        # Decrease the number of members in the room by 1
        rooms[room]["members_count"] -= 1
        
        # If no members are left in the room, delete the room from the rooms dictionary
        if rooms[room]["members_count"] <= 0:
            del rooms[room]
    
    # Send a message to all clients in the room notifying that the user has left
    send({"name": name, "message": "has left the room"}, to=room)
    
    # Print a message to the server console for debugging
    print(f"{name} has left the room {room}")

# Start recording
def start_recording():
    print("Listening... Press the 'Stop Recording' button to stop.")
    with sr.Microphone() as source:
        audio_data = recognizer.listen(source)
        return audio_data

# Process the audio
def process_audio(audio):
    global latest_transcription
    try:
        text = recognizer.recognize_google(audio, language='fr-FR')
        print(f"You said: {text}")
        latest_transcription = text
    except sr.UnknownValueError:
        latest_transcription = "Sorry, I could not understand the audio. Please try again!"

# Start the ranscription
@app.route("/start_recording", methods=["POST"])
def handle_start_recording():
    global listen_thread

    listen_thread = threading.Thread(target=lambda: process_audio(start_recording()))
    listen_thread.start()

    return jsonify({"message": "Recording started"}), 200

# Stop the ranscription
@app.route("/stop_recording", methods=["POST"])
def handle_stop_recording():
    global listen_thread
    if listen_thread:
        listen_thread.join()
        listen_thread = None
        return jsonify({"message": "Recording stopped"}), 200
    else:
        return jsonify({"message": "No recording in progress"}), 400

@app.route("/get_transcription", methods=["GET"])
def get_transcription():
    global latest_transcription
    return jsonify({"text": latest_transcription})

# Main entry point of the application.
if __name__ == "__main__":
    """
    Main entry point of the application.
    
    - Ensures that any process using port 5000 is killed before starting the app.
    - Runs the Flask application with Socket.IO support on port 5000 in debug mode.
    """
            
    # Ensure the port is not in use by killing any process using port 5000
    kill_process_on_port(5000)
    
    # Run the Flask application with Socket.IO support on port 5000 with debug mode enabled
    socketio.run(app, port=5000, debug=True)
