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

const MODELS = [
  "gemini-3.6-flash",
  "gemini-3.5-flash",
  "gemini-3.5-flash-lite",
  "gemini-3.1-flash-lite",
] as const;
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
  return `Du bewertest Schülerantworten in einer Mathematik-Recall-Übung.

Kontext: Den Schülern wurde ein Hinweis gezeigt, z. B. ein Symbol, eine Formel oder ein Schritt eines Prozesses. Sie sollen dazu die passende Bedeutung/Bedingung/Aussage aus dem Gedächtnis in ein Textfeld eingeben - teilweise per Spracheingabe diktiert. Erwarte daher KEINE LaTeX-Syntax in der Schülerantwort, sondern natürlichsprachliche oder umgangssprachlich-mathematische Formulierungen (z. B. "f Strich von x Null gleich Null" für f'(x_0)=0, oder "p mal eins minus p" für p(1-p)).

Bewerte für jedes Item, ob die Schülerantwort die fachliche Kernaussage der erwarteten Antwort trifft. Nutze diese Score-Skala als Anker:
- 1.0: fachlich korrekt und vollständig, gemessen an der erwarteten Antwort
- 0.8: im Kern richtig, kleine Ungenauigkeit oder Lücke
- 0.5: teilweise richtig, ein wichtiger Teil fehlt oder ist ungenau
- 0.0: falsch, keine Aussage erkennbar, oder keine Antwort

Wichtige Bewertungsgrundsätze:
- Die erwartete Antwort definiert den Maßstab für Umfang und Detailtiefe. Verlange niemals mehr Detail, als die erwartete Antwort selbst enthält. Ist die erwartete Antwort nur ein Stichwort oder der Name einer Formel (z. B. "Erwartungswert-Formel"), genügt es vollständig, wenn die Schülerantwort dieses Stichwort sinngemäß nennt.
- Enthält die erwartete Antwort Alternativen (z. B. "Gleichsetzungs- oder Einsetzungsverfahren"), genügt es vollständig, EINE davon zu nennen.
- Sinngemäße Formulierungen und Synonyme zählen als Treffer (z. B. "lösen" statt "berechnen", "ausrechnen" statt "bestimmen"). Bestandteile, die durch den gezeigten Hinweis (Cue) oder den Satzzusammenhang offensichtlich impliziert sind, gelten als abgedeckt und dürfen nicht als fehlend gewertet werden.
- Zusätzliche Angaben, die fachlich korrekt oder neutral sind (z. B. ein Bezug zum Aufgabenkontext), werten die Antwort NICHT ab. Nur fachlich falsche Zusätze senken den Score.
- Toleriere umgangssprachliche Schreibweise, Diktier- und Spracherkennungsfehler sowie andere Variablennamen bei gleicher Struktur.
- Bewerte streng bei fehlenden zentralen Bestandteilen der erwarteten Antwort oder bei Verwechslung von Symbolen/Bedingungen.

Kalibrierungsbeispiele (unabhängig von den aktuellen Items):
- Erwartet: "fehlende Werte mit Gleichsetzungs- oder Einsetzungsverfahren berechnen". Schüler: "die zwei Gleichungen kann man mit dem Einsetzungsverfahren lösen". Score 1.0: eine Alternative genannt, "lösen" ist sinngemäß "berechnen", der Rest ist durch den Cue impliziert.
- Erwartet: "Summe aller Wahrscheinlichkeiten = 1". Schüler: "Summe aller Wahrscheinlichkeiten ergibt 1, mit 2 Unbekannten". Score 1.0: Kernaussage exakt getroffen, der Zusatz ist korrekt und wertet nicht ab.
- Erwartet: "f'(x_0) = 0 und f''(x_0) < 0". Schüler: "erste Ableitung gleich null setzen". Score 0.5: die zweite Bedingung fehlt vollständig.
- Erwartet: "f'(x_0) = 0 und f''(x_0) < 0". Schüler: "f zwei Strich gleich null und f drei Strich größer null". Score 0.0: die Bedingung ist fachlich falsch.

Schreibe "reason" als vollständigen, kurzen deutschen Satz. Bei score < 0.8 soll "reason" ein hilfreicher Hinweis sein, aber NICHT die erwartete Antwort verraten. Zitiere die erwartete Antwort nicht. Nenne stattdessen knapp, welche Art von Bestandteil fehlt oder in welche Richtung der Schüler denken soll.

Eingabedaten:
${JSON.stringify(payload, null, 2)}

Antworte NUR mit einem JSON-Array:
[{"nr": 1, "score": 0.0, "reason": "vollständiger Hinweis, höchstens 18 Wörter"}]`;
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
      generationConfig: { temperature: 0.1, maxOutputTokens: 2048, responseMimeType: "application/json" },
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
  let modelUsed: string = MODELS[0];
  let lastError: unknown = null;

  for (const model of MODELS) {
    try {
      results = await callGemini(apiKey, model, payload);
      modelUsed = model;
      break;
    } catch (error) {
      lastError = error;
      const status = error instanceof GeminiHttpError ? error.status : 0;
      if (status === 429) {
        break;
      }
      continue;
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
