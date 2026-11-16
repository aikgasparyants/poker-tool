# House rules for code-rendered reels (Remotion)

Paste this into a reel project's `CLAUDE.md` so it applies to every cut without repeating it.

## Render contract
- A composition is a pure function of the frame number. Everything derives from `useCurrentFrame()` + `useVideoConfig()`.
- Randomness: `random("seed-string")` only. Never `Math.random()`, never `Date.now()`.
- No CSS `transition` / `animation`, no `setTimeout` / `requestAnimationFrame`, no React state that accumulates across frames.
- Footage: `<OffthreadVideo>` / `@remotion/media` `<Video>` with an explicit `trimBefore` (in frames). After every cut, check ±2 frames for stray frames from the source seek.
- Fonts: `loadFont()` from `@remotion/fonts` with files in `public/fonts/`. Wait for fonts before the first frame (`delayRender` is handled by loadFont).
- Timing constants come from `beats.json` (`BEAT` in frames, cut points as beat indices). Never hard-code seconds that drift off the grid.
- Render: `npx remotion render <Comp> out/<name>-vN.mp4` (H.264, yuv420p, `--crf 16` for masters). Comps that use WebGL need `Config.setChromiumOpenGlRenderer("angle")`.

## Look
- Banned defaults: a centred title on a flat gradient, every element fading in, captions in corners, frame borders, glow on text or UI, particle bursts, a Ken-Burns slideshow of stills.
- One display face plus one text face. One accent colour unless the brand has a defined palette (then use only the brand palette).
- The production's own identity first: the poster's palette, the logotype, the stage's light. Sample hex values from the real poster, don't guess.
- Something new must happen every 2–4 s: a cut, a reveal, a type move, a split, a double exposure, a scale change. No visual device more than ~2 times per reel.
- Footage carries the reel. Graphics frame and punctuate it; they don't cover the best moments.
- Text is on screen almost continuously. It is large, sentence case unless the brand uses caps, and sits inside the safe zones.

## Motion
- Use springs (`spring({ frame, fps, config })`) or eased `interpolate` (`Easing.bezier`, `Easing.out(Easing.cubic)`). Never use a linear move for anything the eye follows.
- A tiny overshoot is fine on small UI-like pieces; big type and logos get none.
- Stagger groups by 2–4 frames per element, not by whole seconds.
- When text swaps inside a box, the old line leaves before the new one enters (no overlap frame).
- Scale footage ≥ 1.0 enough to hide any burned-in text, dates or black bars in the source.

## Sound
- Use the show's score when it exists. Cut it on the musical phrase, and line the segment up so its biggest hit lands on the finale.
- Cuts land on beats, big reveals on downbeats or accents (`beats.json` → `downbeats`, `hits`).
- SFX, if any: whooshes on big moves, a low hit on the logotype. Keep them subtle under a real score.
- Master: −14 LUFS integrated, ≤ −1 dBTP. Short fade-in (≤ 6 frames) and a tail that rings out on the end card.

## Before you show me anything
1. Render a contact sheet (2 fps) and a phone-size sheet (360 px). Look at them.
2. Score 1–10: hook, legibility, motion, variety, brand, sound sync, craft.
3. Fix the 3 worst problems. Repeat until every score is 8+ (2 rounds minimum).
4. Only then do the full render. Ship it with a numbered storyboard and a REVIEW copy.
