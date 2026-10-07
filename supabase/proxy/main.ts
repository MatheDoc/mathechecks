// Reverse Proxy für die Supabase-API unter einer eigenen Domain (z. B. api.mathechecks.de).
// Hintergrund: Manche Schulnetze blockieren *.supabase.co per DNS-Filter.
// Deployment und DNS-Einrichtung: siehe supabase/proxy/README.md

const UPSTREAM = (Deno.env.get("SUPABASE_UPSTREAM_URL") ?? "https://ysqpmtreljfdwtlvjzis.supabase.co")
  .replace(/\/+$/, "");

const ALLOWED_PATH_PREFIXES = ["/auth/v1/", "/rest/v1/", "/functions/v1/", "/storage/v1/"];

const STRIPPED_REQUEST_HEADERS = [
  "host",
  "connection",
  "keep-alive",
  "te",
  "trailer",
  "transfer-encoding",
  "upgrade",
  "accept-encoding",
  "x-forwarded-for",
  "x-forwarded-host",
  "x-forwarded-proto",
  "x-real-ip",
];

// Deno-fetch entpackt Antworten automatisch, behält aber diese Header bei.
const STRIPPED_RESPONSE_HEADERS = [
  "content-encoding",
  "content-length",
  "transfer-encoding",
  "connection",
  "keep-alive",
];

export async function handleRequest(request: Request, clientIp = ""): Promise<Response> {
  const incomingUrl = new URL(request.url);

  if (incomingUrl.pathname === "/" || incomingUrl.pathname === "/health") {
    return new Response("ok", { status: 200, headers: { "content-type": "text/plain" } });
  }

  if (!ALLOWED_PATH_PREFIXES.some((prefix) => incomingUrl.pathname.startsWith(prefix))) {
    return new Response("Not found", { status: 404 });
  }

  const headers = new Headers(request.headers);
  for (const name of STRIPPED_REQUEST_HEADERS) {
    headers.delete(name);
  }
  if (clientIp) {
    headers.set("x-forwarded-for", clientIp);
  }

  const hasBody = request.method !== "GET" && request.method !== "HEAD";

  let upstreamResponse: Response;
  try {
    upstreamResponse = await fetch(`${UPSTREAM}${incomingUrl.pathname}${incomingUrl.search}`, {
      method: request.method,
      headers,
      body: hasBody ? await request.arrayBuffer() : undefined,
      redirect: "manual",
    });
  } catch (error) {
    console.error("Upstream nicht erreichbar:", error);
    return new Response(JSON.stringify({ message: "Upstream nicht erreichbar" }), {
      status: 502,
      headers: { "content-type": "application/json", "access-control-allow-origin": "*" },
    });
  }

  const responseHeaders = new Headers(upstreamResponse.headers);
  for (const name of STRIPPED_RESPONSE_HEADERS) {
    responseHeaders.delete(name);
  }

  return new Response(upstreamResponse.body, {
    status: upstreamResponse.status,
    statusText: upstreamResponse.statusText,
    headers: responseHeaders,
  });
}

if (import.meta.main) {
  Deno.serve((request, info) => {
    const remote = info.remoteAddr as Deno.NetAddr;
    return handleRequest(request, remote?.hostname ?? "");
  });
}
