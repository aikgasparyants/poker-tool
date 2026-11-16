# Brief templates

Fill in the brackets. Each template asks for a written artefact *before* any code. Building from a shot list is fast; repairing a vibe is slow.

## Reference → style guide

Use this when the user shows a video, frame or folder they like.

```
Reference: [./refs/ref.mp4 | ./refs/frame.png | ./refs/folder/]

1. Pull a frame every 0.5 s (qa.py contact --fps 2 does this) and study them.
2. Write docs/style_guide.md:
   palette (hex), type (family, weight, case, tracking), shot lengths,
   transition types, camera moves, texture/grain, how text enters and leaves,
   how footage and graphics share the frame.
3. Write docs/shotlist.md for a [DURATION]s reel about [SHOW] in that style,
   using our real footage and poster.
Borrow the grammar of the reference, never its content, logos or characters.
Show me both files and wait for OK before writing code.
```

Naming a style ("Swiss poster", "A24 trailer", "Soviet constructivist titles") works better than describing one. A frame plus a name is best.

## Shot list on the beat grid

```
Music: [file], segment [start]–[end] s → beats.json (BPM [x], beat = [n] frames @ [fps]).
Hook (beats 0–[k]): [the single most striking moment] + [text].

| # | beats | source clip @ in-point | framing / move | text on screen | transition in | accent |
|---|-------|------------------------|----------------|----------------|---------------|--------|
| 1 | 0–4   | ...                    | ...            | ...            | hard cut      | downbeat |
...
End card (beats [a]–end): logotype + ticket pill + marks only.

Rules: a new device every 2–4 s; no device > 2 times; text almost always on screen;
the big hit of the music lands on the finale.
```

For JSON-driven projects, mirror this in `shots_vN.json` (`{"beat": n, "end": f, "shots": [{name, from, to, text}]}`) so the storyboard tool can number the shots.

## Director's brief (long or ambitious pieces: trailers, 60 s+, festival films)

```
You are the director, editor, motion designer and sound mixer for a [DURATION] [FORMAT] film
about [SHOW]. Treat it as a multi-session production. Don't rush to a final render.

## The film in one line
[What it is + what the viewer should feel at the end.]

## Inputs
- Footage: [paths + what's in each, usable timecodes]
- Poster / layers / logos: [paths]
- Music: [path], use unchanged except trims/fades. Measure with beats.py first.
- Copy: [lines, Armenian], exact spelling as given.
- Skills: motion-reel, remotion-best-practices.

## Look
[3–5 lines: palette, type, texture, camera language, banned looks.]

## Beat sheet
0:00–0:02 hook: [image + text]
...       a new payoff every 3–5 s
[end]     logotype + tickets

## Gates (show me each one)
1. style_guide.md + shotlist.md
2. stills for every shot → contact sheet → critique
3. low-res animatic (540x960) with the real music → fix pacing
4. full animation → polish → sound → final render + storyboard + REVIEW

## Critique (every round)
Score 1–10: hook, legibility at 360 px, motion, variety, brand, sound sync, craft.
Log scores + the 3 worst problems with timestamps in docs/review_log.md. Fix. Repeat until all 8+.

## Deliverables
out/[name]-vN.mp4 · storyboard-vN.jpg · [name]-vN-REVIEW.mp4 · cover-hook.jpg · cover-finale.jpg
```

## Critique prompt (paste after any render)

```
Open qa/contact.jpg, qa/phone.jpg and qa/cuts.jpg and really look at them.
Be a harsh motion director, not a proud author.

Score 1–10: hook in the first 2 s · legibility at phone size · motion quality · variety
(new thing every 2–4 s) · brand accuracy · sound sync · craft.

List the 3 biggest problems with timestamps. Hunt for: text overlapping during swaps,
linear slides, text in unsafe zones, centred-on-gradient shots, a dead beat with nothing
happening, stray frames at cuts, burned-in source text showing, a repeated device.

Fix them, re-render, show the new sheets and new scores.
```

## One-liner (for testing a setup only)

```
make a dynamic 15-second vertical motion-graphics reel for [SHOW] from ./assets,
like a top motion designer's showreel. Real footage only, cuts on the beat of ./music.wav,
Armenian text from ./copy.md. Go all out.
```

A one-liner tests the engine, not the idea. Use the shot list for real work.
