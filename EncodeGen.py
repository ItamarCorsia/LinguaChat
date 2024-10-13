import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://facerec-94461-default-rtdb.firebaseio.com/",
    'storageBucket': "facerec-94461.appspot.com"
})

# Define folder path and list initialization
folderPlayersPath = 'Images'
lsPlayersName = os.listdir(folderPlayersPath)
imgList = []
playersIds = []

# Load images and upload to Firebase Storage
for player in lsPlayersName:
    imgPath = os.path.join(folderPlayersPath, player)
    imgList.append(cv2.imread(imgPath))
    playersIds.append(os.path.splitext(player)[0])

    # Upload image to Firebase Storage
    bucket = storage.bucket()
    blob = bucket.blob(f'Images/{player}')
    blob.upload_from_filename(imgPath)

def findEncoding(imagesList):
    encodeList = []

    for img in imagesList:
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        face_encodings = face_recognition.face_encodings(img_rgb)
        
        if face_encodings:  # Check if any faces were detected
            encodeList.append(face_encodings[0])
        else:
            print("No faces found in the image.")

    return encodeList

encodeListKnownFaces = findEncoding(imgList)
encodeListKnownFacesWithId = [encodeListKnownFaces, playersIds]

# Save encodings and IDs to a pickle file
with open("EncodeFile.p", 'wb') as file:
    pickle.dump(encodeListKnownFacesWithId, file)

print("Encoding data saved.")
