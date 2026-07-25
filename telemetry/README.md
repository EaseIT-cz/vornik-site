# telemetry.vornik.io mock endpoint

This directory is the repository-owned source for Vornik's anonymous
lifecycle-telemetry mock response.

The website remains GitHub Pages at `vornik.io`. GitHub Pages cannot accept
POST requests and the Pages site can have only its existing `vornik.io`
custom-domain configuration, so `telemetry.vornik.io/v1/collect.json` is
handled by a narrowly scoped Cloudflare Worker Route.

The Worker:

- accepts only `POST /v1/collect.json`;
- requires `Content-Type: application/json`;
- limits the body to 4 KiB;
- returns `response.json` with HTTP 202;
- does not parse, store, log, identify, or forward the body;
- sets `Cache-Control: no-store` and no cookies;
- leaves every other website path outside the configured Worker Route.

## Test

Node 20 or newer:

```bash
node --test telemetry/worker.test.mjs
```

## Manual Cloudflare setup

No Page Rule is required, and this repository does not use the Cloudflare API.

1. In **Workers & Pages**, create a Worker named `vornik-telemetry-mock`.
2. Paste `telemetry/worker.js` into the module editor and deploy it.
3. Under the Worker's **Settings → Domains & Routes**, add a route:
   - Zone: `vornik.io`
   - Route: `telemetry.vornik.io/v1/collect.json*`
4. Confirm the existing `telemetry` DNS record is proxied through Cloudflare.
5. Keep Worker observability/log collection disabled. Do not add Logpush,
   request-body logging, cookies, or visitor identifiers.
6. Test:

```bash
curl -i -X POST \
  -H 'Content-Type: application/json' \
  --data '{"schema_version":1,"event":"install_succeeded"}' \
  'https://telemetry.vornik.io/v1/collect.json?e=install_succeeded&sv=1&v=test&os=linux&arch=amd64&source=quickstart'
```

Expected: HTTP 202 and the JSON in `response.json`.

Only after this check and the IP/log-retention review pass should Vornik's
compile-time production-emission gate be enabled.
