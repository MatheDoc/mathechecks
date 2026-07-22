// Minimaler Proxy fuer die KI-Bewertung von Feynman-Erklaerungen.
//
// Zweck: haelt den Gemini-API-Key ausschliesslich serverseitig und bewertet
// gebuendelt, ob Schuelererklärungen zu konkreten Teilfragen den fachlichen
// Loesungsweg tragfaehig beschreiben. Die Function wird nur mit gueltigem
// Supabase-Session-JWT aufgerufen.

const MODELS = [
  "gemini-3.6-flash",
  "gemini-3.5-flash",
  "gemini-3.5-flash-lite",
  "gemini-3.1-flash-lite",
] as const;
const RATE_LIMIT_SCOPE = "feynman_evaluate";
const MAX_ITEMS = 24;
const GEMINI_BATCH_SIZE = 6;
const MAX_FIELD_LENGTH = 1200;
const MAX_CONTEXT_LENGTH = 6400;

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

type PromptItem = {
  nr: number;
  frage: string;
  zielantwort: string;
  schueler_antwort: string;
};

type PromptContext = {
  check: {
    schlagwort: string;
    lernbereich: string;
    kompetenz: string;
    tipps: string[];
  };
  task: {
    einleitung: string;
    visualContext: string;
    fragen: string[];
    zielantworten: string[];
    beispiel: string;
  };
  items: PromptItem[];
};

function normalizeStringArray(value: unknown, maxLength: number): string[] {
  if (!Array.isArray(value)) return [];
  return value.map((item) => truncate(item, maxLength)).filter((item) => item.trim());
}

