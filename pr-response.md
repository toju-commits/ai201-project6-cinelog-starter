# PR Response Doc — CineLog Watchlist Feature

## AI Usage

I used AI as a learning and review assistant throughout this project. Specific uses included:

- explaining the difference between a fork, clone, remote, rebase, and force-push;
- helping me trace `save_to_watchlist()` across the service definition, route import, and route call before renaming it;
- comparing `add_to_watchlist()` with the existing `add_to_collection()` implementation so I could follow the codebase's established deduplication pattern;
- acting as a devil's advocate for the default-visibility and sort-order decisions;
- helping diagnose a semantic rebase conflict that Git did not flag with conflict markers; and
- reviewing this response against the final grading rubric.

I manually inspected the code, ran the commands, made the final design decisions, and verified the implementation. I did not treat AI output as authoritative; when a suggested verification command was wrong for this Flask application, I checked `app.py`, corrected the command, and continued from the codebase's actual structure.

---

## Comment 1 — Rename `save_to_watchlist`

**Reviewer feedback:**  
Rename `save_to_watchlist()` to `add_to_watchlist()` so it follows CineLog's `verb_to_noun` naming convention.

**What I did:**  
I searched the full repository for `save_to_watchlist` before changing anything. I found three references:

1. the function definition in `services/watchlist_service.py`;
2. the service import in `routes/watchlist/watchlist.py`; and
3. the route invocation in `routes/watchlist/watchlist.py`.

I renamed all three references to `add_to_watchlist()` so the service matches established names such as `add_to_collection()`.

**How I verified it:**  
I searched all Python files again and confirmed that `save_to_watchlist` returned no results. I then searched for `add_to_watchlist` and confirmed that the definition, import, and route invocation were all present. I also imported the watchlist route and ran the test suite to confirm the rename did not break application loading.

---

## Comment 2 — Prevent duplicate watchlist entries

**Reviewer feedback:**  
Prevent a user from adding the same film to their watchlist multiple times.

**What I did:**  
Before implementing the fix, I examined `add_to_collection()` in `services/collection_service.py`. That function queries for an existing entry with the same `user_id` and `film_id`, then raises a domain-specific exception instead of inserting another row.

I followed the same pattern in `add_to_watchlist()`. The service now queries `WatchlistEntry` for the exact user-and-film pair. If a match exists, it raises `AlreadyInWatchlistError` and does not create or commit another entry. If no match exists, the new watchlist entry is created normally.

**How I verified it:**  
I reviewed the diff to confirm the check occurred before object creation and commit, confirmed the new exception and service function imported successfully, and ran the test suite. The route now also translates `AlreadyInWatchlistError` into an HTTP `409 Conflict` response.

---

## Comment 3 — Test nonexistent film IDs

**Reviewer feedback:**  
Add a test proving that adding a nonexistent film raises `FilmNotFoundError`.

**What I did:**  
I added `test_add_to_watchlist_nonexistent_film_raises()` in `tests/test_watchlist.py`. I modeled it after the existing `test_add_to_collection_nonexistent_film_raises()` test in `tests/test_collection.py`.

The test creates a valid user, passes a valid-looking UUID that is not stored in the database, and verifies that `add_to_watchlist()` raises `FilmNotFoundError`. This targets the requested nonexistent-`film_id` case rather than malformed input or a duplicate entry.

**How I verified it:**  
I ran the watchlist test independently and then ran the complete test suite.

---

## Comment 4 — Default watchlist visibility

**Reviewer feedback:**  
Explain why new watchlist entries default to `public=True`.

**My decision:**  
I chose to keep `public=True` as the default for new watchlist entries.

**Reasoning:**  
CineLog is presented as a community film-tracking app rather than a private diary. Public watchlists let users discover films through the people they follow, compare what friends plan to watch, and start conversations around shared interests without every user first having to configure a visibility setting. That supports CineLog's community-discovery value and reduces friction during the first-use experience.

**Tradeoff acknowledged:**  
Private-by-default would better protect users who assume saved items are personal and would reduce accidental exposure. That is a meaningful benefit. I still prefer public-by-default for CineLog because the product's stated purpose is community film discovery, but the interface must display the visibility state clearly and make privacy easy to control. To reduce the tradeoff, the endpoint now accepts an explicit `public` boolean and supports later visibility updates.

---

## Comment 5 — Watchlist sort order

**Reviewer feedback:**  
Decide whether watchlists should be sorted alphabetically or by date added.

**My decision:**  
I agreed with the maintainer and changed the default order to date added, newest first.

**Reasoning:**  
A watchlist represents current intent: films a user recently decided they may watch next. When users reopen the list, the newest additions are more likely to reflect their present mood and priorities than titles saved months ago. Newest-first also matches CineLog's collection ordering, making navigation between watched and unwatched lists more predictable.

**Engagement with the maintainer's position:**  
The maintainer argued that most users want to see what they added recently. I agree because recency is directly connected to the "what should I watch next?" use case. Alphabetical order is still valuable for scanning a large established list, but that need is better handled through search or an optional sort control instead of making alphabetical order the only default.

