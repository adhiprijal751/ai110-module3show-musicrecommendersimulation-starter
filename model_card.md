# 🎧 Model Card: VibeFinder 1.0

---

## 1. Model Name

**VibeFinder 1.0** — a content-based music recommender simulation built for classroom exploration.

---

## 2. Goal / Task

VibeFinder tries to answer one question: *given a description of what a listener wants to feel right now, which songs in the catalog come closest to that feeling?*

It does not predict what a user will click. It does not learn from past behaviour. It takes a snapshot of stated preferences (a genre, a mood, an energy level, an emotional tone, and a tempo) and scores every song in the catalog against those preferences using a fixed mathematical formula. The output is a ranked list of the top 5 matches.

---

## 3. Data Used

- **Catalog size:** 18 songs
- **Source:** A hand-crafted CSV (`data/songs.csv`) — not real listening data
- **Base features (10):** id, title, artist, genre, mood, energy (0–1), tempo_bpm, valence (0–1), danceability (0–1), acousticness (0–1)
- **Extended features added (5):** popularity (0–100), release_decade, instrumentalness (0–1), loudness (0–1), explicit_mood_tags (pipe-separated detailed tags)
- **Genres represented:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, blues, edm, country, classical, hip-hop, metal, r&b, folk (15 genres)
- **Moods represented:** happy, chill, intense, relaxed, focused, moody, sad, energetic, peaceful, aggressive, romantic, nostalgic (12 moods)

**Key limits:** Several genres have only one song (rock, blues, classical, metal, country, r&b, folk). The catalog skews toward Western pop and electronic music. All numeric values were assigned by hand — they are plausible estimates, not measured from real audio.

---

## 4. Algorithm Summary

Every song in the catalog gets a **compatibility score** against the user's preferences. Here is how each feature contributes to that score:

- **Genre match:** If the song's genre exactly matches what the user requested, it earns 3.0 points. If not, it earns 0. There is no partial credit.
- **Mood match:** Same idea — an exact match earns 2.0 points, a mismatch earns 0.
- **Energy closeness:** The closer the song's energy is to the user's target, the more points it earns (up to 2.0). Being exactly right earns the full 2.0; being way off earns close to 0. The penalty grows faster the further away you are (squared difference).
- **Valence (emotional tone) closeness:** Same approach, worth up to 1.5 points.
- **Tempo closeness:** Same approach, worth up to 1.0 points.

The scores from all five features are added together. The maximum possible score with default weights is **9.5** (a perfect match on everything).

Songs are then sorted from highest to lowest score, and the top 5 are returned as recommendations.

**Scoring modes** let you change which feature matters most without rewriting the formula. "Genre-First" triples the genre weight; "Mood-First" prioritises the emotional label; "Energy-Focused" rewards closeness in energy above everything else.

**Diversity penalty** (optional): after scoring, any song whose artist or genre already appears earlier in the results list has points subtracted, pushing repeated artists and genres lower so the top 5 is more varied.

---

## 5. Observed Behavior / Biases

**Genre weight dominance.** With genre worth 3.0 out of 9.5 points (32% of the total), a song can score 9.02 out of 9.5 even when its energy is 0.45 points off from what the user asked for — because genre and mood together add up to 5.0 points that no numeric penalty can fully overcome. This was observed directly in the "Conflicting: Sad but High-Energy" test.

**The genre desert problem.** When the user's preferred genre does not exist in the catalog (e.g., reggae), every song loses the full 3.0 genre bonus automatically. The highest achievable score drops from 9.5 to 6.5. The system returns the numerically nearest song, which may sound nothing like what the user wanted. Users with niche or missing genres are structurally disadvantaged compared to users whose genres are represented.

**Unequal catalog coverage.** Lofi has 3 songs; rock, metal, and classical each have 1. A lofi user gets 3 genre matches in their top results; a rock user gets 1, and the second result drops 3+ points. The recommender is only as diverse as the catalog it can draw from.

**Energy-mood correlation is not modeled.** "Sad" music is almost always low-energy in real life; "energetic" music is rarely melancholic. But the scoring formula treats energy and mood as fully independent dimensions. A user who asks for "sad + high energy" gets served a slow blues track (correct emotionally, wrong rhythmically) because the 5.0 categorical score overwhelms the numeric penalty.

**Diversity collapse without the penalty.** Without the diversity function, the top 5 results for a lofi user are all lofi tracks (sometimes all by the same artist), which creates a filter bubble. The diversity penalty fixes this but is an opt-in post-processing step — it is not baked into the scoring.

---

## 6. Evaluation Process

Six user profiles were tested:

