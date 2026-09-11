# RustChain explorer test — 2026-09-11

Browser: Chromium/Playwright on Android/Termux environment, 1280×800 viewport.

Pages tested:

1. `https://rustchain.org/explorer/` — dashboard loads health/epoch, but miner table remains on `Loading miners...`; `GET /api/miners` itself returns HTTP 200 with a paginated object `{miners:[...], pagination:{...}}`. The deployed page JS still tests `miners.length` and then calls `miners.sort`, so the object response is never unwrapped. This reproduces the deployment regression tracked previously in closed RustChain #5614/#6211.
2. `https://rustchain.org/anchors` — the Explorer's `Ergo Anchors` link resolves here and returns nginx 404. This is a known regression class previously tracked in #6693/#7195.
3. `https://rustchain.org/explorer/anchors` — the actual anchors page loads, but `GET https://rustchain.org/api/anchors?limit=50&offset=0` returns HTTP 404, leaving `Failed to load anchor data`. Navigation links on the page also point to root `/` and `/anchors` rather than the `/explorer/` deployment prefix.

Additional dashboard console/network evidence on the same run:
- `GET /health` → 200
- `GET /epoch` → 200
- `GET /api/miners` → 200
- `GET /agent/stats` → 404
- `GET /agent/jobs` → 404

The screenshots in this directory correspond to those three pages. I am treating these as **live regression verification**, not novel vulnerability findings.
