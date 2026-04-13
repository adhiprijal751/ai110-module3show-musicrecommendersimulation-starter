from typing import List, Dict, Tuple
from dataclasses import dataclass
import csv


@dataclass
class Song:
    """Represents a song and its audio and genre attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Stores a listener's categorical and numerical taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """Ranks catalog songs against a UserProfile using the weighted scoring formula."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k songs ranked by compatibility score with the given user profile."""
        prefs = {
            "genre":     user.favorite_genre,
            "mood":      user.favorite_mood,
            "energy":    user.target_energy,
            "valence":   0.65,   # neutral default — not stored in UserProfile
            "tempo_bpm": 100,    # neutral default — not stored in UserProfile
        }
        pairs = [(song, _song_to_dict(song)) for song in self.songs]
        ranked = sorted(pairs, key=lambda p: score_song(prefs, p[1])[0], reverse=True)
        return [song for song, _ in ranked[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a pipe-separated string of scoring reasons for a given song."""
        prefs = {
            "genre":     user.favorite_genre,
            "mood":      user.favorite_mood,
            "energy":    user.target_energy,
            "valence":   0.65,
            "tempo_bpm": 100,
        }
        _, reasons = score_song(prefs, _song_to_dict(song))
        return " | ".join(reasons)


def _song_to_dict(song: Song) -> Dict:
    """Convert a Song dataclass to a plain dictionary for use with score_song."""
    return {
        "id": song.id, "title": song.title, "artist": song.artist,
        "genre": song.genre, "mood": song.mood, "energy": song.energy,
        "tempo_bpm": song.tempo_bpm, "valence": song.valence,
        "danceability": song.danceability, "acousticness": song.acousticness,
    }


def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of dicts with numeric fields properly typed."""
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    int(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song against user preferences; returns (total_score, reasons).

    Categorical features (genre, mood) award full weight on exact match.
    Numerical features (energy, valence, tempo_bpm) use squared-difference
    similarity: sim = 1 − (pref − song)², scaled by the feature weight.
    Maximum possible score is 9.5 (perfect match on all five features).
    """
    WEIGHTS = {"genre": 3.0, "mood": 2.0, "energy": 2.0, "valence": 1.5, "tempo_bpm": 1.0}
    score = 0.0
    reasons = []

    # --- categorical features: binary match ---
    if song.get("genre") == user_prefs.get("genre"):
        score += WEIGHTS["genre"]
        reasons.append(f"genre match (+{WEIGHTS['genre']})")

    if song.get("mood") == user_prefs.get("mood"):
        score += WEIGHTS["mood"]
        reasons.append(f"mood match (+{WEIGHTS['mood']})")

    # --- numerical features: squared-difference similarity ---
    if "energy" in user_prefs:
        sim = 1.0 - (user_prefs["energy"] - song["energy"]) ** 2
        pts = round(WEIGHTS["energy"] * sim, 2)
        score += pts
        reasons.append(f"energy similarity (+{pts})")

    if "valence" in user_prefs:
        sim = 1.0 - (user_prefs["valence"] - song["valence"]) ** 2
        pts = round(WEIGHTS["valence"] * sim, 2)
        score += pts
        reasons.append(f"valence similarity (+{pts})")

    if "tempo_bpm" in user_prefs:
        sim = 1.0 - ((user_prefs["tempo_bpm"] - song["tempo_bpm"]) / 200.0) ** 2
        pts = round(WEIGHTS["tempo_bpm"] * sim, 2)
        score += pts
        reasons.append(f"tempo similarity (+{pts})")

    return round(score, 4), reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Score all songs, sort highest-to-lowest, return top-k as (song, score, explanation) tuples.

    Uses sorted() over list.sort() so the original catalog list is never mutated.
    """
    scored = [(song, *score_song(user_prefs, song)) for song in songs]
    ranked = sorted(scored, key=lambda x: x[1], reverse=True)
    return [(song, score, " | ".join(reasons)) for song, score, reasons in ranked[:k]]
