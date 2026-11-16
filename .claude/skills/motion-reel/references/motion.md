# Motion that feels expensive (Remotion)

Cheap motion travels from A to B on a fixed curve. Expensive motion has mass: it accelerates, maybe overshoots a hair, and settles. In Remotion that means `spring()`, which is already a pure function of the frame.

## Spring presets

```ts
import { spring, useCurrentFrame, useVideoConfig } from "remotion";

export const SPRING = {
  snappy:  { stiffness: 320, damping: 30, mass: 1 },   // small pieces, pills, cursor-like moves
  default: { stiffness: 170, damping: 26, mass: 1 },   // cards, footage panels, camera
  heavy:   { stiffness: 120, damping: 30, mass: 1.4 }, // big type, logotype, end card (no overshoot)
  playful: { stiffness: 220, damping: 14, mass: 1 },   // stickers, mascots (visible overshoot)
};

const p = (frame: number, fps: number, at: number, cfg = SPRING.default) =>
  spring({ frame: frame - at, fps, config: cfg });
```

## A value with several targets: add springs, don't restart

When something moves A → B → C (a panel's width, the camera's x), sum one spring per change. Each starts at its own frame. The motion stays continuous, and every frame can still be rendered on its own.

```ts
// keys: [[frame, value], ...] sorted by frame
export function track(frame: number, fps: number, keys: [number, number][], cfg = SPRING.default) {
  let v = keys[0][1];
  for (let i = 1; i < keys.length; i++) {
    v += (keys[i][1] - keys[i - 1][1]) * spring({ frame: frame - keys[i][0], fps, config: cfg });
  }
  return v;
}
```

A stretchy indicator or underline puts its leading edge on `snappy` and its trailing edge on `heavy`, then draws between `min` and `max`.

## Text

- **Per-word or per-letter stagger:** 2–3 frames per unit for Armenian words, 1 frame per letter. Animate `translateY` (40 → 0 px) plus `opacity` together on a spring; never use opacity alone.
- **Swap inside a box:** the old line ends `swapOut` frames before the next one starts, so the two never overlap. A 4-frame gap is enough at 30 fps.
- **Big type:** the `heavy` spring with no overshoot. Let it hold still long enough to read: about 0.25 s per word plus 0.5 s.
- **Masks beat fades.** Reveal type through a moving clip-path or out from behind footage instead of fading it in.

## Footage moves

- Speed ramps: drive `playbackRate` per shot, or retime with `<Freeze>`/`<Sequence>`. A 1.0 → 0.4 ramp into a hit reads as cinematic.
- Push-ins of 1.0 → 1.08 over a shot, eased; never a linear zoom across the whole reel.
- Double exposure: two footage layers with `mixBlendMode: "screen"` on dark stage shots, `"multiply"` on bright ones.
- Split screens: animate the divider position with `track()`; the panels follow it.

## Cuts on the grid

```ts
const BEAT = beats.beat_frames;           // from beats.json, e.g. 15 at 120 BPM / 30 fps
const at = (b: number) => Math.round(b * BEAT);
<Sequence from={at(8)} durationInFrames={at(4)}>…</Sequence>
```

Cut on beats and land reveals on `downbeats` or `hits`. When the score accents every third beat, let the cuts follow the accents, not the bar lines.

## Loops

For a seamless loop, the last frame must equal the first: positions, scale and text state all included. Check it with `qa.py loop`.
