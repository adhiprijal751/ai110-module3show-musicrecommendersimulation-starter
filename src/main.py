"""
Command line runner for the Music Recommender Simulation.

Run from the project root:
    python -m src.main
"""

import sys
import os

# Make sure src/ is on the path so 'from recommender import ...' resolves
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    user_prefs = {
        "genre":     "pop",
        "mood":      "happy",
        "energy":    0.80,
        "valence":   0.80,
        "tempo_bpm": 118,
    }

    print("User Profile:")
    for key, val in user_prefs.items():
        print(f"  {key:<12}: {val}")
    print()

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("Top 5 Recommendations:")
    print("-" * 75)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"  #{rank}  {song['title']} — {song['artist']}")
        print(f"       Score : {score:.2f} / 9.50")
        print(f"       Why   : {explanation}")
        print()


if __name__ == "__main__":
    main()
