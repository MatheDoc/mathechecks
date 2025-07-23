// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/12.0.0/firebase-app.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/12.0.0/firebase-analytics.js";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBqjhqgl1fJSgr5qwTjzplA8tO8gZfKZsc",
  authDomain: "mathechecks-c1e86.firebaseapp.com",
  projectId: "mathechecks-c1e86",
  storageBucket: "mathechecks-c1e86.firebasestorage.app",
  messagingSenderId: "352100850694",
  appId: "1:352100850694:web:70ca5dfece2f7a68ebb787",
  measurementId: "G-ZVSKFHE5F2",
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
