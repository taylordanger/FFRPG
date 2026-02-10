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

# Static option sets mirroring the console game
LEADER_LINE_TYPES = ["Fluorocarbon", "Monofilament", "Braided"]
LEADER_DIAMETERS = [
    "7X (2.0kg)",
    "6X (2.5kg)",
    "5X (3.0kg)",
    "4X (3.5kg)",
    "3X (4.5kg)",
    "2X (6.0kg)",
    "1X (7.0kg)",
    "0X (8.0kg)",
]

ROD_LENGTHS = [7, 8, 9, 10]
ROD_WEIGHTS = [3, 4, 5, 6, 7, 8]
ROD_MATERIALS = ["Graphite", "Fiberglass", "Bamboo"]

FLY_CATEGORIES = ["Dry Flies", "Wet Flies", "Nymphs", "Streamers"]
FLY_PATTERNS = {
    "Dry Flies": ["Adams", "Elk Hair Caddis", "Parachute Hopper", "Royal Wulff"],
    "Wet Flies": ["Partridge & Orange", "Soft Hackle Hare's Ear", "Tellico Nymph"],
    "Nymphs": ["Pheasant Tail", "Gold-Ribbed Hare's Ear", "Zebra Midge", "Copper John"],
    "Streamers": ["Woolly Bugger", "Clouser Minnow", "Muddler Minnow", "Zonker"],
}
FLY_SIZES = [22, 20, 18, 16, 14, 12, 10, 8, 6, 4]

# Helper to derive category from pattern (for robustness)
PATTERN_TO_CATEGORY = {
    pattern: category
    for category, patterns in FLY_PATTERNS.items()
    for pattern in patterns
}


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

        if action == "build_leader":
            material = request.form.get("leader_material") or "Monofilament"
            if material not in LEADER_LINE_TYPES:
                material = "Monofilament"

            tippet = request.form.get("leader_tippet") or "5X (3.0kg)"
            if tippet not in LEADER_DIAMETERS:
                tippet = "5X (3.0kg)"

            try:
                length_val = int(request.form.get("leader_length") or 9)
            except ValueError:
                length_val = 9
            if length_val < 7 or length_val > 12:
                length_val = 9

            game.current_leader = Leader(material, tippet, length_val)
            last_message = f"Leader built: {material}, {tippet}, {length_val} feet."
            return redirect(url_for("index"))

        if action == "build_rod":
            try:
                length_val = int(request.form.get("rod_length") or 9)
            except ValueError:
                length_val = 9
            if length_val not in ROD_LENGTHS:
                length_val = 9

            try:
                weight_val = int(request.form.get("rod_weight") or 5)
            except ValueError:
                weight_val = 5
            if weight_val not in ROD_WEIGHTS:
                weight_val = 5

            material = request.form.get("rod_material") or "Graphite"
            if material not in ROD_MATERIALS:
                material = "Graphite"

            game.current_rod = FlyRod(length_val, weight_val, material)
            last_message = f"Rod built: {length_val}' {weight_val}-weight {material}."
            return redirect(url_for("index"))

        if action == "build_fly":
            # Category is mostly for flavour; we derive the true category from pattern
            selected_pattern = request.form.get("fly_pattern") or "Adams"
            if selected_pattern not in PATTERN_TO_CATEGORY:
                selected_pattern = "Adams"

            category = PATTERN_TO_CATEGORY[selected_pattern]

            try:
                size_val = int(request.form.get("fly_size") or 16)
            except ValueError:
                size_val = 16
            if size_val not in FLY_SIZES:
                size_val = 16

            game.current_fly = Fly(selected_pattern, category, size_val)
            last_message = f"Fly selected: {selected_pattern}, {category}, size {size_val}."
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
        leader_line_types=LEADER_LINE_TYPES,
        leader_diameters=LEADER_DIAMETERS,
        rod_lengths=ROD_LENGTHS,
        rod_weights=ROD_WEIGHTS,
        rod_materials=ROD_MATERIALS,
        fly_categories=FLY_CATEGORIES,
        fly_patterns=FLY_PATTERNS,
        fly_sizes=FLY_SIZES,
    )


if __name__ == "__main__":
    # Run the Flask dev server
    app.run(debug=True)
