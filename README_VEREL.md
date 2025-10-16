# Deploying this Flask app to Vercel

This repository uses a Flask app under `src/` with static files in `src/static`. The `api/index.py` file wraps the Flask WSGI app as ASGI using `asgiref` so Vercel's Python runtime can serve it.

Quick steps:

1. Ensure `requirements.txt` lists all dependencies (Flask, Flask-SQLAlchemy, asgiref, openai, etc.).
2. Set Vercel project environment variables (e.g. `ARK_API_KEY`) in the Vercel dashboard (or via the `vercel` CLI).
3. From this repository root run:

```bash
vercel deploy --prod
```

Notes & routing:
- `vercel.json` maps all requests to the Python function at `api/index.py`. The Flask app's `serve()` route is used to serve `src/static/index.html` and other assets from the static folder.
- For large static assets consider using Vercel's static file handling or uploading to a CDN.

Troubleshooting:
- If the app fails to start, check the build logs; missing packages must be added to `requirements.txt`.
- Ensure write access is not required at runtime for the SQLite file in `src/database/app.db` — serverless functions have ephemeral writers; for production use migrate to a managed DB (Postgres, MySQL) and update `SQLALCHEMY_DATABASE_URI`.
