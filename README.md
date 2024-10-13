
# LinguaChat

Multilingual Chat Rooms with Real-Time Translation & Speech Recognition




## Project Overview
LinguaChat is a real-time chat application that enables users to communicate across languages through automatic translation. It also includes a powerful speech recognition feature that converts spoken words into text and translates them into the user’s preferred language. The system supports user registration and login via Firebase, and allows for seamless multilingual conversations in chat rooms.
## Features

- Real-time Chat: Communicate in real-time within chat rooms.

- Automatic Translation: Messages are automatically translated into the user’s preferred language.

- Speech Recognition: Convert spoken words into text and have them translated on the fly.

- User Authentication: Secure registration and login system with Firebase integration.

- Face Recognition for Registration: When users upload a profile picture, the system detects all faces in the image and allows them to choose which face they would like to register with.

- Face Recognition for Login: The system recognizes known faces during login, allowing users already registered to be authenticated via face recognition.

- Profile Management: Users can update their email, password, and profile pictures.

- Firebase Storage: Secure storage for user data and images.
## Technologies Used
- Flask: Backend framework for creating the web server and handling HTTP requests.

- Socket.IO: Real-time communication between users for instant message translation.

- Firebase: Authentication, real-time database, and cloud storage for user data.

- Face Recognition: Facial recognition technology for both registration and login, allowing the system to identify known users based on their registered face data.

- Google Translate API (or similar): For automatic translation of messages.

- SpeechRecognition (Python): For recognizing spoken words and converting them into text.

- HTML/CSS/JavaScript: Frontend for user interaction.
## How It Works
- Sign Up / Login: Users can register or log in using their credentials, managed via Firebase.

- Profile Setup with Face Recognition: Users upload profile pictures, and the system detects faces in the image. Users then choose which face to use for their profile, ensuring accurate face recognition.

- Face Recognition for Known Users: If the user has already registered, the system can recognize their face during login, enabling face-based authentication.

- Create or Join Chat Rooms: Users can create a new chat room or join an existing one with a unique room code.

- Multilingual Chat: Users communicate in their native language, and the system translates the messages in real-time to the recipient's preferred language.

- Speech Recognition: Users can speak directly into the app, which converts their speech into translated text.

- Profile Management: Users can update their profile details (email, password, or picture) anytime.

## The directory ScreensAsImg have all the screen shots of all the screens.
# Screen Flow

## Welcome Screen

### Welcome to the App!

On this screen, you have two main options:

1. **Login**  
   If you already have an account, you can log in by clicking the **"Login"** button. This will take you to the face detection login page where the system will recognize you using facial recognition.

2. **Sign In (Register)**  
   If you're new here and don't have an account yet, click the **"Sign in"** button to create a new account and get started.

Choose the option that suits you and enjoy the experience!

