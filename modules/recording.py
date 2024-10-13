import speech_recognition as sr
import threading
from flask import jsonify

# Global variables

recognizer = sr.Recognizer()
latest_transcription = ""
listen_thread = None

def speech_recognition(app):
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

    # Start the transcription
    @app.route("/begin_recording", methods=["POST"])
    def handle_begin_recording():
        global listen_thread
        if listen_thread is None:  # Ensure there is no active recording thread
            listen_thread = threading.Thread(target=lambda: process_audio(start_recording()))
            listen_thread.start()
            return jsonify({"message": "Recording started"}), 200
        else:
            return jsonify({"message": "Recording already in progress"}), 400

    # Stop the transcription
    @app.route("/stop_recording", methods=["POST"])
    def handle_stop_recording():
        global listen_thread
        if listen_thread:
            listen_thread.join()
            listen_thread = None
            return jsonify({"message": "Recording stopped"}), 200
        else:
            return jsonify({"message": "No recording in progress"}), 400

    # Get the latest transcription
    @app.route("/get_transcription", methods=["GET"])
    def get_transcription():
        global latest_transcription
        return jsonify({"text": latest_transcription})
