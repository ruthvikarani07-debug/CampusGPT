# CampusGPT

CampusGPT is a portfolio demonstration of a campus information assistant. It pairs a responsive web application with a dependency-free Python HTTP API and SQLite persistence. The initial workspace is fictional and explicitly labeled as sample data; this is not an official university integration.

## Implementation checklist

- [x] Empty repository inspected; no framework, backend, database, or package manager files were present.
- [x] Responsive branded landing page, dashboard, chat, document library, study planner, profile, theme toggle, and authentication screens.
- [x] Python API with password hashing, HTTP-only sessions, owner-scoped tasks and conversations, and SQLite indexes.
- [x] Optional Gemini integration on the server, only when `GEMINI_API_KEY` is configured.
- [x] Workspace document text upload API protected by an administrator role.
- [x] Local run/configuration and architecture documentation.
- [ ] Production-grade deployment hardening, PDF extraction, API rate limits, admin management UI, and full QA suite remain future work.

## Requirements

- Python 3.10 or later (the implementation uses only the Python standard library).
- No npm, Node modules, or external database is required for local development.
- Optional: a Gemini API key for grounded AI responses.

## Run locally

From this directory:

```powershell
python server.py
```

Then open <http://127.0.0.1:8000>. The server creates `campusgpt.sqlite3` on first run and binds to localhost by default. Set `PORT` to choose a different port. Set `CAMPUSGPT_DB` to choose a database file.

Create a student account using the sign-up page. Passwords are hashed with PBKDF2-HMAC-SHA256 and a per-user random salt. Sessions are stored as hashes in SQLite and sent via HTTP-only, SameSite cookies.

## Environment variables

See [.env.example](.env.example). Python does not load `.env` automatically; export variables in your shell or configure them in the hosting environment.

| Variable | Required | Purpose |
|---|---|---|
| `HOST` | No | Bind address; defaults to `127.0.0.1` |
| `PORT` | No | HTTP port; defaults to `8000` |
| `CAMPUSGPT_DB` | No | SQLite file path; defaults to `./campusgpt.sqlite3` |
| `SESSION_SECRET` | For deployment | Reserved for deployment session signing; replace the development value with a random secret |
| `GEMINI_API_KEY` | No | Server-side key. Without it, chat displays an honest setup message and does not fabricate a model response |
| `GEMINI_MODEL` | No | Gemini model name; defaults to `gemini-2.5-flash` |

Never expose the Gemini key in client-side code. Chat sends only retrieved published passages and the student's question. Provider errors are returned as a safe generic message.

## Features and current behavior

- Landing page with product overview, feature section, and sample assistant preview.
- Sign-up and login with server-validated inputs. Public registration always creates a student.
- Dashboard with real counts and tasks from the current account and published document metadata.
- Chat conversations are persisted per user. A conversation ID is checked against the session owner before access or continuation.
- Published text documents are searched with a simple token overlap retriever. Gemini responses are constrained to retrieved evidence and cite source numbers. If no passage matches, the assistant declines to answer from university sources.
- Study tasks are persisted per user and support create, mark complete, and delete. The API also supports task title, priority, due-date edits.
- Document library search and category filters.
- Dark/light preference is persisted in browser local storage.
- One fictional sample document is seeded on a new database to explain the demonstration workspace.

## Administrator setup and document ingestion

There is intentionally no public route to grant administrator privileges. Create the account through sign-up, then promote it from a trusted local console:

```powershell
python -c "import sqlite3; d=sqlite3.connect('campusgpt.sqlite3'); d.execute('UPDATE users SET role=? WHERE email=?', ('admin','you@example.edu')); d.commit()"
```

The initial UI does not expose an admin dashboard. An administrator can add extracted text using the protected `POST /api/admin/documents` endpoint with JSON fields `title`, `category`, and `content`; allowed categories are Academic notices, Academic calendars, Examination information, Course materials, Student guidelines, and Frequently asked questions. The current endpoint accepts text content, not file uploads. Add a maintained PDF extraction and multipart upload layer before using real PDFs.

## API overview

All endpoints are same-origin. JSON errors use `{"error":"…"}`.

| Method | Path | Access | Purpose |
|---|---|---|---|
| GET | `/api/health` | Public | API and AI configuration status |
| POST | `/api/auth/register` | Public | Student registration; name, email, password (10+ chars) |
| POST | `/api/auth/login` | Public | Create session cookie |
| POST | `/api/auth/logout` | Session | Revoke session |
| GET | `/api/me` | Session | Current user |
| GET/POST | `/api/tasks` | Session | List/create own study tasks |
| PATCH/DELETE | `/api/tasks/{id}` | Owner | Update/delete an own task |
| GET | `/api/documents` | Session | List published document metadata |
| GET | `/api/conversations` | Session | List own conversations |
| GET/DELETE | `/api/conversations/{id}` | Owner | Read/delete an own conversation |
| POST | `/api/chat` | Session | Create/continue grounded chat |
| POST | `/api/admin/documents` | Admin | Publish a text document |

## Data model

SQLite tables: `users`, `sessions`, `tasks`, `documents`, `conversations`, `messages`, and `feedback`. Tasks and conversations include a user foreign key; messages belong to conversations; sessions contain a one-way token hash. Common user, task, and message lookups have indexes. The first version is single-workspace; add a `workspace_id` to users/documents and enforce it in every query before serving multiple institutions.

## Testing

Run the standard-library suite:

```powershell
python -m unittest -v
```

This checks password hashing and the HTTP account/task ownership flows. The suite is a focused smoke test, not the complete acceptance suite in the product brief. It does not verify browser rendering, Gemini calls, upload attack cases, rate limiting, or mobile screenshots.

## Deployment notes

This prototype has no production deployment configuration yet. It is suitable for local review and portfolio demonstration. Before public hosting, use HTTPS, set secure cookies behind TLS, replace the development secret, add CSRF protection and rate limits, validate proxy headers, configure backups, and use a persistent private database volume. The standard-library HTTP server is not intended as a hardened production application server. A hosted Gemini key and a securely configured deployment environment are needed for live AI answers. Deployment provider pricing and free-tier availability have not been verified.

## Known limitations

- Uses Python/SQLite in place of the requested Next.js/NestJS/MongoDB stack because this workspace is empty and npm is unavailable in the provided environment.
- No PDF parsing or multipart upload; admins submit extracted text through the protected API.
- No rate limiting, CSRF defense, production TLS cookie flag, user management UI, document review queue, or admin dashboard UI yet.
- No streaming, feedback UI, summarizer endpoint, semantic embeddings, or browser end-to-end suite.
- Gemini model availability depends on the configured account/API and has not been verified without credentials.
- No claims of deployment or production readiness.

