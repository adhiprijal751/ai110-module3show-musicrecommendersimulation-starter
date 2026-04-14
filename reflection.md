# Reflection: Comparing User Profiles

---

## Profile Pair 1: High-Energy Pop Fan vs. Deep Intense Rock

Both profiles ask for high energy (0.85 and 0.91 respectively) and both get a perfect 9.50 score for their top result. But after #1, their experiences diverge sharply.

The pop fan's #2 is Gym Hero at 7.49. It earns 3.0 points for matching "pop" genre and almost full energy/valence/tempo points — it loses only the 2.0 mood bonus because its mood is "intense" instead of "happy." So the drop from #1 to #2 is exactly 2.0 points, the mood weight.

The rock fan's #2 is Gym Hero at 6.34. It earns the 2.0 mood bonus (both are "intense") but gets 0 for genre since it's "pop" not "rock." The drop from #1 to #2 is 3.16 points.

What this tells us: the rock user gets a far worse "second choice" not because their taste is harder to serve, but because rock is represented by only one song in the catalog. After Storm Runner, the system has nothing left that matches genre. The pop fan has two pop songs (Sunrise City and Gym Hero), so even the second result is a reasonably close match.

**Plain language explanation:** Imagine a music store with 18 CDs. The lofi section has three shelves; the rock section has one. A rock fan walks in wanting intense rock music — they find their one perfect album immediately. But if they want a second option, the clerk just shrugs and points to "intense music in general." The store isn't broken; it just doesn't stock enough rock.

---

## Profile Pair 2: Chill Lofi Studier vs. Genre Desert (Reggae)

Both profiles want calm, mid-low-energy music in the 70–95 BPM range with warm valence. The lofi studier says their genre is "lofi"; the reggae fan says theirs is "reggae."

The lofi studier's top two songs tie at 9.50. Both Midnight Coding and Library Rain match on all five dimensions — they're quiet, slow, lofi, and chill. The whole top-3 is lofi music, which is exactly what the user asked for.

The reggae fan's top result is Sunset Highway at 6.49 — a country song. It matches "relaxed" mood and its energy/tempo/valence are close to what was asked for. But the country genre had no bearing on the request. The user asked for reggae and got country because those features happened to line up numerically.

The 3.01-point gap between the two profiles' top scores (9.50 vs. 6.49) comes almost entirely from the 3.0 genre weight. The lofi studier earns it; the reggae fan cannot earn it because no reggae song exists in the catalog. Every song the reggae fan is shown starts 3.0 points behind where it could be.

**Plain language explanation:** If you walk into a restaurant and order a dish that's not on the menu, the waiter brings you the closest thing they have. It might still taste fine, but you didn't get what you ordered. The recommender behaves the same way — it returns the numerically nearest song, not a reggae song. There's no way for it to say "sorry, we don't have reggae."

---

## Profile Pair 3: Deep Intense Rock (Standard Weights) vs. Deep Intense Rock (Experiment)

The standard weighting (genre 3.0, energy 2.0) and the experimental weighting (genre 1.5, energy 4.0) both rank Storm Runner #1 and Gym Hero #2. The top two are immune to the weight change because Storm Runner matches everything and Gym Hero combines mood match with near-perfect energy — both factors that remain strong under either weight scheme.

The change shows up at positions #3–5. With standard weights, Night Drive Loop (synthwave, energy 0.75) is #3. With doubled energy weight, Shatter Zone (metal, energy 0.97) jumps to #3 while Night Drive Loop drops to #5. Shatter Zone's energy of 0.97 against the user's 0.91 is almost a perfect match; Night Drive Loop's 0.75 is noticeably further away. When energy is worth 4.0 instead of 2.0, that gap matters twice as much and Shatter Zone overtakes it.

Importantly, the rankings did not become "more accurate" — they became different. Shatter Zone is a metal song, not a rock song. Recommending it to a rock fan because it is energetically similar does not feel right musically. This experiment demonstrates that weight changes can shift rankings without improving relevance, and that numerical similarity is not the same as musical similarity.

**Plain language explanation:** Doubling the energy weight is like a restaurant critic suddenly deciding that "portion size" is twice as important as "taste." Your rankings change, but the winner of "biggest portion" is not necessarily the best meal. In the same way, the song that best matches your target energy level is not necessarily the best song for you.

---

## Adversarial Profile: Conflicting Sad + High-Energy

This profile was designed to expose a flaw: genre "blues," mood "sad," but energy 0.90. In real life, sad music is almost always slow and low-energy. We created a profile that asks for something that musically contradicts itself.

The system returned Empty Hallways (blues, sad, energy 0.45) at 9.02. It earned full genre and mood points (5.0 total) but lost 0.41 energy points because the song's energy is 0.45 below the requested 0.90. Every other song in the catalog got 0 for genre and 0 for mood, so even at 9.02 the blues song won by a factor of 2×.

This is actually the right behavior from a categorical perspective — the user said they want blues/sad, and they got blues/sad. But from an energy perspective, the song the system recommended is almost the polar opposite of the "high energy" request. The system cannot know that "sad blues at 88 BPM" and "high energy at 140 BPM" are physically incompatible goals. It just adds up the points independently.

**Plain language explanation:** If you tell a friend "I want something sad but really pumped up," they might laugh and say "that's basically impossible." The recommender does not laugh. It finds the saddest song it knows, notices the energy is a bit off, docks a few points, and hands it to you anyway — because its sadness still outweighs everything else in the math.

