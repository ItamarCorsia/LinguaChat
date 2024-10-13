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

### The directory ScreensAsImg have all the screen shots of all the screens.

                                                                           # Screen Flow

## Welcome Screen
![1](https://github.com/user-attachments/assets/23fd55f4-8b5c-4559-be7c-406e4a55eef3)

### Welcome to the App!

On this screen, you have two main options:

1. **Login**  
   If you already have an account, click the **"Login"** button. This will take you to the face detection login page where the system will recognize you using facial recognition.

2. **Sign In (Register)**  
   If you're new here and don't have an account yet, click the **"Sign in"** button to create a new account and get started.

**Choose the option that suits you and enjoy the experience!**

---

## Sign In Screen

### Welcome to the Registration Page!

To create an account, follow these steps:

1. **Enter Your Details:**
   - **Email:** Type your email address in the provided field.
   - **Password:** Create a password to secure your account.

2. **Upload Profile Picture:**  
   Click the **"Choose File"** button to select an image from your device. This picture will be used for face detection during the login process.

3. **Face Detection (Optional):**  
   After selecting a profile picture, the system will automatically detect faces from the uploaded image. You’ll be prompted to select your face from the detected options. Simply click on the correct image, and it will be highlighted.

4. **Confirm Your Face:**  
   Once you've selected your face, click the **"Confirm Face"** button to finalize your registration.

5. **Complete Registration:**  
   When everything is set, the system will process your information and display a message confirming whether the registration was successful.

**Please ensure to select a profile picture for face detection, as it’s required for logging in later. Once you’ve completed these steps, you’ll be ready to use the app!**

---

## Login Screen

### Welcome to the Login Page!

You have two options to log in as either the First User or Second User.

### Login Methods:

1. **Face Detection Login:**  
   You can use face detection to log in quickly. Just click the **"Face Detection"** button, and the system will try to recognize you through your face.

2. **Login with Password:**  
   If you prefer, you can log in using your password. Simply click the **"Login with password"** button for the user you want to log in as.

### Profile Management:

After logging in, you can update your profile. To do so, click the **"Update profile"** button. This will allow you to manage and change your profile details.

---

## Welcome to the User Dashboard

After successfully logging in, you will see a dashboard that displays information for two users: **First User** and **Second User**. Each user will have their own card, providing quick access to essential functions.

### User Information

**User Cards:** Each card displays the following:
- **User ID:** This is a unique identifier for the user.
- **User Name:** The name associated with the account.
- **Profile Picture:** A small image representing the user, displayed as a base64-encoded JPEG.

### Available Actions for Each User

1. **Face Detection:**  
   Click the **Face Detection** button to initiate facial recognition for the respective user.

2. **Login with Password:**  
   Use the **Login with password** button to authenticate using the user's password.

3. **Update Profile:**  
   The **Update profile** button allows users to manage their profile information.

4. **Find Room:**  
   Click the **Find room** button to enter the chat room and start interacting with other users.

### Additional Options

- **Reset:**  
  Clicking the **Reset** button will reset the current session, allowing users to log in again or switch users.

- **Refresh:**  
  The **Refresh** button will reload the current page to ensure you have the latest information.

This dashboard enables smooth navigation and access to essential features for both users, ensuring an engaging and user-friendly experience.

---

## Finding a Room

Once logged in, you will also be able to find and join a room by clicking the **"Find room"** button. This feature is only available after you've logged in.

Here, users can select their preferred language. All messages sent by other users will be translated and delivered in the recipient's chosen language!

---

## Welcome to the Chat Room

After selecting your preferred language and entering the chat room, you’ll be presented with an interactive messaging interface designed for seamless communication with other users.

### Chat Room Details

- **Chat Room Title:** The title of the chat room is displayed at the top, showing the unique room code (`{{code}}`). This helps you identify the specific chat room you’re currently in.

### Message Area

- **Messages Display:** The main area of the chat room is designated for displaying messages. This is where you can see all the conversations happening in real-time.

### Sending Messages

1. **Message Input:**  
   At the bottom of the screen, you’ll find an input field labeled **"Type your message..."**. You can type your message here to communicate with others in the room.

2. **Send Button:**  
   Once you’ve typed your message, click the **Send** button to share it with everyone in the chat room.

### Voice Messaging

1. **Start Recording:**  
   If you prefer to send voice messages, click the **Start Recording** button to begin capturing your voice.

2. **Stop Recording:**  
   After you’re done speaking, click the **Stop Recording** button to finish. This feature allows for a more interactive communication experience.

### Real-Time Messaging

- **Message Display:** Messages from other users are dynamically displayed in the chat area. The system translates and shows the messages in your selected language, ensuring you understand all conversations.

This chat room interface offers a user-friendly platform for engaging with others in real-time, whether through text or voice, while maintaining language preferences for seamless communication.
