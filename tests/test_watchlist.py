"""
Tests for the watchlist service and endpoints.
"""

from datetime import datetime, timezone

import pytest

from app import create_app, db
from models import Film, User, WatchlistEntry
from services.collection_service import FilmNotFoundError
from services.watchlist_service import (
    add_to_watchlist,
    get_watchlist,
    remove_from_watchlist,
    set_watchlist_visibility,
    NotInWatchlistError,
)


@pytest.fixture
def app():
    """Create an isolated test app with an in-memory database."""
    app = create_app(config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a Flask test client."""
    return app.test_client()


@pytest.fixture
def sample_user(app):
    """Create a user for watchlist tests."""
    with app.app_context():
        user = User(
            username="watchlistuser",
            email="watchlist@example.com",
        )
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def sample_film(app):
    """Create a film for watchlist tests."""
    with app.app_context():
        film = Film(title="Paddington 2", year=2017, genre="Comedy")
        db.session.add(film)
        db.session.commit()
        return film.id


def test_add_to_watchlist_nonexistent_film_raises(app, sample_user):
    """A nonexistent film ID should raise FilmNotFoundError."""
    with app.app_context():
        fake_film_id = "00000000-0000-0000-0000-000000000000"

        with pytest.raises(FilmNotFoundError):
            add_to_watchlist(
                user_id=sample_user,
                film_id=fake_film_id,
            )


def test_get_watchlist_returns_newest_first(app, sample_user):
    """Watchlist results should return the most recently added film first."""
    with app.app_context():
        older_film = Film(title="Alpha", year=2000, genre="Drama")
        newer_film = Film(title="Zulu", year=1964, genre="Drama")
        db.session.add_all([older_film, newer_film])
        db.session.commit()

        older_entry = add_to_watchlist(sample_user, older_film.id)
        newer_entry = add_to_watchlist(sample_user, newer_film.id)
        older_entry.date_added = datetime(2026, 1, 1, tzinfo=timezone.utc)
        newer_entry.date_added = datetime(2026, 1, 2, tzinfo=timezone.utc)
        db.session.commit()

        result = get_watchlist(sample_user)
        assert [film["title"] for film in result] == ["Zulu", "Alpha"]


def test_remove_from_watchlist_deletes_entry(app, sample_user, sample_film):
    """Removing an existing watchlist item should delete its row."""
    with app.app_context():
        add_to_watchlist(sample_user, sample_film)

        assert remove_from_watchlist(sample_user, sample_film) is True
        assert WatchlistEntry.query.filter_by(
            user_id=sample_user,
            film_id=sample_film,
        ).first() is None


def test_remove_from_watchlist_missing_raises(app, sample_user, sample_film):
    """Removing a missing item should raise NotInWatchlistError."""
    with app.app_context():
        with pytest.raises(NotInWatchlistError):
            remove_from_watchlist(sample_user, sample_film)


def test_add_to_watchlist_accepts_private_visibility(
    app, sample_user, sample_film
):
    """Callers may explicitly create a private watchlist entry."""
    with app.app_context():
        entry = add_to_watchlist(
            sample_user,
            sample_film,
            public=False,
        )
        assert entry.public is False


def test_set_watchlist_visibility_updates_entry(
    app, sample_user, sample_film
):
    """Visibility updates should persist on the existing entry."""
    with app.app_context():
        add_to_watchlist(sample_user, sample_film)
        entry = set_watchlist_visibility(
            sample_user,
            sample_film,
            public=False,
        )
        assert entry.public is False


def test_visibility_endpoint_rejects_non_boolean(
    client, sample_user, sample_film
):
    """The visibility endpoint should reject ambiguous string values."""
    response = client.patch(
        f"/watchlist/{sample_user}/visibility",
        json={"film_id": sample_film, "public": "false"},
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "public must be a boolean"
