---
layout: shell
title: Konto
description: Anmeldung, Registrierung, externe Anmeldung und Kontoverwaltung.
page_context: Konto
topbar_status: true
nav: dashboard
body_class: page-dashboard
published: true
permalink: /konto.html
module_script: /assets/js/modules/konto.js?v=20260517-konto-unified
page_css: /assets/css/konto.css?v=20260517-konto-unified
---

<div class="bento konto-grid">
    <article class="card konto-card konto-auth-card" data-requires-supabase data-auth-view="signed-out" hidden>
        <div class="card-header">
            <span class="card-title" data-konto-auth-card-title></span>
        </div>
        <p class="konto-card__hint" data-konto-auth-card-copy></p>
        <p class="konto-card__notice" data-konto-notice data-tone="neutral" hidden></p>

        <div class="konto-oauth" data-konto-oauth-options hidden></div>
        <div class="konto-divider" data-konto-email-divider hidden><span>oder</span></div>

        <form class="konto-form konto-email-auth" data-konto-email-auth>
            <label>
                <span class="visually-hidden">E-Mail-Adresse</span>
                <input type="email" name="email" autocomplete="email" required placeholder="E-Mail-Adresse" />
            </label>
            <button class="btn-primary" type="submit">Weiter</button>
        </form>
    </article>

    <article class="card konto-card konto-account-card" data-requires-supabase data-auth-view="signed-in recovery" hidden>
        <div class="card-header">
            <span class="card-title" data-konto-account-card-title></span>
        </div>
        <p class="konto-card__hint" data-konto-profile-summary></p>
        <p class="konto-card__notice" data-konto-notice data-tone="neutral" hidden></p>

        <div class="konto-card__actions" data-konto-normal-only>
            <button class="btn-primary" type="button" data-konto-signout>Abmelden</button>
        </div>

        <p class="konto-card__hint" data-konto-password-card-copy></p>
        <form class="konto-form" data-konto-password-update>
            <label>
                <span>Neues Passwort</span>
                <input type="password" name="password" autocomplete="new-password" required minlength="6" />
            </label>
            <label>
                <span>Neues Passwort wiederholen</span>
                <input type="password" name="password_confirm" autocomplete="new-password" required minlength="6" />
            </label>
            <button class="btn-primary" type="submit">Passwort aktualisieren</button>
        </form>

        <form class="konto-form konto-delete-form" data-konto-delete data-konto-normal-only>
            <p class="konto-card__hint">Diese Aktion löscht dein Konto und die damit verbundenen MatheChecks-Daten dauerhaft.</p>
            <label>
                <span>Zur Bestätigung LÖSCHEN eingeben</span>
                <input type="text" name="confirmation" autocomplete="off" required />
            </label>
            <button class="btn-ghost konto-danger-button" type="submit">Konto löschen</button>
        </form>
    </article>
</div>
