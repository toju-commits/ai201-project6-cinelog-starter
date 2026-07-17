# CineLog

A community film tracking app. Users log films they've watched, rate them, build collections, and maintain watchlists.

This repository contains the completed work for **Project 6: Simulated Code Review**.

---

## Setup

```bash
pip install -r requirements.txt
python app.py
```

The app starts on `http://localhost:5000` and uses a local SQLite database (`cinelog.db`).

---

## Project Structure

```text
ai201-project6-cinelog-starter/
├── app.py                         # Flask app factory
├── models.py                      # SQLAlchemy models
├── services/
│   ├── collection_service.py      # Collection business logic
│   └── watchlist_service.py       # Watchlist business logic
├── routes/
│   ├── films.py                   # Film browsing endpoints
│   ├── collection.py              # Collection endpoints
│   └── watchlist/
│       └── watchlist.py           # Watchlist endpoints
├── tests/
│   ├── test_collection.py         # Collection service tests
│   └── test_watchlist.py          # Watchlist service and endpoint tests
├── pr-response.md                 # Responses to all review comments
├── CONTRIBUTING.md                # Commit conventions and PR guidelines
└── requirements.txt
```

---

## API Overview

### Films

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/films/` | List all films; supports `?genre=` and `?year=` filters |
| GET | `/films/<film_id>` | Get a single film by UUID |

### Collection

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/collection/<user_id>` | Get a user's collection, newest first |
| POST | `/collection/<user_id>/add` | Add a film to the collection |
| DELETE | `/collection/<user_id>/remove` | Remove a film from the collection |

### Watchlist

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/watchlist/<user_id>` | Get a user's watchlist, newest first |
| POST | `/watchlist/<user_id>/add` | Add a film; optional `public` boolean defaults to `true` |
| DELETE | `/watchlist/<user_id>/remove` | Remove a film from the watchlist |
| PATCH | `/watchlist/<user_id>/visibility` | Change an existing entry's visibility |

Example add request:

```json
{
  "film_id": "<film-uuid>",
  "public": false
}
```

---

## Data Models

**Film** — A film in the catalog. IDs are UUIDs.

**User** — A registered user. IDs are UUIDs.

**CollectionEntry** — Links a user to a film they have watched. Stores rating and date added. A user can only have one collection entry per film.

**WatchlistEntry** — Links a user to a film they want to watch. Stores date added and public visibility.

---

## Design Decisions

- Watchlist entries default to public because CineLog is designed around community discovery. Callers may explicitly create private entries or update visibility later.
- Watchlists are sorted newest-first because recent saves best support the "what should I watch next?" workflow.
- Duplicate user-and-film pairs are rejected with a domain-specific error instead of creating another entry.

The complete reasoning and conflict-resolution notes are documented in `pr-response.md`.

---

## Naming Conventions

Service functions follow a `verb_to_noun` pattern. See `CONTRIBUTING.md` for full details.

---

## Running Tests

```bash
python -m pytest tests/ -v
```
