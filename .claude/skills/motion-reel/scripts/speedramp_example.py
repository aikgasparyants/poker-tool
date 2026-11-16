"""Speed-ramp the drone flight 0:26 → 0:37 into a 9:16 frame sequence with motion blur.

Output time 0 → T_STOP: source 26.0 → 37.0.
  phase A (0 → T_REVEAL): over the seats, v = 1.2 + K·sin²(πt/T_REVEAL)   (peak ≈ 4.7×)
  phase B (T_REVEAL → T_STOP): the stage, v falls linearly 1.2 → V_END, then the hard stop.
T_REVEAL / T_STOP sit on the music: downbeat 47.77 and hit 52.41 of the old reel track,
music starting at its drop 45.45 → 2.32 s and 6.96 s.
Motion blur = average of the source frames inside a 180° shutter.
"""
import os, subprocess, sys
import numpy as np
from PIL import Image

V = "/Users/ed/Downloads/dji_fly_20261024_190356_0007_1792854944081_video_beautify.MOV"
HERE = os.path.dirname(os.path.abspath(__file__))
# 16:9 like the source (Ed: keep it horizontal)
SRC_DIR = os.path.join(HERE, "src_frames_h")
INTERP_DIR = os.path.join(HERE, "interp_hs")  # vidstab-stabilized, then 120 fps
OUT_DIR = os.path.join(HERE, "../reel/remotion/public/drone_h")
FFMPEG = os.path.expanduser("~/.local/bin/ffmpeg")
FPS = 30.0
S0, S1 = 26.0, 37.0
T_REVEAL, T_STOP = 4.17, 10.72  # stage on the hit 49.62, stop on the last big hit 56.17 (music from 45.45)
S_REVEAL = 32.9  # stage comes into view

# Ed: «ускорение пусть будет плавным — очень плавным». One C1-smooth speed curve (PCHIP through
# speed keys with flat tangents), peak solved so the stage appears exactly at T_REVEAL and the
# stop lands on src 37.0 at T_STOP.
from scipy.interpolate import PchipInterpolator

_DT = 1 / 3000.0
_T = np.arange(0, T_STOP + _DT, _DT)


def _curve(vp, v_end):
    keys_t = [0.0, 0.35, 1.9, 3.6, T_REVEAL, 7.6, T_STOP]
    keys_v = [1.0, 1.05, vp, 1.0, 0.8, 0.66, v_end]
    return PchipInterpolator(keys_t, keys_v)(_T)


def _solve():
    v_end = 0.45
    for _ in range(40):  # fit both integrals
        lo, hi = 1.0, 8.0
        for _ in range(60):
            vp = (lo + hi) / 2
            v = _curve(vp, v_end)
            a = np.sum(v[_T <= T_REVEAL]) * _DT
            lo, hi = (vp, hi) if a < S_REVEAL - S0 else (lo, vp)
        v = _curve(vp, v_end)
        b = np.sum(v[_T > T_REVEAL]) * _DT
        v_end += (S1 - S_REVEAL - b) / (T_STOP - 7.6) * 1.5
    v = _curve(vp, v_end)
    return vp, v_end, v, S0 + np.cumsum(v) * _DT


VP, V_END, _V, _S = _solve()


def speed_curve():
    return VP, V_END


def src_time(t, K=None, v_end=None):
    return float(np.interp(min(t, T_STOP), _T, _S))


def speed(t, K=None, v_end=None):
    return float(np.interp(min(t, T_STOP), _T, _V))


def main():
    os.makedirs(SRC_DIR, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    if not os.path.exists(os.path.join(SRC_DIR, "f_0001.jpg")):
        # native frames, 9:16 centre crop of the 4K picture
        subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", str(S0 - 0.2), "-t", str(S1 - S0 + 0.6), "-i", V,
                        "-vf", "scale=1920:1080:flags=lanczos", "-q:v", "1",
                        os.path.join(SRC_DIR, "f_%04d.jpg")], check=True)
    files = sorted(f for f in os.listdir(SRC_DIR) if f.endswith(".jpg"))
    os.makedirs(INTERP_DIR, exist_ok=True)
    if not os.path.exists(os.path.join(INTERP_DIR, "i_00001.jpg")):
        subprocess.run([FFMPEG, "-v", "error", "-y", "-framerate", "29.97", "-i", os.path.join(SRC_DIR, "f_%04d.jpg"),
                        "-vf", "minterpolate=fps=119.88:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1", "-q:v", "2",
                        os.path.join(INTERP_DIR, "i_%05d.jpg")], check=True)
    src_fps = 29.97
    t0 = S0 - 0.2
    cache = {}

    def frame(i):
        i = int(np.clip(i, 0, len(files) - 1))
        if i not in cache:
            cache[i] = np.asarray(Image.open(os.path.join(SRC_DIR, files[i])), dtype=np.float32)
            if len(cache) > 40:
                cache.pop(next(iter(cache)))
        return cache[i]

    ifiles = sorted(f for f in os.listdir(INTERP_DIR) if f.endswith(".jpg"))
    icache = {}

    def iframe(j):
        j = int(np.clip(j, 0, len(ifiles) - 1))
        if j not in icache:
            icache[j] = np.asarray(Image.open(os.path.join(INTERP_DIR, ifiles[j])), dtype=np.float32)
            if len(icache) > 20:
                icache.pop(next(iter(icache)))
        return icache[j]

    K, v_end = speed_curve()
    n_out = int(round(T_STOP * FPS)) + 1
    print(f"peak {VP:.2f}x, end {V_END:.2f}x, src at reveal {src_time(T_REVEAL):.2f}, at stop {src_time(T_STOP):.2f}, frames={n_out}")
    for k in range(n_out):
        t = k / FPS
        s = src_time(t, K, v_end)
        v = speed(t, K, v_end)
        ic = (s - t0) * src_fps * 4  # position on the 120 fps stabilized timeline
        span = v * 0.5 * 4  # 180° shutter in 120 fps frames
        if span <= 1.0:
            lo = int(np.floor(ic)); w = ic - lo
            img = iframe(lo) * (1 - w) + iframe(lo + 1) * w
        else:
            taps = np.linspace(ic - span / 2, ic + span / 2, int(np.ceil(span)) + 2)
            img = np.mean([iframe(int(round(x))) for x in taps], axis=0)
        Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(os.path.join(OUT_DIR, f"r_{k + 1:04d}.jpg"), quality=93)
    # the stop frame, sharp
    Image.fromarray(iframe(int(round((S1 - t0) * src_fps * 4))).astype(np.uint8)).save(os.path.join(OUT_DIR, "stop.jpg"), quality=95)
    print("done", n_out)


if __name__ == "__main__":
    main()
