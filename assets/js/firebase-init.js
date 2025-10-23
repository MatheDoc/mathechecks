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

// Wenn die ältere compat-SDK (globales `firebase`) bereits geladen ist,
// vermeiden wir eine zusätzliche modulare Initialisierung, da das
// zu Konflikten mit FirebaseUI (compat) führen kann.
if (typeof window !== 'undefined' && window.firebase) {
  console.log('firebase-init.js: compat SDK detected — skipping modular initialization');
  // Optional: expose a small marker so other Modules know that the app exists
  window.__firebase_compat_initialized = true;
} else {
  // Initialize Firebase (modular SDK)
  const app = initializeApp(firebaseConfig);
  const analytics = getAnalytics(app);
  // Optional: expose app for debugging
  window.__firebase_modular_app = app;
}