function buildPrompt(context: PromptContext): string {
  return `Du bewertest Schülererklärungen in einer Mathematik-Feynman-Übung.

# Ziel der Übung
Die Schüler bekommen eine konkrete Aufgabe und sollen im Feynman-Stil in eigenen Worten erklären, WIE man die Teilfrage löst. Im Mittelpunkt steht der Rechenweg: die zentralen Schritte, Begriffe, Bedingungen und Begründungen. Ein konkretes Endergebnis darf genannt werden, ist aber nicht erforderlich und darf bei einem vollständigen, korrekten Lösungsweg niemals zu einem Punktabzug führen. Eine Erklärung ohne Endwert kann die volle Punktzahl erreichen. Die Texte entstehen oft per Diktat: Sprach-, Tipp- oder Diktierfehler sind möglich und zählen nicht als fachliche Fehler.

# Bewertungsgrundsätze
1. Maßgeblich ist die sichtbare Aufgabenstellung. Für Form, Darstellung und Lösungsweg ist die interne Zielantwort nur eine fachliche Orientierung, kein zwingendes Antwortformat.
2. Nennt die Erklärung einen konkreten numerischen Wert, gleiche ihn mit der internen Zielantwort ab. Dezimalkomma und Dezimalpunkt sind gleichwertig; sinnvolle Rundungen gelten als korrekt. Ein Wert, der der internen Zielantwort entspricht, darf niemals als falsch bezeichnet werden. Weicht ein genannter Wert von der Zielantwort ab, weise knapp darauf hin.
3. Erfinde keine eigenen Vergleichswerte: Jede Zahl, die du in deiner Begründung als richtig oder falsch einstufst, muss aus Zielantwort, Einleitung, Visualisierung oder Referenzbeispiel stammen. Rechne keine eigene "richtige Lösung" aus, die diesen Daten widerspricht.
4. Akzeptiere mathematisch äquivalente Darstellungen, wenn die Aufgabe keine bestimmte Form verlangt, z. B. Normalform, Produktform, Scheitelpunktform, äquivalente Terme oder äquivalente Wahrscheinlichkeitsausdrücke.
5. Akzeptiere äquivalente Verfahren, wenn die Aufgabe kein bestimmtes Verfahren verlangt, z. B. Scheitelpunkt statt Ableitungsbedingung, Ableitungsweg statt Scheitelpunktform, grafische Begründung oder sinnvoll umgestellte Standardformeln.
6. Akzeptiere konsistent vertauschte Differenzen in Quotienten, z. B. bei mittleren Änderungsraten oder Steigungen: (f(a)-f(b))/(a-b) ist äquivalent zu (f(b)-f(a))/(b-a). Werte nicht als Vorzeichenfehler, wenn Zähler und Nenner gemeinsam umgekehrt wurden.
7. Akzeptiere rückwärts verwendete Beziehungen, z. B. die Pfadmultiplikationsregel in einem Baumdiagramm durch Division nach einer fehlenden Astwahrscheinlichkeit umzustellen.
8. Wenn Lernende sichtbare Nummern, Punkte, Äste oder Tabellenfelder aus Graphen, Baumdiagrammen oder Vierfeldertafeln nennen, interpretiere diese mithilfe von Einleitung, Visualisierung und Generator-Kontext. Werte nicht allein deshalb ab, weil ein formaler Name fehlt.
9. Das Referenzbeispiel dient nur der Orientierung: Die tatsächliche Aufgabe hat andere Zahlenwerte und gegebenenfalls ein anderes Szenario. Bewerte niemals gegen die Zahlen oder das Szenario des Referenzbeispiels. Akzeptiere auch Lösungswege, die vom Referenzbeispiel abweichen, solange sie fachlich korrekt zur gestellten Aufgabe passen.
10. Verlange eine bestimmte Form oder Methode nur, wenn sie in Einleitung oder Teilfrage ausdrücklich gefordert ist.

# Kalibrierungsbeispiele (unabhängig von der aktuellen Aufgabe)
Beispiel A, Score 1.0: Teilfrage verlangt einen Tiefpunkt. Erklärung: "Ich setze die erste Ableitung gleich null und löse nach x auf. Dann prüfe ich mit der zweiten Ableitung: ist sie dort positiv, liegt ein Tiefpunkt vor. Den y-Wert bekommt man durch Einsetzen in f." Kein Endwert genannt, aber der Weg ist vollständig, korrekt und verständlich.
Beispiel B, Score 0.8: Teilfrage verlangt eine mittlere Änderungsrate. Erklärung: "Man rechnet die Differenz der Funktionswerte durch die Differenz der x-Werte." Kernidee korrekt, aber es fehlt der kleine Hinweis, welche Stellen eingesetzt werden.
Beispiel C, Score 0.5: Teilfrage verlangt eine Pfadwahrscheinlichkeit aus einem Baumdiagramm. Erklärung: "Man multipliziert einfach die Wahrscheinlichkeiten." Richtiger Kerngedanke, aber es fehlt, welche Äste gemeint sind und warum multipliziert wird.
Beispiel D, Score 0.0: Teilfrage verlangt einen Hochpunkt. Erklärung: "f''(x)=0 setzen, und wenn f'''(x)>0 ist, ist es ein Hochpunkt." Die Bedingung ist fachlich falsch (erste und zweite Ableitung verwechselt).
Beispiel E, Score 1.0: Teilfrage verlangt einen Angebots- oder Nachfrageüberschuss. Erklärung: "Den festgelegten Preis in Angebots- und Nachfragefunktion einsetzen, die Mengen vergleichen und die Differenz bilden. Ist die Nachfrage größer, liegt ein Nachfrageüberschuss vor, sonst ein Angebotsüberschuss." Kein Zahlenwert genannt, aber Rechenweg, Vergleich und Deutung sind vollständig.

# Check
Schlagwort: ${context.check.schlagwort}
Lernbereich: ${context.check.lernbereich}
Kompetenz: ${context.check.kompetenz}

# Hintergrundhinweise
${context.check.tipps.length ? context.check.tipps.map((tip) => `- ${tip}`).join("\n") : "(keine Tipps hinterlegt)"}

# Aufgabe
Einleitung:
${context.task.einleitung || "(keine Einleitung)"}

Visualisierung / Generator-Kontext:
${context.task.visualContext || "(keine Visualisierung)"}

Referenzbeispiel (nur Orientierung, andere Zahlen/Szenario möglich):
${context.task.beispiel || "(kein Referenzbeispiel)"}

# Teilfragen und interne Zielantworten
${context.items.map((item) => `Teilfrage ${item.nr}: ${item.frage}\nInterne Zielantwort: ${item.zielantwort || "(keine Zielantwort)"}\nSchülererklärung: ${item.schueler_antwort || "(leer)"}`).join("\n\n")}

# Bewertung
Bewerte jede Schülererklärung danach, ob sie den Lösungsweg im Feynman-Stil fachlich sinnvoll erklärt. Nutze diese Score-Skala als Anker:
- 1.0: sehr gut erklärt; zentrale Schritte, Begriffe und Begründung sind korrekt
- 0.8: im Kern gut; kleine Ungenauigkeit oder eine kleine Lücke
- 0.5: teilweise brauchbar; ein zentraler Schritt, Begriff oder Zusammenhang fehlt
- 0.0: fachlich falsch, kaum verwertbar oder leer

Sei streng bei falschen mathematischen Bedingungen, vertauschten Begriffen, falschen Formeln oder fehlendem Kernschritt. Ein fehlendes Endergebnis oder ein fehlender konkreter Zahlenwert ist KEINE Lücke und darf bei vollständig beschriebenem, korrektem Rechenweg nicht zu einem Score unter 1.0 führen. Sei ebenfalls fair, wenn eine kurze oder alltagssprachliche Erklärung durch den Aufgaben- und Visualisierungskontext eindeutig rekonstruierbar ist. Verrate bei schwachen Antworten nicht die komplette Zielantwort, sondern gib einen kurzen Hinweis, was nachgebessert werden sollte. Nutze exakt die angegebenen Teilfragenummern.

Prüfe vor dem Antworten jede Begründung: Nennt sie einen Zahlenwert, muss dieser mit der internen Zielantwort oder den Kontextdaten übereinstimmen. Widerspricht deine Begründung der internen Zielantwort, verwirf sie und bewerte neu.

Antworte NUR mit einem JSON-Array:
[{"nr": 1, "score": 0.0, "reason": "kurzer deutscher Hinweis, höchstens 18 Wörter"}]`;
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

async function consumeRateLimit(req: Request): Promise<{ allowed: boolean; status?: number; error?: string }> {
  const supabaseUrl = Deno.env.get("SUPABASE_URL")?.replace(/\/+$/, "") || "";
  const apiKey = req.headers.get("apikey") || Deno.env.get("SUPABASE_ANON_KEY") || "";
  const authorization = req.headers.get("authorization") || "";

  if (!supabaseUrl || !apiKey || !authorization) {
    return { allowed: false, status: 401, error: "not-authenticated" };
  }

  try {
    const response = await fetch(`${supabaseUrl}/rest/v1/rpc/consume_ai_rate_limit`, {
      method: "POST",
      headers: {
        Authorization: authorization,
        apikey: apiKey,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ p_scope: RATE_LIMIT_SCOPE }),
    });

    if (!response.ok) {
      if (response.status >= 500) return { allowed: true };
      return { allowed: false, status: response.status, error: "rate-limit-check-failed" };
    }

    const data = await response.json();
    return { allowed: data?.allowed !== false, status: data?.allowed === false ? 429 : 200, error: "rate-limited" };
  } catch {
    return { allowed: true };
  }
}

