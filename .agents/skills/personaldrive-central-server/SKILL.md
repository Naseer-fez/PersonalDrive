---
name: PersonalDrive Central Server Architecture
description: Architecture knowledge for the PersonalDrive frontend's Central Server URL resolution system, including auth flow and dynamic backend URL discovery.
---

# PersonalDrive Central Server Architecture

## Overview
PersonalDrive uses a **Central Server (Main Server)** as a URL registry/discovery service to abstract away dynamic ngrok URLs from the frontend user. The backend registers its URL with the Central Server on startup, and the frontend resolves the backend URL through the Central Server.

## Authentication Flow
1. **DualLogin Page** (`/login`): Default view is "Access Drive" — user enters access code + optional password
2. **Code Login**: `GET /login/url/?code=...&userpassword=...` → Central Server verifies code and optional password → returns `{ return: jwt_token, userid }`
3. **URL Resolution**: `GET /url/` with `code` + `auth` headers → returns `{ url, allowusers }`
4. **Client Registration**: If `allowusers=true`, user is redirected to `/client-register` to register on the PersonalDrive backend
5. **Single-User Mode**: If `allowusers=false`, userid is set to `-1` and user goes directly to FileBrowser

## Admin Flow (Server Owner)
1. **Register**: `POST /register/` → `{ api_key, code, server_url, userid }`
2. **Login**: `POST /login/` → `{ api_key, code, server_url, userid }`
3. **Dashboard** (`/dashboard`): Shows API key + access code with copy buttons
4. **Generate New Key**: `POST /dashboard/` → `{ api_key, code }`

## Backend Registration
- `server_launcher.py` calls `GET /register/api/?api=<key>&link=<url>&users=0|1`
- Then `POST /register/user/` with `{ api, code, userpassword }` to register frontend credentials
- The `api_key` is from `packageconfig.json` — NOT exposed to the frontend

## Code Organization
- `src/config.js` — Single source of truth for URLs and localStorage keys
- `src/api/centralServer.js` — Central Server API calls (login, register, resolve, forgot). Isolated, uses raw fetch().
- `src/api/client.js` — PersonalDrive backend HTTP client. Uses dynamic URL from `localStorage[CLIENT_BACKEND_URL_KEY]`.
- `src/api/endpoints.js` — PersonalDrive API endpoint functions.
- `src/context/AuthContext.jsx` — Stores auth state (token, userid).
- `src/pages/DualLogin/` — Combined Access Drive + Admin login/register page.
- `src/pages/Dashboard/` — Admin dashboard with API key management.
- `src/pages/ClientRegister/` — Client-side user registration (when allowusers=true).
- `src/pages/ForgotCode/` — Recover access code via email.
- `src/pages/ForgotPassword/` — Recover PersonalDrive backend password (for client users).

## Key Design Decisions
- DualLogin defaults to Access Drive (code entry), with toggle to admin register/login
- Structured JSON responses (no pipe-delimited strings)
- `userid = -1` sentinel for single-user mode (avoids collision with auto-increment IDs)
- Two forgot flows: ForgotCode (Central Server) + ForgotPassword (PersonalDrive backend)
- Central Server URL from `.env` (`VITE_API_BASE_URL`), not stored in localStorage
- GUI writes Brevo credentials to `.env` for email recovery support
- No ServerProvider/health-check racing — DualLogin handles URL resolution directly

## Central Server API Contract
```
POST /register/       → { api_key, code, server_url, userid }
POST /login/          → { api_key, code, server_url, userid }
POST /dashboard/      → { api_key, code }
GET  /login/url/      → { return: jwt_token, userid }  (verifies userpassword when set)
GET  /url/            → { url, allowusers }  (auth required)
POST /forgot/         → { return: message }
GET  /register/api/   → { return: "success" }  (backend registration)
POST /register/user/  → { message }  (frontend credential registration)
```

## localStorage Keys
| Key | Purpose |
|-----|---------|
| `token` | JWT token from Central Server login |
| `userid` | User ID for PersonalDrive backend API paths |
| `client_backend_url` | Resolved PersonalDrive backend URL |
| `allowusers` | Whether client-side user registration is enabled |
| `main_username` | Admin username (for Dashboard) |
| `main_password` | Admin password (for Dashboard) |
| `main_api_key` | Central API key (for Dashboard) |
| `main_access_code` | Access code (for Dashboard) |
