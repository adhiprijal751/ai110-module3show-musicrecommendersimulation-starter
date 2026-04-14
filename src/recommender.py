from typing import List, Dict, Tuple
from dataclasses import dataclass
import csv


# ── Challenge 2: Scoring mode presets ────────────────────────────────────────
# Each mode re-weights the five base features to favour a different dimension.
# Pass the mode name to recommend_songs() via the `mode` parameter.

SCORING_MODES: Dict[str, Dict[str, float]] = {
    # Default: balanced across all five features (max score 9.5)
    "balanced":      {"genre": 3.0, "mood": 2.0, "energy": 2.0, "valence": 1.5, "tempo_bpm": 1.0},
    # Genre-First: heavily rewards matching the requested genre (max 9.0)
    "genre_first":   {"genre": 6.0, "mood": 1.0, "energy": 1.0, "valence": 0.5, "tempo_bpm": 0.5},
    # Mood-First: prioritises the emotional label over sonic features (max 10.0)
    "mood_first":    {"genre": 1.0, "mood": 5.0, "energy": 2.0, "valence": 1.5, "tempo_bpm": 0.5},
    # Energy-Focused: rewards energy closeness most; genre matters less (max 10.0)
    "energy_focused":{"genre": 1.5, "mood": 1.0, "energy": 5.0, "valence": 1.5, "tempo_bpm": 1.0},
}


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
            "valence":   0.65,
            "tempo_bpm": 100,
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
    """Read songs.csv and return a list of dicts with all fields properly typed.

    Core fields (energy, valence, etc.) are cast to float/int.
    Challenge-1 extended fields (popularity, release_decade, instrumentalness,
    loudness, explicit_mood_tags) are parsed when present; missing columns are
    silently skipped so the loader stays backward-compatible.
    """
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            song: Dict = {
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
            }
            # Challenge 1: extended attributes (optional columns)
            if "popularity" in row:
                song["popularity"] = int(row["popularity"])
            if "release_decade" in row:
                song["release_decade"] = int(row["release_decade"])
            if "instrumentalness" in row:
                song["instrumentalness"] = float(row["instrumentalness"])
            if "loudness" in row:
                song["loudness"] = float(row["loudness"])
            if "explicit_mood_tags" in row:
                # stored as pipe-separated string; parse to frozenset for fast intersection
                song["explicit_mood_tags"] = frozenset(
                    t.strip() for t in row["explicit_mood_tags"].split("|") if t.strip()
                )
            songs.append(song)
    return songs


