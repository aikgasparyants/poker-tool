---
name: motion-reel
description: Make a theatre reel, teaser, trailer or motion-graphics video in Remotion with a director's workflow. That means real production footage and posters, a style taken from a reference, cuts on the score's beat grid, and a contact-sheet critique loop before every render. Use when asked for a reel, Instagram/TikTok video, teaser, trailer, showreel, animated poster or motion ad for a show, festival or theatre, or when a video "looks generic / AI-made / like a slideshow".
argument-hint: "[show or brief] [duration] [format]"
---

# Motion reel

The prompt is 10% of a good reel. The other 90% is the harness: real assets, a measured beat grid, a written shot list, and looking at your own frames before showing anything. This skill is that harness, built for Remotion and for Armenian theatre campaigns. The copy is Armenian-first and briefs usually come in Russian.

Load `remotion-best-practices` alongside this skill for Remotion API details. This skill decides *what* to make and *how to check it*; that one says *how to write the code*.

## 0. Collect the inputs first

Ask only for what is missing. Infer the rest from the project folder and memory.

- **Show and goal:** the title, what the reel must make someone do (buy tickets, come to a premiere, remember a quote), and the deadline.
- **Duration and formats:** 9:16 at 1080x1920 by default. Also 1:1 / 4:5 / 16:9 if asked, built from the same timeline, never cropped.
- **Real assets.** Inventory them: stage footage, rehearsal video, production photos (often a public Google Drive folder), the poster and its layers, logos, the end-card marks. Note burned-in text, dates and watermarks in the sources and their exact pixel rows.
- **Music:** the show's original score, a supplied track, or "synthesize". Prefer the show's own score.
- **Copy:** the quotes and lines, in Armenian unless told otherwise. Never invent credits, dates or prices.
- **Reference (optional):** a video, a single frame or a folder whose *grammar* to borrow.

Do not plan around footage that does not exist. Never redraw a real poster, logo or stage moment from imagination; crop and animate the real thing.

## 1. Workflow with gates

Work through the gates in order. Show the user the artefact at each **⏸** and wait for an OK. If the user says "don't wait", continue on your own after showing it.

1. **Inventory.** List the assets with durations and resolutions, plus the usable moments in the footage (timecodes). Pick visually spectacular moments, not static ones.
2. **Reference → style guide** (if a reference exists). See `references/briefs.md` § Reference. Write `docs/style_guide.md`.
3. **Beat grid.** Run `scripts/beats.py` on the chosen music segment to get `beats.json`, with times *and* frames at the comp's fps. Choose the segment so that the score's big hit lands on the finale.
4. **Shot list on the beat grid ⏸.** Use `docs/shotlist.md` or `shots_vN.json`. For each shot give: beats from–to, source clip and in-point, framing, on-screen text, transition, and SFX/accent. The hook must land in the first 2 s and carry text. Something new happens every 2–4 s.
5. **Stills.** Render one still per shot (`npx remotion still`) or a quick contact sheet from a low-res render. Run the critique loop on the stills.
6. **Animation.** Write the composition, following `references/house-rules.md`.
7. **Critique loop.** See § 2. At least 2 rounds; every score must reach 8+.
8. **Final render ⏸.** Render the MP4, then a numbered storyboard and a REVIEW copy. In the Little Prince project these come from `tools/storyboard.py`; reuse that pattern. Version the files (`-v2`, `-v3`…, never overwrite an approved FINAL).
9. **Deliver.** Hand over the MP4, storyboard.jpg, REVIEW.mp4 and cover frames (hook + finale). Say in one line what you would improve next.

One session per production: the renderer, fonts and helpers you build stay warm for the next cut.

## 2. Critique loop — look at your own frames

Opus reads images. Use that every round:

```bash
python3 <skill>/scripts/qa.py contact out.mp4 qa/contact.jpg      # 2 fps grid of the whole reel
python3 <skill>/scripts/qa.py phone   out.mp4 qa/phone.jpg        # 1 fps at 360 px wide = phone legibility
python3 <skill>/scripts/qa.py cuts    out.mp4 qa/cuts.jpg --frames 45,90,135   # ±2 frames around every cut
python3 <skill>/scripts/qa.py strip   out.mp4 qa/strip.jpg --at 4.2           # 12 frames around a fast move
python3 <skill>/scripts/qa.py safe    out.mp4 qa/safe.jpg         # Instagram UI overlay on sample frames
python3 <skill>/scripts/qa.py loudness out.mp4                    # integrated LUFS / true peak
```

Open each image and judge it like a harsh motion director, not a proud author. Score each item 1–10:

| Criterion | What 8+ means |
|---|---|
| Hook | First 2 s: the most striking moment + text, no slow fade-in |
| Legibility | Every line readable at 360 px wide, inside the safe zones |
| Motion | Springs and eased moves, no linear slides, no dead frames |
| Variety | A new device every 2–4 s; no device used more than ~2 times |
| Brand | The show's own palette, logotype and fonts; reads as *this* show |
| Sound sync | Cuts on beats, big moments on downbeats/accents, loudness ≈ −14 LUFS |
| Craft | No stray frames at cuts, no burned-in source text visible, no overlap during text swaps |

Write the scores and the **3 worst problems with timestamps** to `docs/review_log.md`. Fix those three, re-render only what changed, look again. Stop once all scores are 8+ and two rounds are done. Don't polish forever.

## 3. Hard rules

