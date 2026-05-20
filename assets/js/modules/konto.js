import { buildAccountUrl, formatAuthDisplayName, getCurrentAuthState, getSupabaseClient, getSupabaseRuntimeConfig } from "../platform/supabase-client.js?v=20260517-oauth";

function setStatus(message, tone = "neutral") {
  document.querySelectorAll("[data-konto-notice]").forEach((statusNode) => {
    statusNode.hidden = !message;
    statusNode.textContent = message;
    statusNode.dataset.tone = tone;
  });
}

function setHeaderStatus(message, tone = "neutral") {
  const statusNode = document.querySelector("[data-konto-header-status]");
  if (!statusNode) return;
  statusNode.hidden = !message;
  statusNode.textContent = message;
  statusNode.dataset.tone = tone;
}

function getAuthView(user, recoveryMode) {
  if (recoveryMode) return "recovery";
  return user ? "signed-in" : "signed-out";
}

const signedOutText = {
  title: "Anmelden oder registrieren",
  copy: "Stelle dir deine persönliche Lernsession mit Action-Feed zusammen.",
};

const accountViewText = {
  signedIn: {
    title: "Konto",
    passwordCopy: "Vergib ein neues Passwort für dein Konto. Die aktuelle Session bleibt dabei aktiv.",
  },
  recovery: {
    title: "Neues Passwort setzen",
    passwordCopy: "Der Reset-Link hat eine temporäre Recovery-Session geöffnet. Vergib jetzt ein neues Passwort.",
  },
};

const oauthProviderMeta = {
  google: {
    label: "Google",
    iconSvg: {
      viewBox: "0 0 18 18",
      paths: [
        {
          fill: "#4285F4",
          d: "M17.64 9.2045c0-.6381-.0573-1.2518-.1636-1.8409H9v3.4818h4.8436c-.2086 1.125-.8427 2.0782-1.7968 2.715l2.9086 2.2582C16.6582 14.25 17.64 11.9727 17.64 9.2045z",
        },
        {
          fill: "#34A853",
          d: "M9 18c2.43 0 4.4673-.8055 5.9564-2.1805l-2.9086-2.2582c-.8055.54-1.8359.8591-3.0478.8591-2.3441 0-4.3282-1.5832-5.0364-3.7118L.96 12.9409C2.44 15.8795 5.4818 18 9 18z",
        },
        {
          fill: "#FBBC05",
          d: "M3.9636 10.7086A5.411 5.411 0 013.6818 9c0-.5945.1023-1.1718.2818-1.7086L.96 5.0591A8.9445 8.9445 0 000 9c0 1.4432.345 2.8091.96 3.9409l3.0036-2.2323z",
        },
        {
          fill: "#EA4335",
          d: "M9 3.5795c1.3214 0 2.5077.4541 3.4405 1.3459l2.5814-2.5814C13.4636.8918 11.4264 0 9 0 5.4818 0 2.44 2.1205.96 5.0591l3.0036 2.2323C4.6718 5.1627 6.6559 3.5795 9 3.5795z",
        },
      ],
    },
  },
  apple: {
    label: "Apple",
    iconClass: "fa-brands fa-apple",
  },
};

function createOAuthIcon(provider, providerMeta) {
  if (providerMeta.iconSvg) {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", providerMeta.iconSvg.viewBox);
    svg.setAttribute("aria-hidden", "true");
    svg.classList.add("konto-oauth-icon", `konto-oauth-icon--${provider}`);

    providerMeta.iconSvg.paths.forEach(({ fill, d }) => {
      const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      path.setAttribute("fill", fill);
      path.setAttribute("d", d);
      svg.appendChild(path);
    });

    return svg;
  }

  const icon = document.createElement("i");
  icon.className = `${providerMeta.iconClass} konto-oauth-icon konto-oauth-icon--${provider}`;
  icon.setAttribute("aria-hidden", "true");
  return icon;
}

function getDashboardPath() {
  const dashboardPath = String(document.querySelector("[data-dashboard-nav-item]")?.dataset.dashboardHref || "").trim();
  return dashboardPath.startsWith("/") ? dashboardPath : "/dashboard.html";
}

function getRequestedNextPath() {
  const searchParams = new URLSearchParams(window.location.search);
  const nextPath = String(searchParams.get("next") || "").trim();
  return nextPath.startsWith("/") ? nextPath : "";
}

