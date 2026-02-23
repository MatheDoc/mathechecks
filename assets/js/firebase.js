(function () {
  let resolveAuthReady = null;
  window.MATHECHECKS_AUTH_READY = new Promise((resolve) => {
    resolveAuthReady = resolve;
  });

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
  const forgotPasswordRow = document.getElementById("forgot-password-row");
  const forgotPasswordBtn = document.getElementById("forgot-password-btn");
  const displayEmail = document.getElementById("display-email");
  const displayUid = document.getElementById("display-uid");
  const logoutBtn = document.getElementById("logout-btn");
  const accountButton = document.getElementById("account-button");
  const accountMenuText = document.getElementById("account-menu-text");

  let isLoginMode = true;

  function showMessage(text, isError) {
    if (!messageDiv) return;
    messageDiv.className = isError ? "error" : "success";
    messageDiv.textContent = text;
    messageDiv.style.display = "block";
  }

  function hideMessage() {
    if (!messageDiv) return;
    messageDiv.style.display = "none";
    messageDiv.textContent = "";
  }

  function updateNavAuthState(user) {
    if (accountButton) {
      accountButton.classList.toggle("is-logged-in", !!user);
      accountButton.classList.toggle("is-logged-out", !user);
      accountButton.setAttribute(
        "aria-label",
        user ? "Konto öffnen" : "Anmelden oder Konto öffnen"
      );
      const icon = accountButton.querySelector("i");
      if (icon) {
        icon.className = user ? "fa-solid fa-user-check" : "fa-regular fa-user";
      }
    }

    if (accountMenuText) {
      accountMenuText.textContent = user ? "Konto" : "Anmelden";
    }
  }

  window.toggleAccountMenu = function toggleAccountMenu() {
    if (!modalOverlay) return;
    modalOverlay.classList.add("show");
    document.body.style.overflow = "hidden";
  };

  window.closeAuthModal = function closeAuthModal(event) {
    if (!modalOverlay) return;
    if (!event || event.target === modalOverlay) {
      modalOverlay.classList.remove("show");
      document.body.style.overflow = "";
      hideMessage();
    }
  };

  if (!modalOverlay || !authForm) {
    return;
  }

  const globalConfig = window.MATHECHECKS_FIREBASE_CONFIG || {};
  const firebaseConfig = {
    apiKey: globalConfig.apiKey || window.FIREBASE_API_KEY || "",
    authDomain: globalConfig.authDomain || window.FIREBASE_AUTH_DOMAIN || "",
    projectId: globalConfig.projectId || window.FIREBASE_PROJECT_ID || "",
  };

  const firebaseEnabled =
    typeof firebase !== "undefined" &&
    !!firebaseConfig.apiKey &&
    !!firebaseConfig.authDomain &&
    !!firebaseConfig.projectId;

  if (!firebaseEnabled) {
    updateNavAuthState(null);
    showMessage("Login ist momentan nicht verfügbar (Firebase-Konfiguration fehlt).", true);
    submitBtn.disabled = true;
    if (resolveAuthReady) {
      resolveAuthReady({ auth: null, db: null });
      resolveAuthReady = null;
    }
    return;
  }

  if (!firebase.apps.length) {
    firebase.initializeApp(firebaseConfig);
  }

  const auth = firebase.auth();
  const db = typeof firebase.firestore === "function" ? firebase.firestore() : null;
  window.MATHECHECKS_AUTH = auth;
  window.MATHECHECKS_DB = db;

  if (resolveAuthReady) {
    resolveAuthReady({ auth, db });
    resolveAuthReady = null;
  }

  auth.setPersistence(firebase.auth.Auth.Persistence.LOCAL).catch(() => {});

  function mapAuthError(error) {
    switch (error.code) {
      case "auth/email-already-in-use":
        return "Diese E-Mail ist bereits registriert. Bitte logge dich ein.";
      case "auth/invalid-email":
        return "Ungültige E-Mail-Adresse.";
      case "auth/weak-password":
        return "Passwort zu schwach. Mindestens 6 Zeichen erforderlich.";
      case "auth/user-not-found":
        return "Kein Account mit dieser E-Mail gefunden.";
      case "auth/wrong-password":
      case "auth/invalid-login-credentials":
      case "auth/invalid-credential":
        return "Ungültige Anmeldedaten. Bitte E-Mail und Passwort prüfen.";
      case "auth/popup-closed-by-user":
        return "Anmeldung wurde abgebrochen.";
      case "auth/popup-blocked":
        return "Popup blockiert. Bitte Popups für diese Seite erlauben.";
      case "auth/operation-not-allowed":
        return "Diese Anmeldemethode ist in Firebase noch nicht aktiviert.";
      case "auth/api-key-expired":
        return "Der Firebase API-Key ist abgelaufen. Bitte in Firebase/Google Cloud einen neuen Web-API-Key setzen.";
      case "auth/too-many-requests":
        return "Zu viele Versuche. Bitte warte einen Moment.";
      case "auth/missing-email":
        return "Bitte zuerst eine E-Mail-Adresse eingeben.";
      default:
        return error.message || "Ein Fehler ist aufgetreten.";
    }
  }

  toggleMode.addEventListener("click", () => {
    isLoginMode = !isLoginMode;
    hideMessage();

    if (isLoginMode) {
      formTitle.textContent = "Login";
      formSubtitle.textContent = "Melde dich mit deinem Account an";
      submitBtn.textContent = "Login";
      toggleText.textContent = "Noch kein Account?";
      toggleMode.textContent = "Jetzt registrieren";
      if (forgotPasswordRow) {
        forgotPasswordRow.classList.remove("hidden");
      }
    } else {
      formTitle.textContent = "Registrierung";
      formSubtitle.textContent = "Erstelle einen neuen Account";
      submitBtn.textContent = "Registrieren";
      toggleText.textContent = "Schon registriert?";
      toggleMode.textContent = "Zum Login";
      if (forgotPasswordRow) {
        forgotPasswordRow.classList.add("hidden");
      }
    }
  });

  if (forgotPasswordBtn) {
    forgotPasswordBtn.addEventListener("click", async () => {
      hideMessage();
      const email = emailInput.value.trim();

      if (!email) {
        showMessage("Bitte gib zuerst deine E-Mail-Adresse ein.", true);
        return;
      }

      try {
        await auth.sendPasswordResetEmail(email);
        showMessage("Passwort-Reset gesendet. Bitte prüfe dein E-Mail-Postfach.", false);
      } catch (error) {
        showMessage(mapAuthError(error), true);
      }
    });
  }

  authForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    hideMessage();

    const email = emailInput.value.trim();
    const password = passwordInput.value;

    if (!email) {
      showMessage("Bitte eine E-Mail-Adresse eingeben.", true);
      return;
    }

    if (password.length < 6) {
      showMessage("Passwort muss mindestens 6 Zeichen lang sein.", true);
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = isLoginMode
      ? "Login läuft..."
      : "Registrierung läuft...";

    try {
      if (isLoginMode) {
        await auth.signInWithEmailAndPassword(email, password);
      } else {
        await auth.createUserWithEmailAndPassword(email, password);
      }
      hideMessage();
    } catch (error) {
      showMessage(mapAuthError(error), true);
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = isLoginMode ? "Login" : "Registrieren";
    }
  });

  logoutBtn.addEventListener("click", async () => {
    try {
      await auth.signOut();
      emailInput.value = "";
      passwordInput.value = "";
      window.closeAuthModal();
    } catch (error) {
      showMessage(mapAuthError(error), true);
    }
  });

  auth.onAuthStateChanged((user) => {
    updateNavAuthState(user);

    window.dispatchEvent(
      new CustomEvent("mathechecks-auth-changed", {
        detail: { user },
      })
    );

    if (user) {
      authFormDiv.classList.add("hidden");
      userInfoDiv.classList.remove("hidden");
      displayEmail.textContent = user.email || "";
      displayUid.textContent = user.uid || "";
      hideMessage();
    } else {
      authFormDiv.classList.remove("hidden");
      userInfoDiv.classList.add("hidden");
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && modalOverlay.classList.contains("show")) {
      window.closeAuthModal();
    }
  });
})();
