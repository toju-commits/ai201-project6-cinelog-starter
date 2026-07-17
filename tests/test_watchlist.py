"""
Tests for the watchlist service.
"""

from datetime import datetime, timezone

import pytest

from app import create_app, db
from models import Film, User
from services.collection_service import FilmNotFoundError
from services.watchlist_service import add_to_watchlist, get_watchlist


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


def test_add_to_watchlist_nonexistent_film_raises(app, sample_user):
    """
    Adding a film ID that does not exist should raise FilmNotFoundError.
    """
    with app.app_context():
        fake_film_id = "00000000-0000-0000-0000-000000000000"

        with pytest.raises(FilmNotFoundError):
            add_to_watchlist(
                user_id=sample_user,
                film_id=fake_film_id,
            )



def test_get_watchlist_returns_newest_first(app, sample_user):
    """
    Watchlist results should return the most recently added film first.
    """
    with app.app_context():
        older_film = Film(
            title="Alpha",
            year=2000,
            genre="Drama",
        )
        newer_film = Film(
            title="Zulu",
            year=1964,
            genre="Drama",
        )

        db.session.add_all([older_film, newer_film])
        db.session.commit()

        older_entry = add_to_watchlist(
            user_id=sample_user,
            film_id=older_film.id,
        )
        newer_entry = add_to_watchlist(
            user_id=sample_user,
            film_id=newer_film.id,
        )

        older_entry.date_added = datetime(
            2026, 1, 1, tzinfo=timezone.utc
        )
        newer_entry.date_added = datetime(
            2026, 1, 2, tzinfo=timezone.utc
        )
        db.session.commit()

        result = get_watchlist(sample_user)

        assert [film["title"] for film in result] == [
            "Zulu",
            "Alpha",
        ]
