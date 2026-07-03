// Minimaler Proxy fuer die KI-Bewertung von Recall-Antworten.
//
// Zweck: haelt den Gemini-API-Key ausschliesslich serverseitig (system secret
// GEMINI_API_KEY) und bewertet gebuendelt Cue/Response/Schuelerantwort-Items.
// Wird ausschliesslich von eingeloggten Nutzern ueber
// `/functions/v1/recall-evaluate`
// aufgerufen. Supabase prueft den JWT der Anfrage standardmaessig, bevor die
// Function ueberhaupt ausgefuehrt wird (kein `--no-verify-jwt` bei Deploy).
//
// Bewusst klein gehalten: kein Datenbankzugriff, kein eigener State, nur ein
// gebuendelter Aufruf an die Gemini API mit Modell-Fallback bei Servicefehlern.
// Quota-Fehler (429) werden nicht auf das naechste Modell durchgereicht, damit
// ein einzelner Recall-Klick nicht mehrere Modellquoten belastet.

const MODEL_PRIMARY = "gemini-3.1-flash-lite";
const MODEL_FALLBACK = "gemini-3.5-flash";
const MAX_ITEMS = 12;
const MAX_FIELD_LENGTH = 400;

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...CORS_HEADERS, "Content-Type": "application/json" },
  });
}

function truncate(value: unknown, maxLength: number): string {
  return String(value ?? "").slice(0, maxLength);
}

type PromptItem = { nr: number; cue: string; erwartete_antwort: string; schueler_antwort: string };

function buildPrompt(payload: PromptItem[]): string {
  return `Du bewertest Schuelerantworten in einer Mathematik-Recall-Uebung (Sekundarstufe/Berufskolleg).

Kontext: Den Schuelern wurde ein Hinweis ("cue") gezeigt, z.B. ein Symbol, eine Formel oder eine kurze Frage (kann auch leer sein, dann ist die Erinnerung "blind"). Sie sollen dazu die passende Bedeutung/Bedingung/Aussage aus dem Gedaechtnis in ein Textfeld eingeben - teilweise per Spracheingabe diktiert. Erwarte daher KEINE LaTeX-Syntax in der Schuelerantwort, sondern natuerlichsprachliche oder umgangssprachlich-mathematische Formulierungen (z.B. "f Strich von x Null gleich Null" fuer f'(x_0)=0, oder "p mal eins minus p" fuer p(1-p)).

Bewerte fuer jedes Item, ob die Schuelerantwort die fachliche Kernaussage der erwarteten Antwort trifft. Nutze diese Score-Skala als Anker:
- 1.0: fachlich vollstaendig korrekt und vollstaendig
- 0.8: im Kern richtig, kleine Ungenauigkeit oder Luecke
- 0.5: teilweise richtig, ein wichtiger Teil fehlt oder ist ungenau
- 0.0: falsch, keine Aussage erkennbar, oder keine Antwort

Toleriere umgangssprachliche/diktierte Schreibweise und andere Variablennamen bei gleicher Struktur. Bewerte STRENG bei fehlenden zentralen Bestandteilen oder Verwechslung von Symbolen/Bedingungen.
Schreibe "reason" als vollstaendigen, kurzen deutschen Satz. Bei score < 0.8 soll "reason" ein hilfreicher Hinweis sein, aber NICHT die erwartete Antwort verraten. Zitiere die erwartete Antwort nicht und verwende keine Formulierungen wie "Die erwartete Antwort ist ...". Nenne stattdessen knapp, welche Art von Bestandteil fehlt oder in welche Richtung der Schueler denken soll.

Eingabedaten:
${JSON.stringify(payload, null, 2)}

Antworte NUR mit einem JSON-Array, keine weiteren Erklaerungen, keine Markdown-Codebloecke:
[{"nr": 1, "score": 0.0, "reason": "vollstaendiger Hinweis, max 18 Woerter"}]`;
}

class GeminiHttpError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

function publicGeminiError(error: unknown): { error: string; status?: number } {
  if (error instanceof GeminiHttpError) {
    if (error.status === 429) return { error: "rate-limited", status: 429 };
    if (error.status === 503) return { error: "temporarily-unavailable", status: 503 };
    return { error: "evaluation-failed", status: error.status };
  }
  return { error: "evaluation-failed" };
}

async function callGemini(apiKey: string, model: string, payload: PromptItem[]): Promise<unknown> {
  const prompt = buildPrompt(payload);
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;

  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      contents: [{ parts: [{ text: prompt }] }],
      generationConfig: { temperature: 0.1, maxOutputTokens: 1024 },
    }),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new GeminiHttpError(response.status, `Gemini-Fehler (${response.status}): ${errorText.slice(0, 250)}`);
  }

  const data = await response.json();
  let text: string = data?.candidates?.[0]?.content?.parts?.[0]?.text || "";
  text = text.replace(/```json|```/g, "").trim();

  return JSON.parse(text);
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: CORS_HEADERS });
  }

  if (req.method !== "POST") {
    return jsonResponse({ error: "method-not-allowed" }, 405);
  }

  let body: { items?: unknown };
  try {
    body = await req.json();
  } catch {
    return jsonResponse({ error: "invalid-json" }, 400);
  }

  const rawItems = Array.isArray(body?.items) ? body.items : [];
  if (rawItems.length === 0 || rawItems.length > MAX_ITEMS) {
    return jsonResponse({ error: "invalid-items" }, 400);
  }

  const payload: PromptItem[] = rawItems.map((item: Record<string, unknown>, index: number) => ({
    nr: index + 1,
    cue: truncate(item?.cue, MAX_FIELD_LENGTH),
    erwartete_antwort: truncate(item?.response, MAX_FIELD_LENGTH),
    schueler_antwort: truncate(item?.student, MAX_FIELD_LENGTH),
  }));

  const apiKey = Deno.env.get("GEMINI_API_KEY");
  if (!apiKey) {
    return jsonResponse({ error: "not-configured" }, 500);
  }

  let results: unknown = null;
  let modelUsed = MODEL_PRIMARY;
  let lastError: unknown = null;

  for (const model of [MODEL_PRIMARY, MODEL_FALLBACK]) {
    try {
      results = await callGemini(apiKey, model, payload);
      modelUsed = model;
      break;
    } catch (error) {
      lastError = error;
      const status = error instanceof GeminiHttpError ? error.status : 0;
      if (status === 503) {
        continue;
      }
      break;
    }
  }

  if (!Array.isArray(results)) {
    const publicError = publicGeminiError(lastError);
    return jsonResponse(publicError, publicError.status === 429 || publicError.status === 503 ? publicError.status : 502);
  }

  const byNr = new Map<number, Record<string, unknown>>();
  for (const entry of results as Record<string, unknown>[]) {
    const nr = Number(entry?.nr);
    if (Number.isFinite(nr)) byNr.set(nr, entry);
  }

  const normalized = payload.map((item) => {
    const entry = byNr.get(item.nr);
    const scoreRaw = Number(entry?.score);
    const score = Number.isFinite(scoreRaw) ? Math.max(0, Math.min(1, scoreRaw)) : 0;
    return {
      nr: item.nr,
      score,
      reason: entry ? truncate(entry?.reason, 180) : "keine Bewertung erhalten",
      unchecked: !entry,
    };
  });

  return jsonResponse({ results: normalized, model: modelUsed });
});