async function callGemini(apiKey: string, model: string, context: PromptContext): Promise<unknown> {
  const prompt = buildPrompt(context);
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;

  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      contents: [{ parts: [{ text: prompt }] }],
      generationConfig: { temperature: 0.1, maxOutputTokens: 3072, responseMimeType: "application/json" },
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

function chunkItems(items: PromptItem[], size: number): PromptItem[][] {
  const chunks: PromptItem[][] = [];
  for (let index = 0; index < items.length; index += size) {
    chunks.push(items.slice(index, index + size));
  }
  return chunks;
}

async function evaluateWithFallback(
  apiKey: string,
  context: PromptContext,
): Promise<{ results: unknown; modelUsed: string; lastError: unknown }> {
  let results: unknown = null;
  let modelUsed: string = MODELS[0];
  let lastError: unknown = null;

  for (const model of MODELS) {
    try {
      results = await callGemini(apiKey, model, context);
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

  return { results, modelUsed, lastError };
}

function normalizeBatchResults(items: PromptItem[], results: Record<string, unknown>[]): Record<string, unknown>[] {
  const byNr = new Map<number, Record<string, unknown>>();
  for (const entry of results) {
    const nr = Number(entry?.nr);
    if (Number.isFinite(nr)) byNr.set(nr, entry);
  }

  return items.map((item, index) => {
    const entry = byNr.get(item.nr) || results[index];
    const scoreRaw = Number(entry?.score);
    const emptyAnswer = item.schueler_antwort.trim().length === 0;
    const score = emptyAnswer ? 0 : Number.isFinite(scoreRaw) ? Math.max(0, Math.min(1, scoreRaw)) : 0;
    return {
      nr: item.nr,
      score,
      reason: emptyAnswer ? "Schreibe zuerst eine eigene Erklaerung." : entry ? truncate(entry?.reason, 180) : "keine Bewertung erhalten",
      unchecked: !entry && !emptyAnswer,
    };
  });
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: CORS_HEADERS });
  }

  if (req.method !== "POST") {
    return jsonResponse({ error: "method-not-allowed" }, 405);
  }

  let body: Record<string, unknown>;
  try {
    body = await req.json();
  } catch {
    return jsonResponse({ error: "invalid-json" }, 400);
  }

  const rawItems = Array.isArray(body?.items) ? body.items : [];
  if (rawItems.length === 0 || rawItems.length > MAX_ITEMS) {
    return jsonResponse({ error: "invalid-items", maxItems: MAX_ITEMS }, 400);
  }

  const checkRaw = body?.check && typeof body.check === "object" ? body.check as Record<string, unknown> : {};
  const taskRaw = body?.task && typeof body.task === "object" ? body.task as Record<string, unknown> : {};

  const context: PromptContext = {
    check: {
      schlagwort: truncate(checkRaw.schlagwort, 180),
      lernbereich: truncate(checkRaw.lernbereich, 180),
      kompetenz: truncate(checkRaw.kompetenz, 500),
      tipps: normalizeStringArray(checkRaw.tipps, 500).slice(0, 12),
    },
    task: {
      einleitung: truncate(taskRaw.einleitung, MAX_CONTEXT_LENGTH),
      visualContext: truncate(taskRaw.visualContext, MAX_CONTEXT_LENGTH),
      fragen: normalizeStringArray(taskRaw.fragen, MAX_FIELD_LENGTH).slice(0, MAX_ITEMS),
      zielantworten: normalizeStringArray(taskRaw.zielantworten, MAX_FIELD_LENGTH).slice(0, MAX_ITEMS),
      beispiel: truncate(taskRaw.beispiel, MAX_CONTEXT_LENGTH),
    },
    items: rawItems.map((item: Record<string, unknown>, index: number) => ({
      nr: index + 1,
      frage: truncate(item?.frage, MAX_FIELD_LENGTH),
      zielantwort: truncate(item?.zielantwort, MAX_FIELD_LENGTH),
      schueler_antwort: truncate(item?.schueler_antwort, MAX_FIELD_LENGTH),
    })),
  };

  const rateLimit = await consumeRateLimit(req);
  if (!rateLimit.allowed) {
    return jsonResponse({ error: rateLimit.error || "rate-limited" }, rateLimit.status || 429);
  }

  const apiKey = Deno.env.get("GEMINI_API_KEY");
  if (!apiKey) {
    return jsonResponse({ error: "not-configured" }, 500);
  }

  const normalized: Record<string, unknown>[] = [];
  const usedModels = new Set<string>();

  for (const items of chunkItems(context.items, GEMINI_BATCH_SIZE)) {
    const batchContext = { ...context, items };
    const { results, modelUsed, lastError } = await evaluateWithFallback(apiKey, batchContext);

    if (!Array.isArray(results)) {
      const publicError = publicGeminiError(lastError);
      return jsonResponse(publicError, publicError.status === 429 || publicError.status === 503 ? publicError.status : 502);
    }

    usedModels.add(modelUsed);
    normalized.push(...normalizeBatchResults(items, results as Record<string, unknown>[]));
  }

  return jsonResponse({ results: normalized, model: Array.from(usedModels).join(",") || MODELS[0] });
});