function getAccountRedirectUrl() {
  return buildAccountUrl(getRequestedNextPath() || getDashboardPath());
}

function redirectToRequestedPath() {
  const nextPath = getRequestedNextPath();
  if (!nextPath) return false;

  const accountPathname = new URL(getSupabaseRuntimeConfig().accountPath, window.location.origin).pathname;
  const targetUrl = new URL(nextPath, window.location.origin);
  if (targetUrl.pathname === accountPathname) return false;

  window.location.replace(targetUrl.toString());
  return true;
}

function getEnabledOAuthProviders() {
  const configuredProviders = getSupabaseRuntimeConfig().oauthProviders;
  if (!Array.isArray(configuredProviders)) return [];

  return configuredProviders
    .map((provider) => String(provider || "").trim().toLowerCase())
    .filter((provider, index, providers) => provider && providers.indexOf(provider) === index)
    .filter((provider) => Boolean(oauthProviderMeta[provider]));
}

function renderOAuthProviders() {
  const container = document.querySelector("[data-konto-oauth-options]");
  if (!container) return false;

  const providers = getEnabledOAuthProviders();
  container.innerHTML = "";

  providers.forEach((provider) => {
    const providerMeta = oauthProviderMeta[provider];
    const button = document.createElement("button");
    const icon = createOAuthIcon(provider, providerMeta);
    const label = document.createElement("span");

    button.type = "button";
    button.className = "konto-oauth-button";
    button.dataset.kontoOauthProvider = provider;
    label.textContent = `Mit ${providerMeta.label} fortfahren`;

    button.append(icon, label);
    container.appendChild(button);
  });

  container.hidden = providers.length === 0;
  return providers.length > 0;
}

function setOAuthVisibility() {
  const hasProviders = getEnabledOAuthProviders().length > 0;
  const oauthContainer = document.querySelector("[data-konto-oauth-options]");
  const divider = document.querySelector("[data-konto-email-divider]");

  if (oauthContainer) oauthContainer.hidden = !hasProviders;
  if (divider) divider.hidden = !hasProviders;
}

function setOAuthButtonsDisabled(disabled) {
  document.querySelectorAll("[data-konto-oauth-provider]").forEach((button) => {
    button.disabled = disabled;
  });
}

function renderSignedOutMode() {
  const titleNode = document.querySelector("[data-konto-auth-card-title]");
  const copyNode = document.querySelector("[data-konto-auth-card-copy]");

  if (titleNode) titleNode.textContent = signedOutText.title;
  if (copyNode) copyNode.textContent = signedOutText.copy;

  setOAuthVisibility();
}

function renderAuthUi(user, recoveryMode) {
  const view = getAuthView(user, recoveryMode);
  document.body.dataset.kontoView = view;
  setHeaderStatus(user || recoveryMode ? "Angemeldet" : "Abgemeldet", user || recoveryMode ? "success" : "neutral");

  document.querySelectorAll("[data-auth-view]").forEach((node) => {
    const allowedViews = String(node.dataset.authView || "")
      .split(/\s+/)
      .map((value) => value.trim())
      .filter(Boolean);
    node.hidden = !allowedViews.includes(view);
  });

  const passwordCopy = document.querySelector("[data-konto-password-card-copy]");
  const accountTitle = document.querySelector("[data-konto-account-card-title]");
  const accountText = recoveryMode ? accountViewText.recovery : accountViewText.signedIn;

  if (passwordCopy) {
    passwordCopy.textContent = accountText.passwordCopy;
  }
  if (accountTitle) {
    accountTitle.textContent = accountText.title;
  }

  document.querySelectorAll("[data-konto-normal-only]").forEach((node) => {
    node.hidden = recoveryMode;
  });

  if (!user && !recoveryMode) {
    renderSignedOutMode();
  }
}

