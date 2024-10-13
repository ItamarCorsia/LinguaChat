from flask import render_template, request, session, redirect, url_for
import random
from string import ascii_uppercase

def handleChatRooms(app,socketio,rooms,player_data):
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

    # Renders the home page with a player's name pre-filled.
    def render_home_page(userIndex):
        # Render the home page with the player's name pre-filled
        return render_template("home.html", name=player_data[f'name{userIndex}'])

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