const MAX_BODY_BYTES = 4096;

const RESPONSE_BODY = Object.freeze({
  accepted: true,
  body_stored: false,
  message: "Request accepted. The mock endpoint does not store or process the JSON body.",
});

const RESPONSE_HEADERS = Object.freeze({
  "Cache-Control": "no-store",
  "Content-Type": "application/json; charset=utf-8",
  "Referrer-Policy": "no-referrer",
  "X-Content-Type-Options": "nosniff",
});

export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (url.pathname !== "/v1/collect.json") {
      return jsonResponse({ accepted: false, error: "not_found" }, 404);
    }
    if (request.method !== "POST") {
      return jsonResponse(
        { accepted: false, error: "method_not_allowed" },
        405,
        { Allow: "POST" },
      );
    }
    if (!isJSON(request.headers.get("Content-Type"))) {
      return jsonResponse(
        { accepted: false, error: "content_type_must_be_application_json" },
        415,
      );
    }
    if (!(await bodyFits(request, MAX_BODY_BYTES))) {
      return jsonResponse({ accepted: false, error: "body_too_large" }, 413);
    }

    // Intentionally do not parse, store, log, identify, or forward the body.
    // The allowlisted query dimensions remain available for aggregate edge
    // counts while the future collector is not implemented.
    return jsonResponse(RESPONSE_BODY, 202);
  },
};

function isJSON(contentType) {
  return (contentType || "").split(";", 1)[0].trim().toLowerCase() === "application/json";
}

async function bodyFits(request, maxBytes) {
  const declared = request.headers.get("Content-Length");
  if (declared !== null) {
    const bytes = Number(declared);
    return Number.isInteger(bytes) && bytes >= 0 && bytes <= maxBytes;
  }
  if (!request.body) return true;

  const reader = request.body.getReader();
  let bytes = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) return true;
      bytes += value.byteLength;
      if (bytes > maxBytes) {
        await reader.cancel("body too large");
        return false;
      }
    }
  } finally {
    reader.releaseLock();
  }
}

function jsonResponse(value, status, extraHeaders = {}) {
  return new Response(`${JSON.stringify(value)}\n`, {
    status,
    headers: { ...RESPONSE_HEADERS, ...extraHeaders },
  });
}
