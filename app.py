import json
import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for

from main import FFRPG, FlyRod, Leader, Fly


app = Flask(__name__)
# For development only; change this for any real deployment
app.secret_key = "dev-secret-key"

LEADERBOARD_FILE = "leaderboard.json"

# Single in-memory game instance (good enough for local play)
game = FFRPG()
last_message = "Welcome to FFRPG (web lofi edition). Use the controls below to play."


def ensure_basic_setup():
    """Ensure the game has some sensible defaults for web play."""
    global game, last_message
    if not game.current_location:
        game.current_location = "Mountain Stream"
        game.generate_location("stream")
    if not game.current_rod:
        game.current_rod = FlyRod(9, 5, "Graphite")
    if not game.current_leader:
        game.current_leader = Leader("Monofilament", "5X (3.0kg)", 9)
    if not game.current_fly:
        game.current_fly = Fly("Adams", "Dry Flies", 16)


def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []


def save_leaderboard(entries):
    try:
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)
    except Exception:
        # For this simple app, silently ignore write errors
        pass


def update_leaderboard(player):
    """Record the player's progress in a simple JSON leaderboard.

    Each entry keeps track of player name, total fish caught, best fish size,
    and total XP. Multiple sessions by the same name will just update/merge
    the existing record.
    """
    entries = load_leaderboard()

    total_fish = len(player.catch_record)
    best_size = max((size for _, size in player.catch_record), default=0)
    xp = player.xp

    # Find existing entry by name
    existing = None
    for e in entries:
        if e.get("name") == player.name:
            existing = e
            break

    if existing is None:
        entries.append(
            {
                "name": player.name,
                "total_fish": total_fish,
                "best_size": best_size,
                "xp": xp,
                "last_updated": datetime.utcnow().isoformat() + "Z",
            }
        )
    else:
        existing["total_fish"] = total_fish
        existing["best_size"] = best_size
        existing["xp"] = xp
        existing["last_updated"] = datetime.utcnow().isoformat() + "Z"

    # Sort by total fish, then best size, then xp
    entries.sort(key=lambda e: (-e.get("total_fish", 0), -e.get("best_size", 0), -e.get("xp", 0)))
    save_leaderboard(entries)


@app.route("/", methods=["GET", "POST"])
def index():
    global game, last_message

    if request.method == "POST":
        action = request.form.get("action")

        if action == "reset":
            game = FFRPG()
            last_message = "New game started. Build gear, pick a location, and cast!"
            return redirect(url_for("index"))

        if action == "set_name":
            name = (request.form.get("player_name") or "").strip()
            if name:
                game.player.name = name
                last_message = f"Name set to: {name}"
            else:
                last_message = "Name cannot be empty."
            return redirect(url_for("index"))

        if action == "build_gear":
            # Simple default setup mirroring the console defaults
            game.current_rod = FlyRod(9, 5, "Graphite")
            game.current_leader = Leader("Monofilament", "5X (3.0kg)", 9)
            game.current_fly = Fly("Adams", "Dry Flies", 16)
            last_message = "Built default gear: 9' 5wt Graphite rod, 9' Mono 5X leader, Adams size 16."
            return redirect(url_for("index"))

        if action == "location":
            chosen = request.form.get("location") or "Mountain Stream"
            location_type = "river"
            if "Stream" in chosen:
                location_type = "stream"
            elif "Lake" in chosen:
                location_type = "lake"
            game.generate_location(location_type)
            game.current_location = chosen
            last_message = f"Location set to: {chosen}."
            return redirect(url_for("index"))

        if action == "cast":
            # Track catches before/after this cast
            before_catches = len(game.player.catch_record)
            ensure_basic_setup()
            cast = request.form.get("cast", "").strip()
            result = game.start_fishing_web(cast or None)
            last_message = result
            after_catches = len(game.player.catch_record)
            if after_catches > before_catches:
                update_leaderboard(game.player)
            return redirect(url_for("index"))

    # GET request: render current game state
    display_text = game.display_game(as_string=True)
    return render_template(
        "index.html",
        display_text=display_text,
        last_message=last_message,
        leaderboard=load_leaderboard()[:10],  # top 10
        player_name=game.player.name,
    )


if __name__ == "__main__":
    # Run the Flask dev server
    app.run(debug=True)
