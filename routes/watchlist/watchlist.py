"""
routes/watchlist/watchlist.py — CineLog

Endpoints for the watchlist feature.
"""

from flask import Blueprint, jsonify, request
from services.collection_service import FilmNotFoundError
from services.watchlist_service import (
    add_to_watchlist,
    get_watchlist,
    remove_from_watchlist,
    AlreadyInWatchlistError,
    NotInWatchlistError,
)

watchlist_bp = Blueprint("watchlist", __name__)


@watchlist_bp.route("/<user_id>", methods=["GET"])
def view_watchlist(user_id):
    """Return the user's watchlist, newest entries first."""
    return jsonify(get_watchlist(user_id))


@watchlist_bp.route("/<user_id>/add", methods=["POST"])
def add_film(user_id):
    """
    Add a film to a user's watchlist.

    Body:
        {"film_id": "<uuid>"}
    """
    data = request.get_json()
    if not data or "film_id" not in data:
        return jsonify({"error": "film_id is required"}), 400

    try:
        entry = add_to_watchlist(
            user_id=user_id,
            film_id=data["film_id"],
        )
        return jsonify(entry.to_dict()), 201
    except FilmNotFoundError as error:
        return jsonify({"error": str(error)}), 404
    except AlreadyInWatchlistError as error:
        return jsonify({"error": str(error)}), 409


@watchlist_bp.route("/<user_id>/remove", methods=["DELETE"])
def remove_film(user_id):
    """
    Remove a film from a user's watchlist.

    Body:
        {"film_id": "<uuid>"}
    """
    data = request.get_json()
    if not data or "film_id" not in data:
        return jsonify({"error": "film_id is required"}), 400

    try:
        remove_from_watchlist(user_id=user_id, film_id=data["film_id"])
        return jsonify({"message": "Removed from watchlist"}), 200
    except NotInWatchlistError as error:
        return jsonify({"error": str(error)}), 404
