 // Import the functions you need from the SDKs you need
 import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.5/firebase-app.js";
 import { getAnalytics } from "https://www.gstatic.com/firebasejs/10.12.5/firebase-analytics.js";
 import { getDatabase } from "https://www.gstatic.com/firebasejs/10.12.5/firebase-database.js";
 import { getAuth, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.12.5/firebase-auth.js";

 // Your web app's Firebase configuration
 const firebaseConfig = {
     apiKey: "AIzaSyA2_Vl2ux4AT2urTAgd6gQSify_ZWsKUw8",
     authDomain: "facerec-94461.firebaseapp.com",
     databaseURL: "https://facerec-94461-default-rtdb.firebaseio.com",
     projectId: "facerec-94461",
     storageBucket: "facerec-94461.appspot.com",
     messagingSenderId: "40891611053",
     appId: "1:40891611053:web:0646be3b069e5b02c9d324",
     measurementId: "G-72KZK9M8JG"
 };

 // Initialize Firebase
 const app = initializeApp(firebaseConfig);
 const analytics = getAnalytics(app);
 const auth = getAuth();
 const database = getDatabase(app);

 document.getElementById('login').addEventListener('click', (e) => {
     e.preventDefault();
     var userIndex = document.querySelector('.user-info').textContent.split(' ')[0];
     var email = document.getElementById('email').value;
     var password = document.getElementById('password').value;

     const formData = new FormData();
     formData.append('email', email);
     formData.append('password', password);
     formData.append('userIndex', userIndex);  // Add userIndex to FormData

     fetch('/upload_profile_login', {
     method: 'POST',
     body: formData
     })
     .then(response => {
         if (!response.ok) {
             throw new Error('Network response was not ok');
         }
         return response.text(); // Get HTML response
     })
     .then(html => {
         // Replace the current page content with the response HTML
         document.documentElement.innerHTML = html;
     })
     .catch(error => {
         console.error('Error:', error);
     });

     signInWithEmailAndPassword(auth, email, password)
     .then((userCredential) => {
         // Signed in 
         const user = userCredential.user;
         alert('Login successful!');
     })
 });