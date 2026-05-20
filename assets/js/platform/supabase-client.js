const SUPABASE_CDN_URL = "https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/+esm";

let clientPromise = null;

function readRuntimeConfig() {
  const runtimeConfig = window.MatheChecksSupabase || {};
  const url = String(runtimeConfig.url || "").trim();
  const anonKey = String(runtimeConfig.anonKey || "").trim();
  const accountPath = String(runtimeConfig.accountPath || "/konto.html").trim() || "/konto.html";
  const oauthProviders = Array.isArray(runtimeConfig.oauthProviders)
    ? runtimeConfig.oauthProviders.map((provider) => String(provider || "").trim().toLowerCase()).filter(Boolean)
    : [];

  return {
    url,
    anonKey,
    accountPath,
    oauthProviders,
    configured: Boolean(url && anonKey),
  };
}

function normalizeRelativeAppPath(path) {
  const trimmed = String(path || "").trim();
  return trimmed.startsWith("/") ? trimmed : "";
}

export function getSupabaseRuntimeConfig() {
  return readRuntimeConfig();
}

export function buildAccountUrl(nextPath = "") {
  const { accountPath } = readRuntimeConfig();
  const url = new URL(accountPath, window.location.origin);
  const normalizedNextPath = normalizeRelativeAppPath(nextPath);

  if (normalizedNextPath) {
    url.searchParams.set("next", normalizedNextPath);
  }

  return url.toString();
}

export async function getSupabaseClient() {
  if (!clientPromise) {
    clientPromise = (async () => {
      const config = readRuntimeConfig();
      if (!config.configured) {
        return null;
      }

      const supabaseModule = await import(`${SUPABASE_CDN_URL}?v=20260514-auth-shell`);
      return supabaseModule.createClient(config.url, config.anonKey, {
        auth: {
          persistSession: true,
          autoRefreshToken: true,
          detectSessionInUrl: true,
        },
      });
    })();
  }

  return clientPromise;
}

export async function getCurrentAuthState() {
  const config = readRuntimeConfig();
  if (!config.configured) {
    return {
      configured: false,
      session: null,
      user: null,
      error: null,
    };
  }

  try {
    const supabase = await getSupabaseClient();
    if (!supabase) {
      return {
        configured: false,
        session: null,
        user: null,
        error: null,
      };
    }

    const { data: sessionData, error: sessionError } = await supabase.auth.getSession();

    if (sessionError) {
      return {
        configured: true,
        session: null,
        user: null,
        error: sessionError,
      };
    }

    const session = sessionData?.session || null;
    if (!session) {
      return {
        configured: true,
        session: null,
        user: null,
        error: null,
      };
    }

    const { data: userData, error: userError } = await supabase.auth.getUser();

    return {
      configured: true,
      session,
      user: userData?.user || session.user || null,
      error: userError || null,
    };
  } catch (error) {
    return {
      configured: true,
      session: null,
      user: null,
      error,
    };
  }
}

export function formatAuthDisplayName(user) {
  if (!user) return "";

  const displayName = String(user.user_metadata?.display_name || "").trim();
  if (displayName) return displayName;

  const fullName = String(user.user_metadata?.full_name || "").trim();
  if (fullName) return fullName;

  const email = String(user.email || "").trim();
  if (email) return email;

  return "Profil";
}
