#!/usr/bin/env python3
"""Measure a music segment and write a beat grid for the timeline.

usage:
  python3 beats.py MUSIC.wav [--start S] [--end S] [--fps 30] [--bpm-hint 120] [--bar 4] > beats.json

Output (times relative to --start, so 0 = first frame of the reel):
  {
    "source": "...", "start": S, "end": S, "fps": 30,
    "bpm": 120.2, "beat_frames": 14.98,
    "beats":     [{"t": 0.512, "f": 15}, ...],   # cuts and state changes go here
    "downbeats": [{"t": ..., "f": ...}, ...],    # every --bar-th beat: big moments
    "hits":      [{"t": ..., "f": ..., "strength": 0.83}, ...],  # strongest onsets: accents, SFX, reveals
    "top_hits":  [...6 strongest hits...],      # candidates for the finale / big reveals
    "grid": {"bpm": 160.1, "beat_frames": 11.24, "first_beat_t": 0.33, "max_drift_ms": 40}
  }                                              # constant-tempo fit: use grid.beat_frames as BEAT

Downbeats are a guess (every --bar-th beat from the first strong beat). Check them by ear
or against the score: some scores accent every 3 beats. "Strongest" means the sharpest
onset, not necessarily the musical climax: confirm the finale hit by ear.
Needs librosa (pip install --user librosa).
"""
import argparse
import json
import sys

import librosa
import numpy as np


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audio")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=None)
    ap.add_argument("--fps", type=float, default=30.0)
    ap.add_argument("--bpm-hint", type=float, default=120.0)
    ap.add_argument("--bar", type=int, default=4, help="beats per bar for the downbeat guess")
    ap.add_argument("--hits", type=int, default=24, help="how many strongest onsets to keep")
    a = ap.parse_args()

    dur = None if a.end is None else a.end - a.start
    y, sr = librosa.load(a.audio, sr=22050, mono=True, offset=a.start, duration=dur)
    if len(y) == 0:
        sys.exit("empty segment: check --start/--end")

    hop = 512
    onset = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
    tempo, beat_frames = librosa.beat.beat_track(
        onset_envelope=onset, sr=sr, hop_length=hop, start_bpm=a.bpm_hint, units="frames"
    )
    bpm = float(np.atleast_1d(tempo)[0])
    beat_t = librosa.frames_to_time(beat_frames, sr=sr, hop_length=hop)

    # Downbeat guess: choose the phase (0..bar-1) whose beats carry the most onset energy.
    first = 0
    if len(beat_frames) >= a.bar * 2:
        energy = [onset[beat_frames[p::a.bar]].mean() for p in range(a.bar)]
        first = int(np.argmax(energy))
    down_t = beat_t[first::a.bar]

    # Accent hits: strongest onset peaks, at least ~1/3 beat apart.
    wait = max(1, int(round((60.0 / max(bpm, 1)) / 3 * sr / hop)))
    peaks = librosa.util.peak_pick(onset, pre_max=3, post_max=3, pre_avg=5, post_avg=5, delta=0.3, wait=wait)
    strength = onset[peaks] / (onset.max() or 1)
    order = np.argsort(strength)[::-1][: a.hits]
    keep = sorted(order, key=lambda i: peaks[i])
    hit_t = librosa.frames_to_time(peaks[keep], sr=sr, hop_length=hop)

    fr = lambda t: int(round(float(t) * a.fps))
    pt = lambda t: {"t": round(float(t), 3), "f": fr(t)}
    hits = [dict(pt(t), strength=round(float(s), 3)) for t, s in zip(hit_t, strength[keep])]
    top = sorted(hits, key=lambda h: -h["strength"])[:6]

    # Constant-tempo grid fitted through the tracked beats (least squares), for a fixed BEAT constant.
    grid = None
    if len(beat_t) >= 4:
        idx = np.arange(len(beat_t))
        period, offset = np.polyfit(idx, beat_t, 1)
        resid = beat_t - (offset + period * idx)
        grid = {
            "bpm": round(60.0 / period, 2),
            "beat_frames": round(a.fps * period, 3),
            "first_beat_t": round(float(offset), 3),
            "max_drift_ms": round(float(np.abs(resid).max() * 1000), 1),
        }

    out = {
        "source": a.audio,
        "start": a.start,
        "end": a.end if a.end is not None else round(a.start + len(y) / sr, 3),
        "fps": a.fps,
        "bpm": round(bpm, 2),
        "beat_frames": round(a.fps * 60.0 / bpm, 3) if bpm else None,
        "beats": [pt(t) for t in beat_t],
        "downbeats": [pt(t) for t in down_t],
        "hits": hits,
        "top_hits": top,
        "grid": grid,
    }
    json.dump(out, sys.stdout, indent=1, ensure_ascii=False)
    sys.stdout.write("\n")
    print(
        f"tracked {out['bpm']} bpm · fitted grid {grid and grid['bpm']} bpm = {grid and grid['beat_frames']} frames "
        f"@ {a.fps:g} fps, first beat {grid and grid['first_beat_t']} s, drift ≤ {grid and grid['max_drift_ms']} ms\n"
        f"{len(out['beats'])} beats · strongest hits at "
        + ", ".join(f"{h['t']}s" for h in top)
        + "  (candidates: confirm the musical climax by ear or from the score)",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
