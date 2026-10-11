# Channel style guide

The script writer reads this file on every run (`automation/daily.py`), and anyone (human or
Claude) changing the renderer in `studio/` should follow it. Update it whenever the owner gives
feedback; the newest feedback wins.

## How we work (reference-first method)

1. **The reference videos are the authority.** Put them in `references/`. Match their camera
   distance, shot length, pacing, character look, caption style and transitions. Don't invent a
   style when a reference shows one.
2. **Assets are the source of truth.** Use the supplied character, voice and font. Never swap
   in made-up replacements.
3. **Write a precise spec before building:** exact timeline, scene order, wording, and what
   must not happen.
4. **Refine, don't redesign.** Fix one thing at a time (timing, easing, spacing, framing,
   caption amount) and keep everything that already works.
5. **Check against a list before calling it done** (see the checklist below).

## Owner feedback (keep this up to date)

- Hook: every video opens with a short "What if you...?" question, e.g.
  "What if you don't sleep for 11 days?". The title uses the same question.
- Captions: keep them minimal. Small, two words at a time, lower third, never covering the
  subject. Big number callouts only 2-3 times per video, gone after ~1.5s.
- Camera: not too close. Default to wide and medium shots with space around the subject;
  close-ups are rare and still show head and shoulders.
- Characters: should look like a normal, everyday American person, not a mannequin or a
  stylized avatar.
- Reference style: Zack D. Films-type 3D "what happens if" explainers.

## Motion rules

- Every move eases in and out; no linear, robotic motion, no abrupt stops.
- Transitions stay consistent within a video; one transition language, not a new effect per cut.
- No random effects: no glitches, particle spam, aggressive zooms or heavy distortion.
- Keep one clear focal subject per shot; don't clutter the frame.

## Script rules

- Scene 1: only the "What if...?" question (max 10 words). Scene 2 answers immediately.
- One short sentence per scene (max 16 words). No intro, no filler, no "in this video".
- Facts must be accurate and verifiable. End with a twist or a question for the comments.

## Final checklist

- [ ] Opens with the "What if...?" hook; title matches it
- [ ] Shots are wide or medium; subject never cramped
- [ ] Captions small and minimal; nothing covers the subject
- [ ] Character looks like a normal person
- [ ] Motion smooth, transitions consistent, no random effects
- [ ] Facts checked; no invented names, numbers or quotes
