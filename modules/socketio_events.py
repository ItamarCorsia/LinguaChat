from flask import session
from flask_socketio import join_room, leave_room, send,emit
from googletrans import Translator

translator = Translator()
# Translate text using googletrans between different language pairs.
def translate_multiple_languages(text: str, src_lang: str, tgt_lang: str):
    # Use googletrans to translate the text
    translation = translator.translate(text, src=src_lang, dest=tgt_lang)
    return translation.text


def register_socketio_events(socketio, rooms):
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
