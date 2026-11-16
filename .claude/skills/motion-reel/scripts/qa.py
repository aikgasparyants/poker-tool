#!/usr/bin/env python3
"""QA sheets for a rendered reel, to look at before showing anything.

usage:
  qa.py contact  VIDEO OUT.jpg [--fps 2] [--cols 6] [--width 270]   grid of the whole video
  qa.py phone    VIDEO OUT.jpg [--fps 1]                            1 fps at 360 px wide (phone legibility)
  qa.py cuts     VIDEO OUT.jpg --frames 45,90,135                   rows of frames cut-2 .. cut+2
  qa.py strip    VIDEO OUT.jpg --at 4.2 [--n 12]                    n consecutive frames around a moment
  qa.py safe     VIDEO OUT.jpg [--fps 0.5]                          Instagram 9:16 UI zones drawn over frames
  qa.py loudness VIDEO                                              integrated LUFS, true peak, LRA
  qa.py loop     VIDEO OUT.mp4                                      the video twice back to back (check the seam)

ffmpeg: $FFMPEG, else ~/.local/bin/ffmpeg, else `ffmpeg` on PATH. Remotion's bundled ffmpeg is
stripped (no tile/select/drawtext/ebur128) and is not used.
"""
import argparse
import math
import os
import re
import shutil
import subprocess
import sys


def find_ffmpeg():
    # Remotion's bundled ffmpeg (node_modules/@remotion/compositor-*) is stripped: no tile, select,
    # drawtext or ebur128. So it is not usable here.
    for cand in (os.environ.get("FFMPEG"), os.path.expanduser("~/.local/bin/ffmpeg"), shutil.which("ffmpeg")):
        if cand and os.path.exists(cand):
            return cand
    sys.exit(
        "full ffmpeg not found. Set FFMPEG=/path, or install it to ~/.local/bin/ffmpeg from the imageio-ffmpeg wheel:\n"
        "  pip download imageio-ffmpeg --no-deps --only-binary=:all: --platform macosx_11_0_arm64 --python-version 3.9 -d /tmp/w\n"
        "  unzip the .whl, then copy imageio_ffmpeg/binaries/ffmpeg-* to ~/.local/bin/ffmpeg and chmod +x it"
    )


FFMPEG = None


def ff(*args, capture=False):
    cmd = [FFMPEG, "-hide_banner", "-loglevel", "error" if not capture else "info", "-y", *args]
    r = subprocess.run(cmd, capture_output=capture, text=True)
    if r.returncode != 0:
        sys.exit(f"ffmpeg failed: {' '.join(cmd)}\n{r.stderr if capture else ''}")
    return r


def probe(video):
    """(duration s, width, height, fps) parsed from `ffmpeg -i` (no ffprobe needed)."""
    if not os.path.exists(video):
        sys.exit(f"no such video: {video}")
    r = subprocess.run([FFMPEG, "-hide_banner", "-i", video], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr)
    s = re.search(r"Video:.*?, (\d{2,5})x(\d{2,5})", r.stderr)
    f = re.search(r"([\d.]+) fps", r.stderr)
    if not (m and s):
        sys.exit(f"could not read {video}:\n{r.stderr[-800:]}")
    dur = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    return dur, int(s.group(1)), int(s.group(2)), float(f.group(1)) if f else 30.0


def label(text, size=22):
    # drawtext needs a font; use Arial Unicode if present so Armenian/Cyrillic labels work
    font = "/Library/Fonts/Arial Unicode.ttf"
    fontopt = f":fontfile='{font}'" if os.path.exists(font) else ""
    return (f"drawtext=text='{text}'{fontopt}:fontsize={size}:fontcolor=white:box=1:"
            f"boxcolor=black@0.6:boxborderw=4:x=6:y=6")


def contact(a, width=None, fps=None):
    dur, w, h, _ = probe(a.video)
    fps = fps or a.fps
    width = width or a.width
    n = max(1, int(math.ceil(dur * fps)))
    rows = int(math.ceil(n / a.cols))
    ts = "%{pts\\:hms}"
    vf = f"fps={fps},scale={width}:-2,{label(ts, max(14, width // 14))},tile={a.cols}x{rows}:padding=4:color=0x222222"
    ff("-i", a.video, "-vf", vf, "-frames:v", "1", "-q:v", "3", a.out)
    print(f"{a.out}: {n} frames, {a.cols}x{rows}, {dur:.2f}s")


