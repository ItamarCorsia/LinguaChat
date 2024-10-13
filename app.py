from flask import Flask
from flask_socketio import SocketIO
import firebase_admin
from firebase_admin import credentials
from modules.init import handle_init
from modules.home import handle_home
from modules.updateProfile import handle_update_profile
from modules.login import handle_login
from modules.register import handleregistration
from modules.chatRooms import handleChatRooms
from modules.socketio_events import register_socketio_events
from modules.recording import speech_recognition

# Initialize Flask app
app = Flask(__name__)
# Set a secret key for session management
app.config["SECRET_KEY"] = "dss11"
# Initialize SocketIO with Flask app for real-time communication
socketio = SocketIO(app)
# Load Firebase credentials from the JSON file
#cred = credentials.Certificate("serviceAccountKey.json")
# Initialize Firebase app with credentials, database, and storage bucket
#firebase_admin.initialize_app(cred, {
#    'databaseURL': "https://facerec-94461-default-rtdb.firebaseio.com/",
#    'storageBucket': "facerec-94461.appspot.com"
#})
# Global dictionary to store player data, including IDs, names, and image data
player_data = {
    'id1': 0,
    'name1': None,
    'img_data1': None,
    'id2': 0,
    'name2': None,
    'img_data2': None,
}
# Dictionary to store active chat rooms with room details
rooms = {}

# Call the function from init module to set up initial configurations
handle_init(app)

# Call the function from home module to handle home page and related routes
handle_home(app, player_data)

# Call the function from updateProfile module to handle user profile updates
handle_update_profile(app, player_data)

# Call the function from login module to manage user login, passing SocketIO and player data
handle_login(app, socketio, player_data)

# Call the function from register module to manage user registration
handleregistration(app)

# Call the function from chatRooms module to handle chat room creation and management
handleChatRooms(app, socketio, rooms, player_data)

# Register Socket.IO events to manage real-time communication in chat rooms
register_socketio_events(socketio, rooms)

# Call the function to handle speech recognition routes and events
speech_recognition(app)

# Main entry point of the application.
if __name__ == "__main__":      
    # Run the Flask application with Socket.IO support on port 5000 and enable debug mode
    socketio.run(app, port=5000, debug=True)
