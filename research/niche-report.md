# Shorts strategy: what 65 viral shorts show, top 10 niches, top 10 videos, time to monetization

October 2026. Shorts only.

## The study

- **65 shorts watched and analyzed** by Gemini, out of 86 real links found by web search
  across 12 niches (21 were unreadable). Included: 15 Zack D. Films clips (inside "Nuclear
  Engineer Reacts" shorts), 6 Kurzgesagt shorts, plus space, survival, animal, human body,
  psychology, money, scary-fact and how-it-works shorts.
- Each analysis records the hook, structure, cuts, shot length, camera distance, visual style,
  captions, voice speed, music, ending, emotion and why it works. Raw data:
  `research/viral-shorts/analyses.json`; script: `research/viral_study.py`.
- **Limits:** YouTube is blocked from this session, so videos came from web search, not
  YouTube's own "most viewed" ranking, and some are from small channels. Like counts were read
  off pages in batches and are **unreliable** (one Kurzgesagt short read as 371K likes alone and
  3.5K in a batch). So the patterns below come from what was *in* the videos, and the niche
  ranking also uses known channel scale (`research/channels.md`).

## What the 65 shorts have in common (measured)

| Pattern | Finding |
|---|---|
| Length | Median **60 s**; the best "what if" shorts are 55-60 s |
| Shot length | Median **2.7 s** per shot (Kurzgesagt ~2.0 s, Zack D. clips ~3.1 s) |
| Speaking pace | Median **150 words/min** |
| Hook | **Question** 25/65, shocking claim 16, visual shock 13, story cold-open 6, countdown 4 |
| Emotion | **Curiosity** 44/65, then humor 9, awe 8, fear 4 |
| Ending | **Abrupt/loop** 26, punchline 17, call to action 14, question 4 |
| Captions | Word-by-word 32, phrase 20, none 9; mostly **middle of screen** (36), bottom 19 |
| Camera | Mostly **medium** shots; Zack D. clips about 60% medium, 20% wide, 20% close |
| Look | Mixed visuals 32, pure 3D 13, 2D animation 8 |
| Retention tricks | Fast cuts every 1-3 s, word-by-word highlighted captions, a hypothetical that escalates |

The winners in the sample were all **one hypothetical question answered with escalating
consequences**: universe size comparisons, "What if a white hole and black hole collided?",
"Let's make Earth twice as large", "What happens if a grain of sand hits Earth at light speed?",
"How many moons could Earth handle?", "What's the deadliest animal on Earth?".

## Top 10 niches for this channel

| # | Niche | Evidence | Pipeline fit |
|---|---|---|---|
| 1 | **"What if" hypotheticals: body and physics** (Zack D. Films / Kurzgesagt style) | Most of the top performers; curiosity hook; endless topics | Strong |
| 2 | **Space and scale** (size comparisons, "what if the Sun...") | Top short in the sample; awe emotion | Strong (planet scene) |
| 3 | **Survival scenarios** ("What if you fell into...") | Question hook plus "would I survive?" comments | Strong |
| 4 | **Deadly and weird animals** | "Deadliest animal" format performs; cute-vs-deadly contrast | Medium (needs animal models) |
| 5 | **Inside the human body** | Fits our scenes; plain explainers did poorly, so frame them as "what if" | Strong |
| 6 | **History "what if you lived then"** | Strong genre on YouTube overall; not well covered in sample | Medium |
| 7 | **Mysteries and strange places** | Strong storytelling genre; not covered in sample | Medium |
| 8 | **How it works (3D cutaways)** | Sample shorts were slow (89 wpm, 4 s shots) and weak | Medium |
| 9 | **Psychology facts** | Crowded; sample shorts performed poorly | Weak |
| 10 | **Money stories** | Mostly live-action interviews; hard to make in 3D | Weak |

**Lesson from the weak niches:** plain explainers ("how an engine works", "human body facts")
underperformed. The same topics work when framed as a hypothetical with stakes for *you*:
"What if your heart stopped for 60 seconds?" rather than "How the heart works".

## The shorts formula (apply to every video)

1. **Hook, 0-2 s:** a "What if you...?" question, max 10 words. The voice starts on frame 1.
2. **Answer, 2-5 s:** the first consequence immediately.
3. **Escalate:** 4-6 beats, each more extreme; one fact per line; ~150 words per minute.
4. **Twist** near the end: one surprising true detail.
5. **End abruptly** on a punchline or question that flows back into the hook, so the loop
   replays.
6. **Length:** 45-60 s. **Shots:** a new one every 2-3 s, mostly medium framing.
7. **Captions:** word-by-word with the current word highlighted (the most common style in the
   sample). Keep them small and lower on screen, per the owner's feedback, which overrides the
   sample's middle-of-screen habit.

## Top 10 shorts to make first

| # | Title / hook | Niche |
|---|---|---|
| 1 | What if you don't sleep for 11 days? (already made) | Body |
| 2 | What if Earth were twice as big? | Space |
| 3 | What if you fell into the Mariana Trench? | Survival |
| 4 | What happens to your body in space without a suit? | Body/space |
| 5 | What if the Moon disappeared tonight? | Space |
| 6 | What if you got struck by lightning? | Survival/body |
| 7 | What if your heart stopped for 60 seconds? | Body |
| 8 | What if you stood next to a black hole? | Space |
| 9 | What if a mosquito bit you in 1347? | History/animals |
| 10 | What if you fell through thin ice? | Survival |

Check every fact before publishing.

## How long until a Shorts channel is monetized

| Tier | Requirement (Shorts path) | What you get |
|---|---|---|
| Early access | 500 subs + 3 uploads in 90 days + **3M Shorts views in 90 days** | Memberships, Super Thanks, Shopping; no ad money |
| Full YPP, applying before Feb 1, 2027 | 1,000 subs + **10M engaged Shorts views in 90 days** | Shorts ad revenue share |
| Full YPP, applying from Feb 1, 2027 | 1,000 subs + **20M engaged Shorts views in 90 days** | Same |

Only engaged views count (replays don't). 10M in 90 days is ~110,000 views/day; 20M is ~220,000.
New channels' shorts usually get a few hundred to a few thousand views each, so the target is
reached through breakout shorts (1M+), not volume alone.

| Scenario (daily shorts, improving weekly) | Early access (3M) | Full monetization |
|---|---|---|
| Best case: a 5M+ breakout in the first 6-8 weeks | ~1-2 months | ~2-3 months, under the 10M rule if before Feb 1, 2027 |
| Realistic, if the videos are good: several 500k-2M shorts | ~2-4 months | ~4-8 months, likely under the 20M rule |
| Common outcome: no breakout | Maybe never | Never, unless the format improves |

**Pay:** Shorts earn roughly $50-500 per million views, so 10M views is roughly $500-5,000,
depending on the audience's country and niche.

**What raises the odds:** post daily; read each short's retention graph and fix the first
3 seconds when viewers leave; double down on topics that beat the channel average; answer
comments and turn the best ones into new shorts; keep the facts accurate and the look
consistent (YouTube demonetizes "mass-produced" AI content).

## Sources

- YPP tiers and the Feb 2027 change: [AIR Media-Tech YPP guide 2026](https://air.io/en/monetization/youtube-partner-program-requirements-2026-the-complete-guide),
  [Tubefilter, Aug 10 2026](https://www.tubefilter.com/2026/08/10/youtube-partner-program-ad-eligibility-requirements-shorts/amp/),
  [YouTube blog: qualified watch hours and Shorts views](https://blog.youtube/news-and-events/youtube-monetization-qualified-watch-hours-shorts-views/)
- Shorts RPM ranges (vendor blog, rough): [gofaceless.ai](https://www.gofaceless.ai/en/blog/youtube-shorts-monetization)
- Channel scale and styles: `research/channels.md`
