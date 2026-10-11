# Top 10 niches, top 10 videos, and time to monetization

October 2026. **Read the method note first.**

## Method and limits

- Goal: watch ~100 viral shorts and rank niches from measurements.
- What actually happened: this cloud session can't reach YouTube, and the free Gemini key
  hit its daily limit after ~60 requests. Gemini also invented most of the video IDs it
  suggested: 33 of 223 were real, and most of those were famous long videos, not shorts in our
  niches. **Only 1 short was fully analyzed.** Raw data: `research/viral/`.
- So this report is built from: the channel research in `research/channels.md`, YouTube's
  published monetization rules, published RPM ranges, and the well-known patterns of the big
  faceless shorts channels (Zack D. Films, Jake Fellman, What If, Kurzgesagt, The Infographics
  Show, zefrank). Treat the rankings as an expert estimate, not a measurement.
- To get the real 100-video measurement: allow `youtube.com`, `www.youtube.com`, `youtu.be`
  and `googlevideo.com` in this environment's network settings, then run
  `python3 research/viral_study.py --out research/viral-v2`. It searches YouTube with real view
  counts and analyzes the top 7 per niche (needs the Gemini free quota over ~2 days, or uploaded files).

## How the niches were scored

Each niche scored 1-5 on: viral potential on Shorts, US audience fit, ad value (RPM),
fit with our free 3D pipeline (`studio/`), risk under YouTube's "inauthentic/mass-produced"
rules, and competition. Ranked by total.

## Top 10 niches

| # | Niche | Why it ranks | Pipeline fit |
|---|---|---|---|
| 1 | **3D "What if / what happens to your body"** | Proven by Zack D. Films; curiosity + mild gross-out = rewatches; endless topics | Strong: person, x-ray body, tunnel, organ scenes exist |
| 2 | **Survival scenarios ("What if you fell into...")** | Fear + "would I survive?" makes people comment; overlaps #1 | Strong: person + shatter/tunnel; needs a few new sets (water, ice, cave) |
| 3 | **Space and scale** | Awe, evergreen, strong long-form RPM; size comparisons go viral repeatedly | Strong: planet scene; add scale comparisons |
| 4 | **Inside the human body (accurate medical explainers)** | Educational = safer from demonetization, high trust | Strong; facts must be checked carefully |
| 5 | **Animated history ("What if you lived in 1347?")** | Big long-form audience; "what if you lived then" fits our hook | Medium: needs period clothes/sets |
| 6 | **Weird and deadly animals** | Huge broad appeal (zefrank, BBC clips do 10M-100M) | Medium: needs animal models |
| 7 | **How it works (3D cutaways)** | High RPM (tech/engineering), evergreen searches | Medium: needs machine models |
| 8 | **Mysteries and strange places** | Strong retention with storytelling; works long-form too | Medium: atmosphere scenes |
| 9 | **Psychology and life facts** | Cheap and fast to make, big audience | Weak differentiation; template risk |
| 10 | **Money and business stories** | Highest RPM of all (finance $8-18 long-form) | Weak for 3D; stock/graphics better |

**Avoid for this channel:** Reddit stories over gameplay (reused-content risk, saturated),
ambient/satisfying loops (repetitive-content risk), movie recaps (copyright claims), and
low-effort "scary facts" lists (crowded, weak RPM).

## Playbook for the top 4 (same core formula)

**Script formula (30-45 s, 7-9 lines):**
1. Hook (0-2 s): a "What if you...?" question, max 10 words, with the payoff implied.
2. Instant answer (2-5 s): the first consequence, no intro.
3. Escalation (3-5 beats): each line more extreme than the last; one fact per line.
4. Twist (late): a surprising true detail ("Guinness stopped tracking it").
5. Ending: a question for the comments, or a line that loops back into the hook.

**Editing:** a new shot every 2-4 s; one consistent cut style; no dead air; the voice starts
on frame 1. Wide/medium shots, close-ups rare. Captions small, 2 words, lower third.
Numbers as brief pop-ups 2-3 times per video.

**Visual style:** one recognizable character (the same person every video, so viewers know
the channel); clean studio-like sets; glowing "x-ray" cutaways to show what happens inside;
consistent palette per channel.

**Voice/sound:** confident narrator, 150-170 words per minute; subtle music; whoosh/impact
sound effects on cuts (to add: our pipeline has no SFX yet).

**Viewers:** 13-34, mostly mobile, curiosity-driven; they comment "I'd survive" and argue
about facts. Answer those comments (it boosts reach) and turn the best ones into new videos.

