# PR Response Doc — CineLog Watchlist Feature

## AI Usage

I used AI as a learning and review assistant to help interpret the project requirements, understand unfamiliar code, explain Git commands, and review my reasoning. I manually ran all commands, inspected the code, made the final decisions, and verified the results.

## Comment 1 — Rename `save_to_watchlist`

**Reviewer feedback:**  
Rename `save_to_watchlist()` to `add_to_watchlist()` so it follows CineLog's `verb_to_noun` naming convention.

**What I did:**  
Renamed `save_to_watchlist()` to `add_to_watchlist()` in the service definition, route import, and route call so the function follows CineLog's `verb_to_noun` convention.

**How I verified it:**  
Searched the repository to confirm no references to `save_to_watchlist()` remained, confirmed the watchlist route imported successfully, and ran the full test suite. All 4 existing tests passed.

---

## Comment 2 — Prevent duplicate watchlist entries

**Reviewer feedback:**  
Prevent a user from adding the same film to their watchlist multiple times.

**What I did:**  
Added an `AlreadyInWatchlistError` exception and checked for an existing `WatchlistEntry` with the same `user_id` and `film_id` before creating a new entry.

**How I verified it:**  
Confirmed the updated service imports successfully, checked the diff for unintended changes, and ran the full existing test suite. All 4 tests passed.

---

## Comment 3 — Test nonexistent film IDs

**Reviewer feedback:**  
Add a test proving that adding a nonexistent film raises `FilmNotFoundError`.

**What I did:**

**How I verified it:**

---

## Comment 4 — Default watchlist visibility

**Reviewer feedback:**  
Explain why new watchlist entries default to `public=True`.

**My decision:**

**Reasoning:**

**Tradeoff acknowledged:**

---

## Comment 5 — Watchlist sort order

**Reviewer feedback:**  
Decide whether watchlists should be sorted alphabetically or by date added.

**My decision:**

**Reasoning:**

**Engagement with the reviewer's position:**

---

## Comment 6 — Rebase onto updated `main`

**Reviewer feedback:**  
Rebase onto `main` after film IDs changed from integers to UUIDs.

**What conflicted:**

**How I resolved it:**

**How I verified it:**

---

## Final PR Description

### What the feature does

### Design decisions

### How to manually test


