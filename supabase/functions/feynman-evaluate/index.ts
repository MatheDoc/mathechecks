// Minimaler Proxy fuer die KI-Bewertung von Feynman-Erklaerungen.
//
// Zweck: haelt den Gemini-API-Key ausschliesslich serverseitig und bewertet
// gebuendelt, ob Schuelererklärungen zu konkreten Teilfragen den fachlichen
// Loesungsweg tragfaehig beschreiben. Die Function wird nur mit gueltigem
// Supabase-Session-JWT aufgerufen.

const MODELS = [
  "gemini-3.8-flash",
  "gemini-3.7-flash",
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
  evaluateNrs: number[];
};

function normalizeStringArray(value: unknown, maxLength: number): string[] {
  if (!Array.isArray(value)) return [];
  return value.map((item) => truncate(item, maxLength)).filter((item) => item.trim());
}

function buildPrompt(context: PromptContext): string {
  return `Du bewertest Schülererklärungen in einer Mathematik-Feynman-Übung.

# Ziel der Übung
Die Schüler bekommen eine konkrete Aufgabe und sollen im Feynman-Stil in eigenen Worten erklären, WIE man die Teilfrage löst. Im Mittelpunkt steht der Lösungsweg: die fachlich notwendigen Denk- und Rechenschritte, die zentralen Begriffe, Bedingungen und Begründungen. Eine gute Erklärung beschreibt nicht nur, welche Formel oder welches Verfahren verwendet wird, sondern auch, welche konkreten Schritte durchgeführt werden und warum diese zum Ziel führen, sofern dies für die Teilfrage wesentlich ist.

Bewertet wird, ob der Schüler den mathematischen Gedankengang verstanden hat, nicht ob seine Erklärung der internen Zielantwort möglichst ähnlich formuliert ist. Eine bloße richtige Endantwort ist keine Erklärung und erhält keine Punkte. Ein konkretes Endergebnis darf genannt werden, ist aber nicht erforderlich und darf bei einem vollständigen, korrekten Lösungsweg niemals zu einem Punktabzug führen. Eine Erklärung ohne Endwert kann die volle Punktzahl erreichen.

Die Texte entstehen oft per Diktat: Sprach-, Tipp- oder Diktierfehler sind möglich und zählen nicht als fachliche Fehler.

# Bewertungsgrundsätze
1. Maßgeblich ist die sichtbare Aufgabenstellung. Für Form, Darstellung und Lösungsweg ist die interne Zielantwort nur eine fachliche Orientierung, kein zwingendes Antwortformat.
2. Nennt die Erklärung einen konkreten numerischen Wert, gleiche ihn mit der internen Zielantwort ab. Dezimalkomma und Dezimalpunkt sind gleichwertig; sinnvolle Rundungen gelten als korrekt. Ein Wert, der nicht zufällig der internen Zielantwort entspricht, darf nicht als falsch bezeichnet werden. Weicht ein genannter Wert von der Zielantwort ab, weise knapp darauf hin.
3. Erfinde keine eigenen Vergleichswerte: Jede Zahl, die du in deiner Begründung als richtig oder falsch einstufst, muss aus Zielantwort, Einleitung, Visualisierung oder Referenzbeispiel stammen. Rechne keine eigene "richtige Lösung" aus, die diesen Daten widerspricht.
4. Akzeptiere mathematisch äquivalente Darstellungen, wenn die Aufgabe keine bestimmte Form verlangt, z. B. Normalform, Produktform, Scheitelpunktform, äquivalente Terme oder äquivalente Wahrscheinlichkeitsausdrücke.
5. Akzeptiere äquivalente Verfahren, wenn die Aufgabe kein bestimmtes Verfahren verlangt, z. B. Scheitelpunkt statt Ableitungsbedingung, Ableitungsweg statt Scheitelpunktform, grafische Begründung oder sinnvoll umgestellte Standardformeln.
6. Akzeptiere konsistent vertauschte Differenzen in Quotienten, z. B. bei mittleren Änderungsraten oder Steigungen: (f(a)-f(b))/(a-b) ist äquivalent zu (f(b)-f(a))/(b-a). Werte nicht als Vorzeichenfehler, wenn Zähler und Nenner gemeinsam umgekehrt wurden.
7. Akzeptiere rückwärts verwendete Beziehungen, z. B. die Pfadmultiplikationsregel in einem Baumdiagramm durch Division nach einer fehlenden Astwahrscheinlichkeit umzustellen.
8. Wenn Lernende sichtbare Nummern, Punkte, Äste oder Tabellenfelder aus Graphen, Baumdiagrammen oder Vierfeldertafeln nennen, interpretiere diese mithilfe von Einleitung, Visualisierung und Generator-Kontext. Werte nicht allein deshalb ab, weil ein formaler Name fehlt.
9. Das Referenzbeispiel dient nur der Orientierung: Die tatsächliche Aufgabe hat andere Zahlenwerte und gegebenenfalls ein anderes Szenario. Bewerte niemals gegen die Zahlen oder das Szenario des Referenzbeispiels. Akzeptiere auch Lösungswege, die vom Referenzbeispiel abweichen, solange sie fachlich korrekt zur gestellten Aufgabe passen.
10. Verlange eine bestimmte Form oder Methode nur, wenn sie in Einleitung oder Teilfrage ausdrücklich gefordert ist.
11. Vergib keine Punkte allein für eine richtige Zahl, einen Term, einen Fachbegriff oder ein bloßes "ja" bzw. "nein". Das gilt auch dann, wenn die Antwort offensichtlich der Zielantwort entspricht. Fordere stattdessen knapp eine Begründung anhand der Aufgabe ein.
12. Für eine hohe Bewertung muss mindestens die fachliche Kernidee des Lösungswegs genannt werden, sofern nach Regel 13 überhaupt ein Lösungsweg erforderlich ist. Allgemeine Aussagen wie „ich rechne das aus“, „ich setze etwas ein“, „ich benutze die Formel“ oder bloße Fachbegriffe ohne Erläuterung reichen nicht aus.
13. Ein vollständiger Rechenweg ist nicht erforderlich, wenn sich die Antwort unmittelbar und ohne Zwischenschritt aus einer gegebenen Darstellung ergibt, z. B. ein Parameter, der in der gegebenen Funktionsform bereits sichtbar ist, ein Wert, der direkt aus Graph, Tabelle, Baumdiagramm oder Vierfeldertafel abgelesen werden kann oder eine Angabe, die wörtlich im Aufgabentext steht. In diesem Fall genügt es, dass der Schüler kurz erklärt, woraus der Wert unmittelbar entnommen wird oder warum kein weiterer Schritt erforderlich ist. In diesem Fall besteht die nach Regel 12 geforderte Kernidee bereits aus diesem knappen Quellenbezug; ein bloßer Zahlenwert oder das bloße Abschreiben einer Aufgabenangabe ohne jeden Bezug zur Quelle bleibt unzureichend.
14. Fachlich falsche Zusatzbehauptungen zum Lösungsweg selbst (z. B. falsche Bedingungen, falsche Regeln, falsche Begriffe) mindern den Score auch dann, wenn andere Teile der Erklärung korrekt sind. Eine ansonsten korrekte Erklärung erhält keine volle Punktzahl, wenn sie zusätzlich wesentliche fachliche Fehler enthält. Ein rein rechnerischer Fehler im genannten Endergebnis bei sonst korrekt beschriebenem Weg fällt nicht darunter (siehe Regel 2 und die Hinweise zum Endergebnis oben).

# Kalibrierungsbeispiele (unabhängig von der aktuellen Aufgabe)
Beispiel A, Score 1.0: Teilfrage verlangt einen Tiefpunkt. Erklärung: "Ich setze die erste Ableitung gleich null und löse nach x auf. Dann prüfe ich mit der zweiten Ableitung: ist sie dort positiv, liegt ein Tiefpunkt vor. Den y-Wert bekommt man durch Einsetzen in f." Kein Endwert genannt, aber der Weg ist vollständig, korrekt und verständlich.

Beispiel B, Score 0.8: Teilfrage verlangt eine mittlere Änderungsrate. Erklärung: "Man rechnet die Differenz der Funktionswerte durch die Differenz der x-Werte." Kernidee korrekt, aber es fehlt der Hinweis, welche Stellen verwendet werden.

Beispiel C, Score 0.5: Teilfrage verlangt eine Pfadwahrscheinlichkeit aus einem Baumdiagramm. Erklärung: "Man multipliziert einfach die Wahrscheinlichkeiten." Richtiger Kerngedanke, aber es fehlt, welche Äste gemeint sind und warum multipliziert wird.

Beispiel D, Score 0.0: Teilfrage verlangt einen Hochpunkt. Erklärung: "f''(x)=0 setzen, und wenn f'''(x)>0 ist, ist es ein Hochpunkt." Die mathematischen Bedingungen sind falsch.

Beispiel E, Score 1.0: Teilfrage verlangt einen Angebots- oder Nachfrageüberschuss. Erklärung: "Den festgelegten Preis in Angebots- und Nachfragefunktion einsetzen, die Mengen vergleichen und die Differenz bilden. Ist die Nachfrage größer, liegt ein Nachfrageüberschuss vor, sonst ein Angebotsüberschuss." Kein Zahlenwert genannt, aber Rechenweg, Vergleich und Deutung sind vollständig.

Beispiel F, Score 0.0: Teilfrage fragt, ob eine Zufallsgröße binomialverteilt ist. Erklärung: "Ja." Die Antwort kann richtig sein, erklärt aber keine der erforderlichen Bedingungen.

Beispiel G, Score 1.0: Teilfrage verlangt den y-Achsenabschnitt von f(x)=2x+5. Erklärung: "Die Funktion steht schon in der Form y=mx+b da, der y-Achsenabschnitt ist die Zahl ohne x, also b. Das kann ich direkt ablesen." Kein Rechenweg nötig, da der Wert unmittelbar aus der gegebenen Form entnommen werden kann und der Bezug erklärt wird.

Beispiel H, Score 0.0: Gleiche Teilfrage wie in Beispiel G. Erklärung: "5." Der Wert ist zwar korrekt, aber es fehlt jeder Bezug dazu, warum dieser Wert direkt übernommen werden kann.

Beispiel I, Score 0.8: Teilfrage verlangt einen Hochpunkt. Erklärung: "Ich setze die erste Ableitung gleich null und prüfe mit der zweiten Ableitung, ob sie negativ ist – dann liegt ein Hochpunkt vor. Außerdem muss die Funktion dafür immer monoton steigend sein." Der Grundweg ist korrekt, aber die angehängte Zusatzbedingung zur Monotonie ist fachlich falsch und mindert den Score trotz sonst richtigem Kerngedanken.

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
${context.items
  .map(
    (item) =>
      `Teilfrage ${item.nr}${context.evaluateNrs.includes(item.nr) ? " [BEWERTEN]" : " [NUR KONTEXT]"}: ${item.frage}\nInterne Zielantwort: ${item.zielantwort || "(keine Zielantwort)"}\nSchülererklärung: ${item.schueler_antwort || "(leer)"}`
  )
  .join("\n\n")}

# Bewertung
Bewerte ausschließlich die mit [BEWERTEN] markierten Schülererklärungen. Die übrigen Erklärungen dienen nur als Kontext, damit Zusammenhänge zwischen Teilfragen berücksichtigt werden können. Gib für [NUR KONTEXT] markierte Teilfragen kein Ergebnis aus.

Zu bewertende Teilfragen: ${context.evaluateNrs.join(", ")}

Bewerte diese Schülererklärungen danach, ob sie den Lösungsweg im Feynman-Stil fachlich sinnvoll erklären oder – falls kein Rechenweg nötig ist – ob sie den direkten Bezug zur Quelle des Werts nennen (siehe Regel 13).

Nutze diese Score-Skala als Anker; auch passende Zwischenwerte sind ausdrücklich erlaubt. Verwende Zwischenwerte (z. B. 0.2, 0.3, 0.6 oder 0.9), wenn sie die Qualität der Erklärung besser treffen als die vier Ankerwerte.

- 1.0: sehr gut erklärt; zentrale Schritte, Begriffe und Begründung sind korrekt (oder: Wert korrekt direkt abgelesen mit benanntem Bezug zur Quelle, wenn kein Rechenweg nötig ist)
- 0.8: im Kern gut; kleine Ungenauigkeit oder eine kleine Lücke
- 0.5: teilweise brauchbar; ein zentraler Schritt, Begriff oder Zusammenhang fehlt
- 0.0: fachlich falsch, kaum verwertbar oder leer

Sei streng bei falschen mathematischen Bedingungen, vertauschten Begriffen, falschen Formeln oder fehlendem Kernschritt. Eine kurze oder alltagssprachliche Erklärung ist nur dann ausreichend, wenn sie mindestens einen konkreten Lösungs-, Begründungs- oder Bedingungsschritt enthält oder – gemäß Regel 13 – knapp erklärt, woraus ein Wert unmittelbar entnommen wird. Der Aufgaben- und Visualisierungskontext darf einen fehlenden Erklärschritt nicht ersetzen.

Bewerte nicht die Anzahl genannter Fachbegriffe oder Einzelschritte, sondern ob die Erklärung den mathematischen Gedankengang verständlich macht. Teilweise richtige Erklärungen sollen entsprechend ihres fachlichen Gehalts bewertet werden. Allgemeine Aussagen ohne mathematischen Inhalt genügen nicht.

Ein fehlendes Endergebnis oder ein fehlender konkreter Zahlenwert ist keine Lücke und darf bei vollständig beschriebenem, korrektem Lösungsweg nicht zu einer Reduzierung des Scores führen. Verrate bei schwachen Antworten nicht die komplette Zielantwort, sondern gib einen kurzen Hinweis, was nachgebessert werden sollte. Nutze exakt die angegebenen Teilfragenummern.

Prüfe vor dem Antworten jede Begründung: Nennt sie einen Zahlenwert, sollte dieser mit der internen Zielantwort oder den Kontextdaten übereinstimmen. Widerspricht deine Begründung der internen Zielantwort, verwirf sie und bewerte neu.

Antworte NUR mit einem JSON-Array:
[{"nr":1,"score":0.0,"reason":"kurzer deutscher Hinweis, höchstens 18 Wörter"}]`;
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
      // 429 nicht auf weitere Modelle durchreichen, sonst belastet ein Klick mehrere Quoten.
      if (error instanceof GeminiHttpError && error.status === 429) break;
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
      reason: emptyAnswer ? "Schreibe zuerst eine eigene Erklärung." : entry ? truncate(entry?.reason, 180) : "keine Bewertung erhalten",
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

  const availableNrs = new Set(rawItems.map((_, index) => index + 1));
  const requestedNrs = Array.isArray(body?.evaluateNrs)
    ? body.evaluateNrs.map(Number).filter((nr) => Number.isInteger(nr) && availableNrs.has(nr))
    : Array.from(availableNrs);
  const evaluateNrs = Array.from(new Set(requestedNrs));
  if (evaluateNrs.length === 0) {
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
    evaluateNrs,
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

  const evaluationItems = context.items.filter((item) => evaluateNrs.includes(item.nr));
  // Leere Antworten kosten keine Gemini-Tokens: direkt mit Score 0 beantworten.
  const emptyItems = evaluationItems.filter((item) => !item.schueler_antwort.trim());
  const geminiItems = evaluationItems.filter((item) => item.schueler_antwort.trim());

  for (const item of emptyItems) {
    normalized.push({ nr: item.nr, score: 0, reason: "Schreibe zuerst eine eigene Erklärung.", unchecked: false });
  }

  for (const items of chunkItems(geminiItems, GEMINI_BATCH_SIZE)) {
    const batchContext = { ...context, evaluateNrs: items.map((item) => item.nr) };
    const { results, modelUsed, lastError } = await evaluateWithFallback(apiKey, batchContext);

    if (!Array.isArray(results)) {
      const publicError = publicGeminiError(lastError);
      return jsonResponse(publicError, publicError.status === 429 || publicError.status === 503 ? publicError.status : 502);
    }

    usedModels.add(modelUsed);
    normalized.push(...normalizeBatchResults(items, results as Record<string, unknown>[]));
  }

  normalized.sort((a, b) => Number(a.nr) - Number(b.nr));

  return jsonResponse({ results: normalized, model: Array.from(usedModels).join(",") || MODELS[0] });
});