def cuts(a):
    _, _, _, fps = probe(a.video)
    frames = [int(x) for x in a.frames.split(",") if x.strip()]
    sel = "+".join(f"between(n\\,{max(0, c - 2)}\\,{c + 2})" for c in frames)
    num = "%{eif\\:t*" + f"{fps:g}" + "\\:d}"  # original frame number from the timestamp
    vf = (f"select='{sel}',scale={a.width}:-2,{label(num, 18)},"
          f"tile=5x{len(frames)}:padding=4:color=0x222222")
    ff("-i", a.video, "-vf", vf, "-fps_mode", "vfr", "-frames:v", "1", "-q:v", "3", a.out)
    print(f"{a.out}: rows = cuts {frames}, columns = cut-2 .. cut+2 (source frame numbers burned in)")


def strip(a):
    _, _, _, fps = probe(a.video)
    start = max(0.0, a.at - (a.n / 2) / fps)
    vf = f"scale={a.width}:-2,{label('%{pts}', 16)},tile={a.n}x1:padding=4:color=0x222222"
    ff("-ss", f"{start:.3f}", "-i", a.video, "-vf", vf, "-frames:v", "1", "-q:v", "3", a.out)
    print(f"{a.out}: {a.n} frames from {start:.2f}s")


def safe(a):
    dur, w, h, _ = probe(a.video)
    sx, sy = w / 1080.0, h / 1920.0
    boxes = [  # x, y, w, h in 1080x1920 space: Instagram reel UI
        (0, 0, 1080, 220), (0, 1600, 1080, 320), (940, 1050, 140, 700),
    ]
    draw = ",".join(
        f"drawbox=x={int(x*sx)}:y={int(y*sy)}:w={int(bw*sx)}:h={int(bh*sy)}:color=red@0.22:t=fill"
        for x, y, bw, bh in boxes
    )
    guide = f"drawbox=x={int(130*sx)}:y={int(220*sy)}:w={int(820*sx)}:h={int(1380*sy)}:color=yellow@0.8:t=3"
    n = max(1, int(math.ceil(dur * a.fps)))
    rows = int(math.ceil(n / a.cols))
    vf = f"fps={a.fps},{draw},{guide},scale={a.width}:-2,tile={a.cols}x{rows}:padding=4:color=0x222222"
    ff("-i", a.video, "-vf", vf, "-frames:v", "1", "-q:v", "3", a.out)
    print(f"{a.out}: red = Instagram UI, yellow = 820 px text column")


def loudness(a):
    r = ff("-nostats", "-i", a.video, "-af", "ebur128=peak=true", "-f", "null", "-", capture=True)
    tail = r.stderr[r.stderr.rfind("Summary:"):]
    i = re.search(r"I:\s+(-?[\d.]+) LUFS", tail)
    lra = re.search(r"LRA:\s+(-?[\d.]+) LU", tail)
    tp = re.search(r"Peak:\s+(-?[\d.]+) dBFS", tail)
    I = float(i.group(1)) if i else None
    print(f"integrated {I} LUFS · true peak {tp.group(1) if tp else '?'} dBTP · LRA {lra.group(1) if lra else '?'} LU")
    if I is not None and abs(I + 14) > 1.0:
        print(f"→ off target by {I + 14:+.1f} LU; aim for -14 LUFS, peak ≤ -1 dBTP")


def loop(a):
    ff("-stream_loop", "1", "-i", a.video, "-c", "copy", a.out)
    print(f"{a.out}: played twice; watch the seam")


def main():
    global FFMPEG
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, out=True):
        p = sub.add_parser(name)
        p.add_argument("video")
        if out:
            p.add_argument("out")
        p.add_argument("--width", type=int, default=270)
        p.add_argument("--cols", type=int, default=6)
        p.add_argument("--fps", type=float, default=2.0)
        return p

    add("contact")
    add("phone")
    add("cuts").add_argument("--frames", required=True)
    s = add("strip")
    s.add_argument("--at", type=float, required=True)
    s.add_argument("--n", type=int, default=12)
    add("safe").set_defaults(fps=0.5, cols=5)
    add("loudness", out=False)
    add("loop")
    a = ap.parse_args()
    FFMPEG = find_ffmpeg()

    os.makedirs(os.path.dirname(os.path.abspath(getattr(a, "out", ".") or ".")), exist_ok=True)
    if a.cmd == "contact":
        contact(a)
    elif a.cmd == "phone":
        a.cols = 5 if a.cols == 6 else a.cols
        contact(a, width=360, fps=1.0 if a.fps == 2.0 else a.fps)
    elif a.cmd == "cuts":
        cuts(a)
    elif a.cmd == "strip":
        strip(a)
    elif a.cmd == "safe":
        safe(a)
    elif a.cmd == "loudness":
        loudness(a)
    elif a.cmd == "loop":
        loop(a)


if __name__ == "__main__":
    main()