| Niche | Extra notes |
|---|---|
| Survival | End on "Would you survive?"; show the person, then the danger, then the body's reaction |
| Space | Use scale and size: "If the Sun were a basketball..."; slower, awe-toned narration |
| Inside the body | Cite real sources in the description; never give medical advice |

## Top 10 videos to make first

| # | Hook (title = hook) | Niche | Scenes to use |
|---|---|---|---|
| 1 | What if you don't sleep for 11 days? | Body | Done: `studio/examples/no-sleep-11-days.json` |
| 2 | What if you fell into the Mariana Trench? | Survival | person, tunnel (water), body (lungs), shatter |
| 3 | What happens to your body in space without a suit? | Body/space | person, planet, body (lungs/blood), blob |
| 4 | What if the Moon disappeared tonight? | Space | planet, person (shocked), shatter |
| 5 | What if you got struck by lightning? | Survival | person, body (heart/skin), shatter |
| 6 | What if you held your breath for 5 minutes? | Body | person (close), body (lungs/brain), tunnel |
| 7 | What if you stood next to a black hole? | Space | person, planet, tunnel, shatter |
| 8 | What if you fell through thin ice? | Survival | person, body (heart), blob |
| 9 | What if you lived through the Black Death in 1347? | History | person (tired), virus, body (blood) |
| 10 | What if you only drank energy drinks for a month? | Body | person, body (heart), tunnel (blood) |

Check every fact before publishing; accuracy is what keeps channels like this monetized.

## How long until the channel is monetized

**The rules (October 2026):**

| Tier | Requirement | What you get |
|---|---|---|
| Early access | 500 subs + 3 public uploads in 90 days + 3M Shorts views in 90 days (or 3,000 watch hours) | Memberships, Super Thanks, Shopping; **no ad money** |
| Full YPP (until Jan 31, 2027) | 1,000 subs + **10M** engaged Shorts views in 90 days, or 4,000 watch hours in 12 months | Ad revenue, Shorts revenue share |
| Full YPP (from Feb 1, 2027, new applicants) | 1,000 subs + **20M** Shorts views in 90 days, or 8,000 watch hours in 12 months | Same |

Only *engaged* views count (loops don't), and Shorts views and watch hours can't be combined.

**What 10M Shorts views in 90 days means:** about 110,000 views per day. A new channel's
typical short gets a few hundred to a few thousand views; you reach 10M only with breakout
shorts (1M+ each). So monetization depends on hits, not on upload count alone.

**Estimates for this channel (daily uploads, improving quality each week):**

| Scenario | What has to happen | Time to full monetization |
|---|---|---|
| Best case | A short breaks out (5M+) in the first 6-8 weeks | ~2-3 months; apply before Feb 1, 2027 to use the 10M rule |
| Realistic, if the videos are good | Several 500k-2M shorts by month 3-4 | ~4-8 months (likely under the 20M rule) |
| Common outcome | No breakout; views stay in the thousands | Never, unless the format improves |

**Faster route most people miss: long-form.** 4,000 watch hours is about 50,000 views of an
8-10 minute video at 50% retention, which is often easier than 10M shorts views. Plan: daily
shorts for discovery, plus one 8-12 minute compilation per week ("10 What-Ifs That Would
Kill You"). From Feb 2027 that path needs 8,000 hours (~100,000 long-form views/year).

**What it pays (published ranges, rough):** Shorts earn about $50-500 per million views
(roughly $500-5,000 for 10M views). Long-form education/science earns about $4-12 per 1,000
views; finance more.

## Sources

- YPP tiers and the Feb 2027 change: [AIR Media-Tech YPP guide 2026](https://air.io/en/monetization/youtube-partner-program-requirements-2026-the-complete-guide),
  [Tubefilter, Aug 10 2026](https://www.tubefilter.com/2026/08/10/youtube-partner-program-ad-eligibility-requirements-shorts/amp/),
  [Free Press Journal](https://www.freepressjournal.in/tech/youtube-doubles-watch-hour-requirement-for-creators-to-join-monetisation-programme-all-details),
  [YouTube blog: qualified watch hours and Shorts views](https://blog.youtube/news-and-events/youtube-monetization-qualified-watch-hours-shorts-views/)
- RPM and time-to-monetize ranges (vendor blogs, rough): [gofaceless.ai](https://www.gofaceless.ai/en/blog/youtube-shorts-monetization),
  [bytecap.io](https://www.bytecap.io/blog/faceless-youtube-channel-that-makes-money-2026),
  [easyviral.ai](https://easyviral.ai/blog/how-much-do-faceless-youtube-channels-make-2026)
- Niche and channel patterns: `research/channels.md`
