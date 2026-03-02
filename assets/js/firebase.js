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
  const usernameInput = document.getElementById("username");
  const usernameGroup = document.getElementById("username-group");
  const displayEmail = document.getElementById("display-email");
  const displayUid = document.getElementById("display-uid");
  const displayUsername = document.getElementById("display-username");
  const logoutBtn = document.getElementById("logout-btn");
  const accountButton = document.getElementById("account-button");
  const accountMenuText = document.getElementById("account-menu-text");

  // Account-Verwaltung: Username ändern
  const changeUsernameToggle = document.getElementById("change-username-toggle");
  const changeUsernameForm = document.getElementById("change-username-form");
  const newUsernameInput = document.getElementById("new-username");
  const changeUsernameBtn = document.getElementById("change-username-btn");
  const changeUsernameCancel = document.getElementById("change-username-cancel");

  // Account-Verwaltung: Account löschen
  const deleteAccountToggle = document.getElementById("delete-account-toggle");
  const deleteAccountConfirm = document.getElementById("delete-account-confirm");
  const deleteConfirmPassword = document.getElementById("delete-confirm-password");
  const deleteAccountBtn = document.getElementById("delete-account-btn");
  const deleteAccountCancel = document.getElementById("delete-account-cancel");
  const userMessage = document.getElementById("user-message");

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

  auth.setPersistence(firebase.auth.Auth.Persistence.LOCAL).catch(() => { });

  function mapAuthError(error) {
    const errorMessage = (error && error.message ? String(error.message) : "").toLowerCase();

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
        if (errorMessage.includes("requests-from-referer") || errorMessage.includes("referer") && errorMessage.includes("blocked")) {
          return "Firebase blockiert diese Test-URL. Bitte den Host in den API-Key-Referrer-Regeln erlauben (z. B. localhost:4001 und 127.0.0.1:4001).";
        }
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
      if (usernameGroup) {
        usernameGroup.classList.add("hidden");
        if (usernameInput) usernameInput.removeAttribute("required");
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
      if (usernameGroup) {
        usernameGroup.classList.remove("hidden");
        if (usernameInput) usernameInput.setAttribute("required", "");
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

  // Enter in E-Mail- oder Passwort-Feld → Formular absenden
  [emailInput, passwordInput].forEach((input) => {
    if (input) {
      input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          authForm.requestSubmit ? authForm.requestSubmit() : submitBtn.click();
        }
      });
    }
  });

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

    const username = usernameInput ? usernameInput.value.trim() : "";
    if (!isLoginMode) {
      if (!username || username.length < 3) {
        showMessage("Benutzername muss mindestens 3 Zeichen lang sein.", true);
        return;
      }
      if (username.length > 30) {
        showMessage("Benutzername darf maximal 30 Zeichen lang sein.", true);
        return;
      }
      if (!/^[a-zA-Z0-9_\-äöüÄÖÜß]+$/.test(username)) {
        showMessage("Benutzername darf nur Buchstaben, Zahlen, _ und - enthalten.", true);
        return;
      }
    }

    submitBtn.disabled = true;
    submitBtn.textContent = isLoginMode
      ? "Login läuft..."
      : "Registrierung läuft...";

    try {
      if (isLoginMode) {
        await auth.signInWithEmailAndPassword(email, password);
      } else {
        const usernameLower = username.toLowerCase();

        // 1) Auth-Account anlegen (Nutzer ist danach eingeloggt)
        const credential = await auth.createUserWithEmailAndPassword(email, password);
        const user = credential.user;

        try {
          // 2) Vorab-Check: Benutzername schon vergeben?
          //    (Schnelles UX-Feedback; echte Absicherung über Firestore-Rules beim Batch-Write)
          if (db) {
            const existingDoc = await db.collection("usernames").doc(usernameLower).get();
            if (existingDoc.exists) {
              throw new Error("USERNAME_TAKEN");
            }
          }

          // 3) Atomarer Batch-Write: Username reservieren + Profil anlegen
          const batch = db.batch();

          const usernameRef = db.collection("usernames").doc(usernameLower);
          batch.set(usernameRef, {
            uid: user.uid,
            username: username,
            createdAt: firebase.firestore.FieldValue.serverTimestamp()
          });

          const userRef = db.collection("users").doc(user.uid);
          batch.set(userRef, {
            username: username,
            email: email,
            createdAt: firebase.firestore.FieldValue.serverTimestamp()
          }, { merge: true });

          await batch.commit();

          // 4) displayName im Firebase-Auth-Profil setzen
          await user.updateProfile({ displayName: username });

        } catch (batchError) {
          // Registrierung fehlgeschlagen → Auth-Account aufräumen
          console.error("Username-Reservierung fehlgeschlagen:", batchError);
          try { await user.delete(); } catch (_) { /* best effort */ }
          showMessage("Dieser Benutzername ist bereits vergeben. Bitte wähle einen anderen.", true);
          return;
        }
      }
      hideMessage();
      window.closeAuthModal();
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

  // ── Hilfsfunktion: Meldungen im User-Info-Bereich ──────
  function showUserMessage(text, isError) {
    if (!userMessage) return;
    userMessage.className = isError ? "error" : "success";
    userMessage.textContent = text;
    userMessage.style.display = "block";
  }

  function hideUserMessage() {
    if (!userMessage) return;
    userMessage.style.display = "none";
    userMessage.textContent = "";
  }

  // ── Benutzername ändern ────────────────────────────────
  if (changeUsernameToggle) {
    changeUsernameToggle.addEventListener("click", () => {
      changeUsernameForm.classList.toggle("hidden");
      hideUserMessage();
    });
  }

  if (changeUsernameCancel) {
    changeUsernameCancel.addEventListener("click", () => {
      changeUsernameForm.classList.add("hidden");
      if (newUsernameInput) newUsernameInput.value = "";
      hideUserMessage();
    });
  }

  if (changeUsernameBtn) {
    changeUsernameBtn.addEventListener("click", async () => {
      hideUserMessage();
      const user = auth.currentUser;
      if (!user || !db) return;

      const newName = newUsernameInput ? newUsernameInput.value.trim() : "";
      const newNameLower = newName.toLowerCase();

      // Validierung
      if (!newName || newName.length < 3) {
        showUserMessage("Benutzername muss mindestens 3 Zeichen lang sein.", true);
        return;
      }
      if (newName.length > 30) {
        showUserMessage("Benutzername darf maximal 30 Zeichen lang sein.", true);
        return;
      }
      if (!/^[a-zA-Z0-9_\-äöüÄÖÜß]+$/.test(newName)) {
        showUserMessage("Benutzername darf nur Buchstaben, Zahlen, _ und - enthalten.", true);
        return;
      }

      // Gleicher Name?
      const oldName = user.displayName || "";
      if (newName === oldName) {
        showUserMessage("Das ist bereits dein Benutzername.", true);
        return;
      }

      changeUsernameBtn.disabled = true;
      changeUsernameBtn.textContent = "Wird gespeichert...";

      try {
        // 1) Prüfen, ob neuer Name frei ist
        const existingDoc = await db.collection("usernames").doc(newNameLower).get();
        if (existingDoc.exists) {
          showUserMessage("Dieser Benutzername ist bereits vergeben.", true);
          return;
        }

        // 2) Neuen Namen reservieren
        await db.collection("usernames").doc(newNameLower).set({
          uid: user.uid,
          username: newName,
          createdAt: firebase.firestore.FieldValue.serverTimestamp()
        });

        // 3) Alten Namen freigeben (falls vorhanden)
        if (oldName) {
          const oldNameLower = oldName.toLowerCase();
          try {
            await db.collection("usernames").doc(oldNameLower).delete();
          } catch (_) { /* best effort – alter Eintrag ggf. nicht vorhanden */ }
        }

        // 4) Profil aktualisieren
        await user.updateProfile({ displayName: newName });
        await db.collection("users").doc(user.uid).set({
          username: newName
        }, { merge: true });

        // 5) UI aktualisieren
        if (displayUsername) {
          displayUsername.textContent = "Willkommen, " + newName + "!";
        }

        changeUsernameForm.classList.add("hidden");
        if (newUsernameInput) newUsernameInput.value = "";
        showUserMessage("Benutzername erfolgreich geändert!", false);

      } catch (error) {
        console.error("Username-Änderung fehlgeschlagen:", error);
        showUserMessage("Fehler beim Ändern des Benutzernamens. Bitte versuche es erneut.", true);
      } finally {
        changeUsernameBtn.disabled = false;
        changeUsernameBtn.textContent = "Speichern";
      }
    });
  }

  // ── Account löschen ────────────────────────────────────
  if (deleteAccountToggle) {
    deleteAccountToggle.addEventListener("click", () => {
      deleteAccountConfirm.classList.toggle("hidden");
      hideUserMessage();
    });
  }

  if (deleteAccountCancel) {
    deleteAccountCancel.addEventListener("click", () => {
      deleteAccountConfirm.classList.add("hidden");
      if (deleteConfirmPassword) deleteConfirmPassword.value = "";
      hideUserMessage();
    });
  }

  if (deleteAccountBtn) {
    deleteAccountBtn.addEventListener("click", async () => {
      hideUserMessage();
      const user = auth.currentUser;
      if (!user) return;

      const password = deleteConfirmPassword ? deleteConfirmPassword.value : "";
      if (!password) {
        showUserMessage("Bitte gib zur Bestätigung dein Passwort ein.", true);
        return;
      }

      deleteAccountBtn.disabled = true;
      deleteAccountBtn.textContent = "Wird gelöscht...";

      try {
        // 1) Re-Authentifizierung (erforderlich für sensible Aktionen)
        const credential = firebase.auth.EmailAuthProvider.credential(user.email, password);
        await user.reauthenticateWithCredential(credential);

        // 2) Username-Reservierung löschen
        if (db && user.displayName) {
          const nameLower = user.displayName.toLowerCase();
          try {
            await db.collection("usernames").doc(nameLower).delete();
          } catch (_) { /* best effort */ }
        }

        // 3) User-Dokument löschen (inkl. Subcollections bleibt Firebase-Limitation)
        if (db) {
          try {
            await db.collection("users").doc(user.uid).delete();
          } catch (_) { /* best effort */ }
        }

        // 4) Auth-Account löschen
        await user.delete();

        // 5) UI zurücksetzen
        emailInput.value = "";
        passwordInput.value = "";
        if (deleteConfirmPassword) deleteConfirmPassword.value = "";
        window.closeAuthModal();

      } catch (error) {
        console.error("Account-Löschung fehlgeschlagen:", error);
        if (error.code === "auth/wrong-password" || error.code === "auth/invalid-credential") {
          showUserMessage("Falsches Passwort. Bitte erneut versuchen.", true);
        } else {
          showUserMessage("Fehler beim Löschen des Accounts: " + (error.message || "Unbekannter Fehler"), true);
        }
      } finally {
        deleteAccountBtn.disabled = false;
        deleteAccountBtn.textContent = "Endgültig löschen";
      }
    });
  }

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

      // Benutzername anzeigen
      if (displayUsername) {
        const name = user.displayName || user.email || "Willkommen!";
        displayUsername.textContent = name.startsWith("Willkommen") ? name : "Willkommen, " + name + "!";
      }

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