def score_song(user_prefs: Dict, song: Dict, weights: Dict = None) -> Tuple[float, List[str]]:
    """Score one song against user preferences; returns (total_score, reasons).

    Base scoring (five features):
      - genre, mood: binary match, full weight on exact label match.
      - energy, valence, tempo_bpm: squared-difference similarity
        sim = 1 - (pref - song)², scaled by feature weight.

    Challenge-1 extended scoring (triggered only when the key appears in user_prefs):
      - popularity (0-100): proximity reward, normalised over 100.
      - release_decade (e.g. 2010): proximity reward, normalised over 60 years.
      - instrumentalness (0-1): squared-difference similarity.
      - loudness (0-1): squared-difference similarity.
      - explicit_mood_tags (set of strings): fraction of user's requested tags
        that appear in the song's tag set.

    Pass a custom weights dict or use the SCORING_MODES presets via recommend_songs().
    """
    DEFAULT_WEIGHTS = {"genre": 3.0, "mood": 2.0, "energy": 2.0, "valence": 1.5, "tempo_bpm": 1.0}
    W = {**DEFAULT_WEIGHTS, **(weights or {})}
    score = 0.0
    reasons = []

    # ── base categorical features ─────────────────────────────────────────────
    if song.get("genre") == user_prefs.get("genre"):
        score += W["genre"]
        reasons.append(f"genre match (+{W['genre']})")

    if song.get("mood") == user_prefs.get("mood"):
        score += W["mood"]
        reasons.append(f"mood match (+{W['mood']})")

    # ── base numerical features ───────────────────────────────────────────────
    if "energy" in user_prefs:
        sim = 1.0 - (user_prefs["energy"] - song["energy"]) ** 2
        pts = round(W["energy"] * sim, 2)
        score += pts
        reasons.append(f"energy similarity (+{pts})")

    if "valence" in user_prefs:
        sim = 1.0 - (user_prefs["valence"] - song["valence"]) ** 2
        pts = round(W["valence"] * sim, 2)
        score += pts
        reasons.append(f"valence similarity (+{pts})")

    if "tempo_bpm" in user_prefs:
        sim = 1.0 - ((user_prefs["tempo_bpm"] - song["tempo_bpm"]) / 200.0) ** 2
        pts = round(W["tempo_bpm"] * sim, 2)
        score += pts
        reasons.append(f"tempo similarity (+{pts})")

    # ── Challenge 1: extended features ───────────────────────────────────────
    if "popularity" in user_prefs and "popularity" in song:
        sim = 1.0 - ((user_prefs["popularity"] - song["popularity"]) / 100.0) ** 2
        pts = round(W.get("popularity", 0.5) * sim, 2)
        score += pts
        reasons.append(f"popularity proximity (+{pts})")

    if "release_decade" in user_prefs and "release_decade" in song:
        sim = 1.0 - ((user_prefs["release_decade"] - song["release_decade"]) / 60.0) ** 2
        pts = round(W.get("release_decade", 1.0) * sim, 2)
        score += pts
        reasons.append(f"era match (+{pts})")

    if "instrumentalness" in user_prefs and "instrumentalness" in song:
        sim = 1.0 - (user_prefs["instrumentalness"] - song["instrumentalness"]) ** 2
        pts = round(W.get("instrumentalness", 1.0) * sim, 2)
        score += pts
        reasons.append(f"instrumentalness proximity (+{pts})")

    if "loudness" in user_prefs and "loudness" in song:
        sim = 1.0 - (user_prefs["loudness"] - song["loudness"]) ** 2
        pts = round(W.get("loudness", 1.0) * sim, 2)
        score += pts
        reasons.append(f"loudness proximity (+{pts})")

    if "explicit_mood_tags" in user_prefs and "explicit_mood_tags" in song:
        user_tags = set(user_prefs["explicit_mood_tags"])
        song_tags = song["explicit_mood_tags"]  # frozenset from load_songs
        if user_tags:
            overlap = len(user_tags & song_tags) / len(user_tags)
            pts = round(W.get("explicit_mood_tags", 2.0) * overlap, 2)
            score += pts
            reasons.append(f"tag overlap {overlap:.0%} (+{pts})")

    return round(score, 4), reasons


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    weights: Dict = None,
    mode: str = "balanced",
) -> List[Tuple[Dict, float, str]]:
    """Score all songs, sort highest-to-lowest, return top-k as (song, score, explanation) tuples.

    Challenge 2: pass `mode` to select a named weight preset from SCORING_MODES.
    An explicit `weights` dict takes precedence over the mode preset.
    Uses sorted() — never mutates the original catalog list.
    """
    resolved_weights = weights if weights is not None else SCORING_MODES.get(mode, SCORING_MODES["balanced"])
    scored = [(song, *score_song(user_prefs, song, resolved_weights)) for song in songs]
    ranked = sorted(scored, key=lambda x: x[1], reverse=True)
    return [(song, score, " | ".join(reasons)) for song, score, reasons in ranked[:k]]


def diversify(
    ranked: List[Tuple[Dict, float, str]],
    artist_penalty: float = 1.5,
    genre_penalty: float = 0.75,
) -> List[Tuple[Dict, float, str]]:
    """Challenge 3: re-rank results to prevent artist and genre clustering.

    Walks the ranked list sequentially. Any song whose artist has already
    appeared has `artist_penalty` subtracted from its score; any song whose
    genre has already appeared has `genre_penalty` subtracted. The list is
    then re-sorted so duplicate-heavy clusters drop lower and diverse picks
    bubble up.
    """
    seen_artists: set = set()
    seen_genres: set = set()
    adjusted = []
    for song, score, explanation in ranked:
        penalty = 0.0
        if song["artist"] in seen_artists:
            penalty += artist_penalty
        if song["genre"] in seen_genres:
            penalty += genre_penalty
        adjusted.append((song, round(score - penalty, 4), explanation))
        seen_artists.add(song["artist"])
        seen_genres.add(song["genre"])
    return sorted(adjusted, key=lambda x: x[1], reverse=True)
