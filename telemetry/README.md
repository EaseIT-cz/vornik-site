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

## Deploy the Worker

No Page Rule is required. There is no CI workflow or stored Cloudflare
credential in this repository. The optional Wrangler path uses your
interactive Cloudflare login to deploy the preview Worker; the dashboard path
does not require you to run a CLI.

The Cloudflare Pages/static uploader cannot deploy this directory because it
contains Worker JavaScript. Use either:

### Dashboard editor (no CLI)

1. In **Workers & Pages**, choose **Create → Worker → Start with Hello World**.
   Do not choose Pages, static asset upload, or repository asset upload.
2. Name it `vornik-telemetry-mock`, deploy the placeholder, then choose
   **Edit code**.
3. Replace the placeholder module with `telemetry/worker.js` and deploy.

### Wrangler

```bash
cd telemetry
npm install
npx wrangler login
WRANGLER_SEND_METRICS=false npm run deploy
```

`wrangler.jsonc` deliberately publishes only to the Worker's `workers.dev`
preview URL. It does not create or change a production route.
`WRANGLER_SEND_METRICS=false` disables Wrangler's own CLI usage telemetry for
this deployment.

## Add the production route manually

1. Under the Worker's **Settings → Domains & Routes**, add a route:
   - Zone: `vornik.io`
   - Route: `telemetry.vornik.io/v1/collect.json*`
2. Confirm the existing `telemetry` DNS record is proxied through Cloudflare.
3. Confirm **Observability** is disabled. Do not add Logpush,
   request-body logging, cookies, or visitor identifiers.
4. Test:

```bash
curl -i -X POST \
  -H 'Content-Type: application/json' \
  --data '{"schema_version":1,"event":"install_succeeded"}' \
  'https://telemetry.vornik.io/v1/collect.json?e=install_succeeded&sv=1&v=test&os=linux&arch=amd64&source=quickstart'
```

Expected: HTTP 202 and the JSON in `response.json`.

Only after this check and the IP/log-retention review pass should Vornik's
compile-time production-emission gate be enabled.
