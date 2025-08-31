# F1 DataLens 🏎️  
_Serverless Formula 1 analytics dashboard on **AWS S3 + API Gateway + Lambda** (frontend-only hosting, backend via REST)_

![Static Site](https://img.shields.io/badge/Hosting-AWS%20S3-orange)
![API](https://img.shields.io/badge/API-API%20Gateway%20%2B%20Lambda-red)
![JS](https://img.shields.io/badge/Frontend-HTML%2FCSS%2FJS-blue)
![License](https://img.shields.io/badge/License-MIT-black)

> **F1 DataLens** is a lightweight analytics UI that calls the **API-SPORTS Formula-1** endpoints through an AWS **Lambda** function exposed by **API Gateway**, and renders standings, race info, driver comparisons, and circuit profiles. The site is hosted as a **static website on S3**.

---

## Table of Contents
- [Live Demo](#live-demo)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Quickstart (Local)](#quickstart-local)
- [Deploy to AWS](#deploy-to-aws)
- [Configuration](#configuration)
- [Security](#security)
- [Cost & Limits](#cost--limits)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)
- [License](#license)

---

## Live Demo
- **S3 website endpoint** (static frontend): _your-public-s3-website-url_
- **API Gateway** (backend Lambda endpoint): _your-api-gw-url_/top-tracks (example path)

> Replace the placeholders above after you deploy.

---

## Features
- **Overview**: season KPIs (races, drivers, teams, points sum), latest & next race cards.
- **Season Analysis**: race calendar table, season stats.
- **Driver Comparison**: pick up to 2 drivers and compare key stats with clean progress bars.
- **Circuit Profiler**: browse circuits used in the selected season.
- **Resilient UI**: guards against missing fields, graceful loading/error states.
- **Dark/Light** theme toggle with persistence.

---

## Architecture

```
Browser (S3 static site: HTML/CSS/JS)
  └── fetch() ───────────────► API Gateway (HTTP/REST)
                               └── Lambda (Python)
                                   └── Calls API-SPORTS F1 endpoints
                                       (via RapidAPI key)
```

- **Frontend**: single-page app (`frontend/index.html`) served from **S3 static website hosting**.
- **Backend**: `backend/lambda_function.py` (Python) behind **API Gateway**. The Lambda injects API key headers and aggregates data when necessary.
- **No servers to manage**; you can optionally add **CloudFront** CDN in front of S3 for HTTPS and caching.

---

## Project Structure

```
/frontend
  └── index.html        # single-page app (Bootstrap + Chart.js + vanilla JS)
/backend
  └── lambda_function.py # Python Lambda handler (proxy to API-SPORTS F1)
README.md
```

---

## Prerequisites
- **AWS account** with S3, Lambda, API Gateway permissions
- **RapidAPI** (API-SPORTS Formula-1) — plan used here: **$15/month**, **7,500 requests/day**
- Python 3.10+ (for local packaging of Lambda if needed)
- A modern browser

---

## Quickstart (Local)

> You can open the frontend **directly** in a browser for layout testing. API calls will only work if CORS allows your origin (or if you point the page to a **Lambda Function URL** during testing).

1) Clone repo
```bash
git clone https://github.com/<you>/f1-datalens.git
cd f1-datalens
```

2) Open the UI
```bash
# Option A: open the static file
open frontend/index.html  # macOS (or double click)

# Option B: run a tiny HTTP server (recommended)
cd frontend
python -m http.server 5173
# visit http://localhost:5173
```

3) Configure API base in `index.html` (see **Configuration** below).

---

## Deploy to AWS

### 1) S3 static hosting
- Create bucket, enable **Static website hosting**.
- Upload `frontend/index.html`.
- Set **Index document** = `index.html` (and optional Error document = `index.html`).
- Bucket policy for public read (or put CloudFront in front).

### 2) Lambda
- Create function (Python 3.10/3.12), set **handler** to `lambda_function.lambda_handler`.
- Upload zipped `backend/lambda_function.py`.
- **Env vars** (example):
  - `RAPIDAPI_HOST = v1.formula-1.api-sports.io`
  - `RAPIDAPI_KEY  = <your-rapidapi-key>`
- Timeout: 10–15s, Memory: 256 MB.

### 3) API Gateway
- Create **HTTP API** (or REST API) and integrate with Lambda.
- Route: `GET /top-tracks` (and other routes you expose).
- **CORS**: allow your S3 website origin (or `*` while testing).
- Deploy and note the invoke URL.

### 4) Wire the frontend
- In `frontend/index.html`, point to your API GW / Lambda Function URL (see **Configuration**).  
- Test from the **S3 website endpoint**.

---

## Configuration

In `frontend/index.html`, set the API config near the top of the script:

```js
// API Configuration
const API_BASE_URL = 'https://v1.formula-1.api-sports.io'; // or your API Gateway/Lambda URL
const API_KEY = 'YOUR_RAPIDAPI_KEY'; // if you call RapidAPI directly (NOT recommended in browser)
```

**Recommended**: keep API keys only in Lambda. In that case, change the `API_BASE_URL` to your **API Gateway** or **Lambda Function URL**, and remove the key from the browser code. Add CORS on the backend and return JSON to the frontend.

---

## Security
- **Do not expose API keys** in the browser. Prefer the Lambda proxy pattern.
- Least-privilege IAM for Lambda execution role.
- If you add a VPC later for other data sources, ensure **NAT** for outbound Internet.

---

## Cost & Limits
- Frontend hosting on **S3** is pennies per month.
- Backend: **Lambda** + **API Gateway** charges are modest for student-scale traffic.
- RapidAPI plan used: **$15/month** with **7,500 requests/day** (sufficient for classroom use).
- Optimizations:
  - **Cache** responses in the browser (localStorage) or add a small in-memory cache in Lambda.
  - Avoid fetching on every tab switch; reuse previously loaded data (the code already memoizes some calls).
  - Limit driver comparison to **2 drivers** (already enforced) to avoid unnecessary calls.

---

## Monitoring
- **CloudWatch Logs** for Lambda (errors, latency).
- **API Gateway metrics** (4XX/5XX, latency).
- **S3 access logs** (optional).

---

## Troubleshooting
- **CORS** errors in browser but `curl` works → enable CORS in API Gateway or return headers from Lambda:
  - `Access-Control-Allow-Origin: https://<your-s3-site>`
  - `Access-Control-Allow-Methods: GET,OPTIONS`
- **Lambda timeout** → increase to 10–15s and confirm it has outbound Internet (no VPC or NAT present).
- **S3 403/404** → check bucket policy and **Index document** = `index.html`.
- **Images/logos missing** → this version intentionally uses **text-first** standings to avoid logo lookups.

---

## Roadmap
- Add **CloudFront** in front of S3 for TLS + caching.
- Precompute season aggregates in Lambda for faster first paint.
- Add a **/health** route on Lambda for quick status checks.
- Optional **map** for circuits with Leaflet + OSM.

---

## License
MIT © 2025 Your Name