- **Real material only.** Use real footage, real poster layers and real logotypes. No invented UI, people, credits or dates.
- **Deterministic.** Everything is a function of `useCurrentFrame()`. Use `random(seed)`, never `Math.random()`. No CSS transitions or animations, no timers, no state carried between frames.
- **Banned looks.** No centred title on a plain gradient, no "everything fades in", no captions in corners or frame borders, no glow on text, no generic particle bursts, no Ken-Burns slideshow of stills.
- **Typography.** One display face plus one text face. Armenian copy uses fonts from `~/Library/Fonts` copied into `public/fonts/` and loaded with `@remotion/fonts`. Check every Armenian glyph renders (no tofu).
- **Safe zones** at 1080x1920: keep text out of the top 220 px and bottom 320 px, and out of x > 940 for y 1050–1750. Keep lines ≤ 820 px wide.
- **Sound.** Use the music unchanged except for trims, fades and level. Bring it to −14 LUFS integrated with true peak ≤ −1 dBTP.


## Cut-outs, mattes and depth — professional grade only

Ed rejected a reel (Hamlet v8, 2026-10-19) because the imgly cut-outs were mushy: haze, lost faces, missing people. Never use `@imgly/background-removal` for a deliverable again.

- Environment: `~/.local/venvs/vfx` (Python 3.11 via `~/.local/bin/uv`, torch with Apple MPS, transformers, timm).
- `scripts/matte.py frames IN OUT [--depth]` → `<name>_a.png` alpha from **BiRefNet-matting** (hair-level edges) and `<name>_d.png` depth from **Depth-Anything-V2-Small** (1 = near).
- `scripts/matte.py clip SRC START DUR OUT --depth` → per-frame `rgb_/alpha_/depth_%04d` for footage, alpha temporally smoothed (0.25/0.5/0.25) so edges don't shimmer.
- Prefer keeping the original plate behind the person and inserting graphics BETWEEN plate and matte (text-behind-actor, light, fog by depth): matte errors stay invisible. Only isolate a person on a flat field when the alpha is clean at full size; check a 100 % crop of hair and hands before using it.
- Out-of-focus people are treated as background by the model — don't promise a cut-out of a blurred second figure.


## Speed ramps, slow motion and drone footage — smooth or nothing

Ed (Hamlet drone teaser, 2026-10-24): «ускорение пусть будет плавным — очень плавным», «все повороты с дергами». What fixes it:

1. **Keep the source aspect.** A 16:9 drone shot stays 16:9 unless Ed asks for vertical.
2. **Stabilize first** (ffmpeg has libvidstab): `vidstabdetect=shakiness=6:accuracy=15:stepsize=6` → `vidstabtransform=smoothing=18:optzoom=0:zoom=5:interpol=bicubic`, light `unsharp`. Measure jitter before/after with OpenCV LK flow (deviation from a 0.5 s moving average of the camera path).
3. **Interpolate the whole range to 120 fps** before ramping (`minterpolate=fps=119.88:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:scd=none` on the stabilized frames). RIFE is better but its downloaded binary is blocked by the permission classifier — ask Ed before using it.
4. **One C1-smooth speed curve** (PCHIP through speed keys, no piecewise kinks; solve the peak so story beats land on music hits). Keep peaks modest (≈2.5×); a 5× spike reads as a jerk.
5. **Render fast moves at 60 fps** (Remotion comp fps 60, ramp frames at 60): at 30 fps a 40 px/frame pan strobes whatever you do. Measured shake on dark FPV footage is mostly estimator noise — vidstab/own stabilization did not reduce it; don't chase it, fix sampling and frame rate.
6. **Dense motion blur:** 180° shutter = average of ⌈v·0.5·4⌉+2 frames from the 120 fps timeline; never blend just 2–3 native frames.
Reference implementation: `scripts/speedramp_example.py` (Hamlet drone).

## Files in this skill

- `references/house-rules.md`: render contract, look, motion and sound rules in Remotion terms. A copy can be dropped into a project's CLAUDE.md.
- `references/briefs.md`: templates for the reference→style guide prompt, the beat-grid shot list, the director's brief for long pieces, and the critique prompt.
- `references/motion.md`: springs that feel expensive in Remotion (multi-target sums, staggered text, swaps, loops).
- `scripts/beats.py`: music → `beats.json` (BPM, beats, downbeats, accent hits, all in seconds and frames). Needs librosa.
- `scripts/matte.py`: BiRefNet-matting alpha + Depth-Anything-V2 depth for stills or whole clips (run with `~/.local/venvs/vfx/bin/python`).
- `scripts/qa.py`: contact sheet, phone test, cut check, strip, safe-zone overlay, loudness and loop check. Uses Remotion's bundled ffmpeg.

On this Mac:
- Node lives in `~/.local/node/bin`, so prefix commands with `export PATH=~/.local/node/bin:$PATH;`.
- A full ffmpeg 7.1 is at `~/.local/bin/ffmpeg` (from the imageio-ffmpeg wheel). `qa.py` uses it, and so does `tools/storyboard.py` (pass it as the FFMPEG argument). Remotion's own bundled ffmpeg is stripped: it lacks tile, select, drawtext and ebur128, so it cannot make the sheets.
- librosa 0.11 is installed for the system `python3` (3.8) with `--user`.

Tested on `little-prince-reel/malenkiy-prints-FINAL.mp4` (2026-10-17). `beats.py` fitted the Fox Theme segment to 160.07 BPM = 11.245 frames per beat, matching the hand-measured 11.25. `qa.py loudness` read −14.0 LUFS.