| Profile | Type | Top score | Key finding |
|---|---|---|---|
| High-Energy Pop Fan | Normal | 9.50 | Perfect match existed; results felt correct |
| Chill Lofi Studier | Normal | 9.50 (tied) | Two songs identical on all 5 features |
| Deep Intense Rock | Normal | 9.50 | One rock song; large drop-off after #1 |
| Conflicting (Sad + High-Energy) | Adversarial | 9.02 | Genre/mood won over large energy mismatch |
| Genre Desert (Reggae) | Adversarial | 6.49 | Capped by missing genre; country song surfaced |
| All-Neutral (Jazz) | Adversarial | 9.40 | Genre still dominated with neutral numerics |

Four scoring modes were compared on the same Chill Lofi profile. "Mood-First" mode promoted `Spacewalk Thoughts` (ambient/chill) from #4 to #3, showing that reducing genre weight unlocks genre-diverse alternatives when mood aligns. "Energy-Focused" mode kept the same top 3 but narrowed score gaps.

The weight-shift experiment (genre 3.0→1.5, energy 2.0→4.0) was tested on the rock profile. Shatter Zone (metal, energy 0.97) rose from #4 to #3 and Night Drive Loop dropped from #3 to #5. Rankings changed, but did not improve — Shatter Zone is metal, not rock.

The diversity penalty was tested on the lofi profile. Without it: #1, #2, #3 are all lofi, two by the same artist (LoRoom). With it: Focus Flow (LoRoom) drops to #4 and Spacewalk Thoughts (a different artist and genre) enters at #3.

---

## 7. Intended Use and Non-Intended Use

**Intended use:**
- A classroom simulation for learning how content-based recommendation systems work
- Exploring how numeric weights affect ranked outputs
- Practicing the design of scoring functions and evaluation of bias

**Not intended for:**
- Recommending music to real users — the catalog is too small (18 songs) and the feature values are hand-assigned, not measured
- Any commercial or production use
- Drawing conclusions about what real users prefer — there is no user feedback loop
- Users with genres not represented in the catalog — the system will silently give them irrelevant results with no warning

---

## 8. Ideas for Improvement

1. **Soft genre matching.** Instead of binary match/no-match, measure genre similarity — "lofi" and "ambient" are closer than "lofi" and "metal." A genre distance matrix would make the system far more useful for Genre Desert users.

2. **Dynamic weight learning.** Let users thumbs-up or thumbs-down three songs, then adjust the feature weights based on which features drove the picks they liked. This would replace the hand-tuned weights with something grounded in actual user feedback.

3. **Larger and more representative catalog.** With one song per niche genre, the recommender cannot provide meaningful diversity for those users. Even tripling the catalog to 50 songs would significantly improve results.

---

## 9. Personal Reflection

**Biggest learning moment:** The moment that surprised me most was discovering how much a single weight controls everything. I set genre to 3.0 because it felt like "a strong preference." But when I tested the "Conflicting: Sad but High-Energy" profile, I saw that a song could score 9.02 out of 9.5 while being energetically wrong by nearly half the entire scale. The genre weight was not just "strong" — it was so dominant that a correct genre label could override almost everything else. That made me realize that setting weights by intuition is dangerous. You need to test them against adversarial inputs before you trust them.

**How AI tools helped — and where I had to double-check:** AI assistance was fast for generating boilerplate code (CSV loading, list comprehensions, docstrings) and for describing patterns I already understood ("show me a sorted list using a lambda"). But it consistently over-simplified the scoring logic when I didn't give it enough context — for example, first drafts used absolute difference instead of squared difference, which changes how tolerant the system is of small errors. I had to explain the *goal* (penalise large gaps more than small gaps) before the implementation matched my intent. The rule I learned: AI writes good *syntax*; you still have to own the *semantics*.

**What surprised me about simple algorithms "feeling" like recommendations:** When I ran the High-Energy Pop Fan profile and got Sunrise City at a perfect 9.50 with the explanation "genre match | mood match | energy similarity | valence similarity | tempo similarity," it genuinely *felt* like the right answer — even though the math is just five multiplications and an addition. The surprise was that "feeling right" and "being right" are actually two different things that happened to align here. For the Conflicting profile, the math felt wrong even though it was technically correct. The algorithm did exactly what I told it to do; the problem was that my formula didn't capture the real constraint. That gap — between what the formula computes and what the user actually wants — is where the interesting design work lives.

**What I would try next:** I would add a short feedback loop — show the user their top-3, ask them to rate each one (thumbs up/down/skip), and use those ratings to adjust the weights automatically. Even with 3 ratings you could tell whether genre or energy is mattering more to that specific user and narrow in on what they actually want, rather than asking them to describe it in advance.