---

## Comment 6 — Rebase onto updated `main`

**Reviewer feedback:**  
Rebase onto `main` after film IDs changed from integers to UUIDs.

**What conflicted:**  
My feature branch was created before CineLog changed film IDs from auto-incrementing integers to UUID strings. The original watchlist code therefore used an integer `film_id`, while updated `main` defined `Film.id` and related foreign keys as `db.String(36)` UUID values.

The rebase produced a textual conflict in `.gitignore` because both branches had added similar ignore rules. After Git reported that the rebase had succeeded, the tests exposed a second, semantic conflict: the UUID-based `Film` and `CollectionEntry` definitions were present, but the `WatchlistEntry` class had been dropped. Git did not show conflict markers for that architectural mismatch.

**How I resolved it:**  
I combined the `.gitignore` rules without creating a merge commit. I preserved the UUID-based `Film` model from updated `main`, restored `WatchlistEntry`, and changed its `film_id` foreign key from an integer column to `db.String(36)`. I also preserved the relationships between users, films, and watchlist entries that `get_watchlist()` requires.

**How I verified it:**  
I searched the repository for stale integer-based film-ID references, confirmed that `WatchlistEntry` imported successfully, checked that the branch history remained linear with no merge commits, and ran the complete test suite.

---

## Stretch Feature — Second Test

I added `test_get_watchlist_returns_newest_first()` to make the Comment 5 decision executable. The test uses two titles whose alphabetical order conflicts with their timestamp order: `Alpha` is older and `Zulu` is newer. It expects `Zulu` before `Alpha`, so it fails if the implementation is changed back to alphabetical sorting.

I chose this case because a strong test should distinguish the two competing behaviors instead of passing under either implementation. While developing it, the test also exposed missing relationships between `WatchlistEntry`, `User`, and `Film`, which were fixed so populated watchlists can access `entry.film`.

---

## Stretch Feature — `remove_from_watchlist()`

I implemented `remove_from_watchlist(user_id, film_id)` by following the existing `remove_from_collection()` pattern. The service queries for the matching user-and-film entry. If it exists, the row is deleted and the transaction is committed. If it does not exist, the service raises `NotInWatchlistError` instead of silently reporting success.

I added `DELETE /watchlist/<user_id>/remove`, which accepts a JSON body containing `film_id`. The route returns `200` after a successful removal and `404` when the entry is not on the watchlist.

Tests cover both the successful deletion path and the missing-entry error path.

---

## Stretch Feature — Visibility Controls

`add_to_watchlist()` now accepts an optional `public` parameter. The default remains `True`, preserving the intentional community-oriented default from Comment 4. A caller can create a private entry by sending:

```json
{
  "film_id": "<film-uuid>",
  "public": false
}
```

The add endpoint validates that `public` is a boolean. I also added `PATCH /watchlist/<user_id>/visibility`, which lets a caller change an existing entry's visibility using `film_id` and `public`. The service raises `NotInWatchlistError` when the requested film is not on the user's watchlist.

Tests cover private creation, persisted visibility updates, and rejection of ambiguous non-boolean values.

---

## Final PR Description

### What the feature does

This PR adds watchlists to CineLog so users can save films they want to watch later, retrieve those films newest-first, remove films, and control whether each entry is public. It includes a UUID-compatible `WatchlistEntry` model, service-layer business rules, REST endpoints, duplicate protection, explicit error handling, and focused tests.

### Design decisions

- **Default visibility:** New entries default to public because CineLog is a community film-discovery app, while callers can explicitly create private entries or change visibility later.
- **Sort order:** Watchlists default to newest-added first because recent saves are most relevant to the "what should I watch next?" workflow; alphabetical search or sorting can be added as a separate option later.

### How to manually test

1. Install dependencies with `pip install -r requirements.txt`.
2. Start CineLog with `python app.py`.
3. Obtain a valid user UUID and film UUID from the local database.
4. Add a public entry:
   `POST /watchlist/<user_id>/add` with `{"film_id": "<film-uuid>"}`.
5. Add a private entry for another film:
   `POST /watchlist/<user_id>/add` with `{"film_id": "<film-uuid>", "public": false}`.
6. Send `GET /watchlist/<user_id>` and confirm the most recently added film appears first and each item includes its `public` value.
7. Attempt to add the same film again and confirm the API returns `409` without creating a duplicate.
8. Change visibility with `PATCH /watchlist/<user_id>/visibility` and body `{"film_id": "<film-uuid>", "public": true}`.
9. Remove the film with `DELETE /watchlist/<user_id>/remove` and body `{"film_id": "<film-uuid>"}`.
10. Repeat the removal and confirm the API returns `404`.
11. Run `python -m pytest tests/ -v` and confirm the complete suite passes.

### Submission evidence

The setup screenshot and final commit-history screenshot are submitted separately through the course portal. They are intentionally not committed as binary repository artifacts because they are grading evidence rather than application source code.