function isPasswordRecoveryFlow() {
  const searchParams = new URLSearchParams(window.location.search);
  const hashParams = new URLSearchParams(window.location.hash.replace(/^#/, ""));
  return searchParams.get("type") === "recovery" || hashParams.get("type") === "recovery";
}

function cleanupAuthUrl() {
  const url = new URL(window.location.href);
  const searchParams = url.searchParams;
  const hashParams = new URLSearchParams(url.hash.replace(/^#/, ""));
  const transientKeys = [
    "type",
    "access_token",
    "refresh_token",
    "expires_at",
    "expires_in",
    "token_type",
    "provider_token",
    "provider_refresh_token",
    "code",
  ];

  let changed = false;
  transientKeys.forEach((key) => {
    if (searchParams.has(key)) {
      searchParams.delete(key);
      changed = true;
    }
    if (hashParams.has(key)) {
      hashParams.delete(key);
      changed = true;
    }
  });

  if (!changed) return;

  const nextSearch = searchParams.toString();
  const nextHash = hashParams.toString();
  const nextUrl = `${url.pathname}${nextSearch ? `?${nextSearch}` : ""}${nextHash ? `#${nextHash}` : ""}`;
  window.history.replaceState({}, document.title, nextUrl);
}

function mapAuthError(error, fallbackMessage) {
  const code = String(error?.code || error?.error_code || "").trim().toLowerCase();
  const message = String(error?.message || "").trim();
  const normalized = message.toLowerCase();

  if (code === "over_email_send_rate_limit") {
    return "Zu viele Auth-Mails in kurzer Zeit. Die aktuelle Supabase-Standard-Mailzustellung ist stark begrenzt. Warte etwas oder richte für weitere Tests ein eigenes SMTP-Setup ein.";
  }

  if (code === "email_address_not_authorized") {
    return "Diese E-Mail-Adresse ist für die aktuelle Supabase-Standardzustellung nicht freigegeben. Ohne eigenes SMTP sendet Supabase nur an vorautorisierte Team-Adressen.";
  }

  if (code === "invalid_credentials") {
    return "Anmeldung fehlgeschlagen. Prüfe die E-Mail-Adresse oder fordere einen neuen Link an.";
  }

  if (code === "email_not_confirmed") {
    return "Die E-Mail-Adresse ist noch nicht bestätigt. Prüfe dein Postfach und bestätige zuerst dein Konto.";
  }

  if (code === "user_already_exists" || code === "email_exists") {
    return "Für diese E-Mail-Adresse existiert bereits ein Konto. Nutze den Anmeldelink oder die externe Anmeldung.";
  }

  if (code === "same_password") {
    return "Das neue Passwort muss sich vom bisherigen Passwort unterscheiden.";
  }

  if (code === "weak_password") {
    return "Das neue Passwort ist zu schwach. Wähle ein längeres oder robusteres Passwort.";
  }

  if (code === "pgrst202" || normalized.includes("delete_current_user_account")) {
    return "Kontolöschung ist aktuell nicht verfügbar. Prüfe die Supabase-Migration.";
  }

  if (code.includes("provider") || normalized.includes("provider is not enabled") || normalized.includes("unsupported provider")) {
    return "Diese externe Anmeldung ist in Supabase noch nicht aktiviert. Prüfe die OAuth-Provider im Supabase-Dashboard.";
  }

  if (!normalized) {
    return fallbackMessage;
  }

  if (normalized.includes("email rate limit exceeded")) {
    return "Zu viele Auth-Mails in kurzer Zeit. Die aktuelle Supabase-Standard-Mailzustellung ist stark begrenzt. Warte etwas oder richte für weitere Tests ein eigenes SMTP-Setup ein.";
  }

  if (normalized.includes("email address not authorized")) {
    return "Diese E-Mail-Adresse ist für die aktuelle Supabase-Standardzustellung nicht freigegeben. Ohne eigenes SMTP sendet Supabase nur an vorautorisierte Team-Adressen.";
  }

  if (normalized.includes("invalid login credentials")) {
    return "Anmeldung fehlgeschlagen. Prüfe die E-Mail-Adresse oder fordere einen neuen Link an.";
  }

  if (normalized.includes("email not confirmed")) {
    return "Die E-Mail-Adresse ist noch nicht bestätigt. Prüfe dein Postfach und bestätige zuerst dein Konto.";
  }

  if (normalized.includes("user already registered")) {
    return "Für diese E-Mail-Adresse existiert bereits ein Konto. Nutze den Anmeldelink oder die externe Anmeldung.";
  }

  if (normalized.includes("oauth") || normalized.includes("external provider")) {
    return "Diese externe Anmeldung konnte nicht gestartet werden. Prüfe die OAuth-Provider im Supabase-Dashboard.";
  }

  if (normalized.includes("confirmation required")) {
    return "Gib zur Bestätigung LÖSCHEN ein.";
  }

  if (normalized.includes("account not found")) {
    return "Das Konto wurde nicht gefunden oder ist bereits gelöscht.";
  }

  return message || fallbackMessage;
}

function setConfiguredState(configured) {
  if (configured) return;

  document.querySelectorAll("[data-requires-supabase]").forEach((node) => {
    node.hidden = true;
  });
}

function renderProfile(user) {
  const profileSummary = document.querySelector("[data-konto-profile-summary]");

  if (profileSummary) {
    profileSummary.textContent = user
      ? `Angemeldet als ${formatAuthDisplayName(user)}${user.email ? ` (${user.email})` : ""}.`
      : "Du bist nicht angemeldet.";
  }
}

async function handleEmailAuth(event, supabase) {
  event.preventDefault();
  const form = event.currentTarget;
  const formData = new FormData(form);
  const email = String(formData.get("email") || "").trim();
  const redirectTo = getAccountRedirectUrl();

  setStatus("Anmeldelink wird versendet ...");

  const { error } = await supabase.auth.signInWithOtp({
    email,
    options: {
      emailRedirectTo: redirectTo,
      shouldCreateUser: true,
    },
  });

  if (error) {
    throw error;
  }

  setStatus("Anmeldelink versendet. Prüfe dein Postfach.", "success");
  form?.reset();
}

async function handleOAuthSignIn(provider, supabase) {
  const providerMeta = oauthProviderMeta[provider];
  if (!providerMeta) {
    setStatus("Diese externe Anmeldung wird aktuell nicht unterstützt.", "error");
    return;
  }

  setStatus(`Weiterleitung zu ${providerMeta.label} ...`);
  setOAuthButtonsDisabled(true);

  const { error } = await supabase.auth.signInWithOAuth({
    provider,
    options: {
      redirectTo: getAccountRedirectUrl(),
    },
  });

  if (error) {
    setOAuthButtonsDisabled(false);
    throw error;
  }
}

async function handlePasswordUpdate(event, supabase, recoveryMode) {
  event.preventDefault();
  const form = event.currentTarget;
  const formData = new FormData(form);
  const password = String(formData.get("password") || "");
  const confirmPassword = String(formData.get("password_confirm") || "");

  if (password.length < 6) {
    setStatus("Das neue Passwort muss mindestens 6 Zeichen haben.", "error");
    return;
  }

  if (password !== confirmPassword) {
    setStatus("Die beiden Passwortfelder stimmen nicht überein.", "error");
    return;
  }

  setStatus("Neues Passwort wird gesetzt ...");

  const { error } = await supabase.auth.updateUser({ password });
  if (error) {
    throw error;
  }

  cleanupAuthUrl();
  setStatus(recoveryMode ? "Passwort aktualisiert. Du bist jetzt wieder normal angemeldet." : "Passwort aktualisiert.", "success");
  form?.reset();
}

async function handleSignOut(supabase) {
  setStatus("Abmeldung läuft ...");
  const { error } = await supabase.auth.signOut({ scope: "local" });
  if (error) {
    throw error;
  }
  renderProfile(null);
  setStatus("");
}

async function handleDeleteAccount(event, supabase, onDeleted) {
  event.preventDefault();
  const form = event.currentTarget;
  const formData = new FormData(form);
  const confirmation = String(formData.get("confirmation") || "").trim();

  if (confirmation.toLocaleUpperCase("de-DE") !== "LÖSCHEN") {
    setStatus("Gib zur Bestätigung LÖSCHEN ein.", "error");
    return;
  }

  setStatus("Konto wird gelöscht ...");

  const { error } = await supabase.rpc("delete_current_user_account", {
    p_confirmation: confirmation,
  });

  if (error) {
    throw error;
  }

  await supabase.auth.signOut({ scope: "local" }).catch(() => undefined);

  form?.reset();
  onDeleted();
  setStatus("Konto gelöscht. Du bist abgemeldet.", "success");
}

async function initKontoPage() {
  const config = getSupabaseRuntimeConfig();
  setConfiguredState(config.configured);
  let recoveryMode = isPasswordRecoveryFlow();
  let currentUser = null;

  if (recoveryMode) {
    cleanupAuthUrl();
  }

  if (!config.configured) {
    setHeaderStatus("");
    setStatus("Supabase ist noch nicht konfiguriert. Ergänze zuerst `supabase_url` und `supabase_anon_key` in Jekyll.");
    return;
  }

  const supabase = await getSupabaseClient();
  if (!supabase) {
    setStatus("Supabase-Client konnte nicht initialisiert werden.", "error");
    return;
  }

  const applyUiState = (user, nextRecoveryMode = recoveryMode) => {
    currentUser = user || null;
    recoveryMode = nextRecoveryMode;
    renderProfile(currentUser);
    renderAuthUi(currentUser, recoveryMode);
  };

  const applyRecoveryMode = (enabled) => {
    recoveryMode = enabled;
    renderAuthUi(currentUser, enabled);
  };

  supabase.auth.onAuthStateChange((event, session) => {
    if (event === "SIGNED_IN" || event === "USER_UPDATED" || event === "TOKEN_REFRESHED") {
      currentUser = session?.user || currentUser;
      renderProfile(currentUser);
      renderAuthUi(currentUser, recoveryMode);
      cleanupAuthUrl();
      if (!recoveryMode && redirectToRequestedPath()) {
        return;
      }
    }

    if (event === "PASSWORD_RECOVERY") {
      currentUser = session?.user || currentUser;
      renderProfile(currentUser);
      applyRecoveryMode(true);
      cleanupAuthUrl();
      setStatus("Reset-Link erkannt. Vergib jetzt ein neues Passwort.", "neutral");
      return;
    }

    if (event === "SIGNED_OUT") {
      applyUiState(null, false);
    }
  });

  const state = await getCurrentAuthState();
  currentUser = state.user || null;
  applyUiState(currentUser, recoveryMode);

  if (state.user && !recoveryMode && redirectToRequestedPath()) {
    return;
  }

  if (state.error) {
    setStatus("Supabase ist konfiguriert, aber aktuell nicht erreichbar.", "error");
  } else if (state.user) {
    cleanupAuthUrl();
    if (recoveryMode) {
      setStatus("Reset-Link erkannt. Vergib jetzt ein neues Passwort.", "neutral");
    } else {
      setStatus("");
    }
  } else {
    setStatus("");
  }

  const emailAuthForm = document.querySelector("[data-konto-email-auth]");
  const updatePasswordForm = document.querySelector("[data-konto-password-update]");
  const signOutButton = document.querySelector("[data-konto-signout]");
  const deleteAccountForm = document.querySelector("[data-konto-delete]");
  const oauthContainer = document.querySelector("[data-konto-oauth-options]");

  renderOAuthProviders();

  oauthContainer?.addEventListener("click", async (event) => {
    const button = event.target instanceof Element ? event.target.closest("[data-konto-oauth-provider]") : null;
    if (!button) return;

    try {
      await handleOAuthSignIn(button.dataset.kontoOauthProvider, supabase);
    } catch (error) {
      setStatus(mapAuthError(error, "Externe Anmeldung konnte nicht gestartet werden."), "error");
    }
  });

  emailAuthForm?.addEventListener("submit", async (event) => {
    try {
      await handleEmailAuth(event, supabase);
    } catch (error) {
      setStatus(mapAuthError(error, "Anmeldelink konnte nicht versendet werden."), "error");
    }
  });

  updatePasswordForm?.addEventListener("submit", async (event) => {
    try {
      const wasRecoveryMode = recoveryMode;
      await handlePasswordUpdate(event, supabase, wasRecoveryMode);
      const nextState = await getCurrentAuthState();
      applyUiState(nextState.user, false);
    } catch (error) {
      setStatus(mapAuthError(error, "Passwort konnte nicht aktualisiert werden."), "error");
    }
  });

  signOutButton?.addEventListener("click", async () => {
    try {
      await handleSignOut(supabase);
      applyUiState(null, false);
    } catch (error) {
      setStatus(mapAuthError(error, "Abmeldung fehlgeschlagen."), "error");
    }
  });

  deleteAccountForm?.addEventListener("submit", async (event) => {
    try {
      await handleDeleteAccount(event, supabase, () => applyUiState(null, false));
    } catch (error) {
      setStatus(mapAuthError(error, "Konto konnte nicht gelöscht werden."), "error");
    }
  });
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    initKontoPage();
  }, { once: true });
} else {
  initKontoPage();
}