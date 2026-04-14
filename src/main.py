"""
Command line runner for the Music Recommender Simulation.

Run from the project root:
    python -m src.main
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from recommender import load_songs, recommend_songs, diversify, SCORING_MODES

# Challenge 4: use tabulate for formatted tables; fall back to plain ASCII
try:
    from tabulate import tabulate
    _TABULATE = True
except ImportError:
    _TABULATE = False


# ── Challenge 4: table formatter ─────────────────────────────────────────────

def _truncate(text: str, width: int) -> str:
    """Truncate a string to width, adding ellipsis if cut."""
    return text if len(text) <= width else text[: width - 1] + "…"


def print_table(recs: list, max_score: float) -> None:
    """Print a formatted recommendation table.

    Uses tabulate when available; falls back to fixed-width ASCII columns.
    """
    rows = []
    for rank, (song, score, explanation) in enumerate(recs, start=1):
        short_why = _truncate(explanation, 60)
        rows.append([
            f"#{rank}",
            _truncate(song["title"], 24),
            _truncate(song["artist"], 18),
            song["genre"],
            f"{score:.2f}/{max_score:.1f}",
            short_why,
        ])

    headers = ["#", "Title", "Artist", "Genre", "Score", "Reasons"]

    if _TABULATE:
        print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))
    else:
        col_w = [4, 26, 20, 12, 11, 62]
        sep = "  ".join("-" * w for w in col_w)
        header_row = "  ".join(h.ljust(w) for h, w in zip(headers, col_w))
        print(header_row)
        print(sep)
        for row in rows:
            print("  ".join(str(v).ljust(w) for v, w in zip(row, col_w)))
    print()


# ── helpers ───────────────────────────────────────────────────────────────────

def section(title: str) -> None:
    print(f"\n{'━'*75}")
    print(f"  {title}")
    print(f"{'━'*75}\n")


def run_profile(label: str, prefs: dict, songs: list, mode: str = "balanced",
                use_diversity: bool = False, weights: dict = None) -> None:
    """Run one profile and print the formatted results table."""
    recs = recommend_songs(prefs, songs, k=5, mode=mode, weights=weights)
    if use_diversity:
        # fetch a deeper list so diversity re-ranking has material to work with
        full = recommend_songs(prefs, songs, k=len(songs), mode=mode, weights=weights)
        recs = diversify(full)[:5]

    resolved = weights if weights is not None else SCORING_MODES.get(mode, SCORING_MODES["balanced"])
    max_score = sum(resolved.values())
    # add extended-feature weights to max_score if present
    for key in ("popularity", "release_decade", "instrumentalness", "loudness", "explicit_mood_tags"):
        if key in prefs:
            max_score += resolved.get(key, {"popularity": 0.5, "release_decade": 1.0,
                                            "instrumentalness": 1.0, "loudness": 1.0,
                                            "explicit_mood_tags": 2.0}[key])

    diversity_tag = " + DIVERSITY PENALTY" if use_diversity else ""
    mode_tag = f"[{mode.upper()}]{diversity_tag}"
    print(f"  Profile : {label}")
    print(f"  Mode    : {mode_tag}")
    print(f"  Prefs   : {', '.join(f'{k}={v}' for k, v in prefs.items())}\n")
    print_table(recs, max_score)


# ── profiles ─────────────────────────────────────────────────────────────────

CHILL_LOFI = {
    "genre": "lofi", "mood": "chill",
    "energy": 0.38,  "valence": 0.58, "tempo_bpm": 76,
}

HIGH_ENERGY_POP = {
    "genre": "pop",  "mood": "happy",
    "energy": 0.85,  "valence": 0.82, "tempo_bpm": 125,
}

INTENSE_ROCK = {
    "genre": "rock", "mood": "intense",
    "energy": 0.91,  "valence": 0.45, "tempo_bpm": 150,
}

# Challenge 1 extended profile — includes the five new features
NOSTALGIC_ACOUSTIC = {
    "genre": "folk",   "mood": "nostalgic",
    "energy": 0.35,    "valence": 0.65,  "tempo_bpm": 95,
    "popularity":       50,
    "release_decade":   2010,
    "instrumentalness": 0.40,
    "loudness":         0.45,
    "explicit_mood_tags": {"nostalgic", "warm", "bittersweet"},
}


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"\nLoaded songs: {len(songs)}")

    # ── Challenge 2: scoring modes side-by-side ───────────────────────────────
    section("CHALLENGE 2 — Scoring Modes: same profile, four different lenses")
    for mode in SCORING_MODES:
        run_profile(f"Chill Lofi Studier", CHILL_LOFI, songs, mode=mode)

    # ── Challenge 3: diversity penalty ────────────────────────────────────────
    section("CHALLENGE 3 — Diversity Penalty: before vs. after")
    print("  WITHOUT diversity penalty:\n")
    run_profile("Chill Lofi Studier", CHILL_LOFI, songs, mode="balanced")
    print("  WITH diversity penalty (artist_penalty=1.5, genre_penalty=0.75):\n")
    run_profile("Chill Lofi Studier", CHILL_LOFI, songs, mode="balanced", use_diversity=True)

    # ── Challenge 1: extended features ────────────────────────────────────────
    section("CHALLENGE 1 — Extended Features: popularity · era · instrumentalness · loudness · tags")
    run_profile("Nostalgic Acoustic (extended)", NOSTALGIC_ACOUSTIC, songs, mode="balanced")

    # ── standard profiles for reference ──────────────────────────────────────
    section("REFERENCE — Standard Profiles (balanced mode)")
    run_profile("High-Energy Pop Fan",  HIGH_ENERGY_POP, songs)
    run_profile("Deep Intense Rock",    INTENSE_ROCK,    songs)


if __name__ == "__main__":
    main()
