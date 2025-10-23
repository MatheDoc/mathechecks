const firebaseConfig = {
  apiKey: "AIzaSyBqjhqgl1fJSgr5qwTjzplA8tO8gZfKZsc",
  authDomain: "mathechecks-c1e86.firebaseapp.com",
  projectId: "mathechecks-c1e86",
};

firebase.initializeApp(firebaseConfig);
const auth = firebase.auth();

// DOM Elements
const modalOverlay = document.getElementById("auth-modal-overlay");
const authFormDiv = document.getElementById("auth-form");
const userInfoDiv = document.getElementById("user-info");
const authForm = document.getElementById("auth-form-element");
const emailInput = document.getElementById("email");
const passwordInput = document.getElementById("password");
const submitBtn = document.getElementById("submit-btn");
const toggleMode = document.getElementById("toggle-mode");
const toggleText = document.getElementById("toggle-text");
const formTitle = document.getElementById("form-title");
const formSubtitle = document.getElementById("form-subtitle");
const messageDiv = document.getElementById("message");
const displayEmail = document.getElementById("display-email");
const displayUid = document.getElementById("display-uid");
const logoutBtn = document.getElementById("logout-btn");

let isLoginMode = true;

// Toggle Account Menu (wird von deinem Button aufgerufen)
function toggleAccountMenu() {
  modalOverlay.classList.add("show");
  document.body.style.overflow = "hidden";
}

// Close Modal
function closeAuthModal(event) {
  if (!event || event.target === modalOverlay) {
    modalOverlay.classList.remove("show");
    document.body.style.overflow = "";
    hideMessage();
  }
}

// Show message
function showMessage(text, isError = false) {
  messageDiv.className = isError ? "error" : "success";
  messageDiv.textContent = text;
  messageDiv.style.display = "block";
}

function hideMessage() {
  messageDiv.style.display = "none";
}

// Toggle between Login and Register
toggleMode.addEventListener("click", () => {
  isLoginMode = !isLoginMode;
  hideMessage();

  if (isLoginMode) {
    formTitle.textContent = "Login";
    formSubtitle.textContent = "Melde dich mit deinem Account an";
    submitBtn.textContent = "Login";
    toggleText.textContent = "Noch kein Account?";
    toggleMode.textContent = "Jetzt registrieren";
  } else {
    formTitle.textContent = "Registrierung";
    formSubtitle.textContent = "Erstelle einen neuen Account";
    submitBtn.textContent = "Registrieren";
    toggleText.textContent = "Schon registriert?";
    toggleMode.textContent = "Zum Login";
  }
});

// Form Submit
authForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  hideMessage();

  const email = emailInput.value.trim();
  const password = passwordInput.value;

  if (password.length < 6) {
    showMessage("Passwort muss mindestens 6 Zeichen lang sein", true);
    return;
  }

  submitBtn.disabled = true;
  submitBtn.textContent = isLoginMode
    ? "Login läuft..."
    : "Registrierung läuft...";

  try {
    if (isLoginMode) {
      await auth.signInWithEmailAndPassword(email, password);
      showMessage("Login erfolgreich!");
    } else {
      await auth.createUserWithEmailAndPassword(email, password);
      showMessage("Registrierung erfolgreich!");
    }
  } catch (error) {
    console.error("Auth Error:", error);
    let errorMessage = "Ein Fehler ist aufgetreten";

    switch (error.code) {
      case "auth/email-already-in-use":
        errorMessage =
          "Diese E-Mail ist bereits registriert. Bitte logge dich ein.";
        break;
      case "auth/invalid-email":
        errorMessage = "Ungültige E-Mail-Adresse";
        break;
      case "auth/weak-password":
        errorMessage =
          "Passwort zu schwach. Mindestens 6 Zeichen erforderlich.";
        break;
      case "auth/user-not-found":
        errorMessage = "Kein Account mit dieser E-Mail gefunden";
        break;
      case "auth/wrong-password":
        errorMessage = "Falsches Passwort";
        break;
      case "auth/invalid-login-credentials":
        errorMessage = "Falsches Passwort oder E-Mail nicht gefunden";
        break;
      case "auth/invalid-credential":
        errorMessage =
          "Ungültige Anmeldedaten. Bitte überprüfe E-Mail und Passwort.";
        break;
      case "auth/too-many-requests":
        errorMessage = "Zu viele Versuche. Bitte warte einen Moment.";
        break;
      default:
        errorMessage = error.message;
    }

    showMessage(errorMessage, true);
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = isLoginMode ? "Login" : "Registrieren";
  }
});

// Logout
logoutBtn.addEventListener("click", async () => {
  try {
    await auth.signOut();
    emailInput.value = "";
    passwordInput.value = "";
    closeAuthModal();
  } catch (error) {
    console.error("Logout Error:", error);
    showMessage("Fehler beim Logout: " + error.message, true);
  }
});

// Auth State Observer
auth.onAuthStateChanged((user) => {
  if (user) {
    authFormDiv.classList.add("hidden");
    userInfoDiv.classList.remove("hidden");
    displayEmail.textContent = user.email;
    displayUid.textContent = user.uid;
  } else {
    authFormDiv.classList.remove("hidden");
    userInfoDiv.classList.add("hidden");
    hideMessage();
  }
});

// ESC-Taste zum Schließen
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && modalOverlay.classList.contains("show")) {
    closeAuthModal();
  }
});
