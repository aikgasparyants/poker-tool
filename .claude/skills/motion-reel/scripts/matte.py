"""Professional person matting + depth for reel footage.

BiRefNet-matting (ZhengPeng7/BiRefNet-matting, MIT) gives a soft alpha with hair detail;
Depth-Anything-V2-Small (Apache-2.0) gives relative depth. Runs on Apple MPS.

usage:
  python matte.py frames IN_DIR OUT_DIR [--depth]        # every PNG/JPG in IN_DIR -> OUT_DIR/<name>_a.png (+ _d.png)
  python matte.py clip SRC.mp4 START DUR OUT_DIR [--depth] [--size 1024]
      -> OUT_DIR/rgb_%04d.jpg, alpha_%04d.png (temporally smoothed), depth_%04d.png
"""
import argparse, glob, os, subprocess, sys
import numpy as np
import torch
from PIL import Image

DEV = "mps" if torch.backends.mps.is_available() else "cpu"
FFMPEG = os.path.expanduser("~/.local/bin/ffmpeg")
_birefnet = None
_depth = None


def birefnet():
    global _birefnet
    if _birefnet is None:
        from transformers import AutoModelForImageSegmentation

        m = AutoModelForImageSegmentation.from_pretrained("ZhengPeng7/BiRefNet-matting", trust_remote_code=True)
        _birefnet = m.to(DEV).eval().float()
    return _birefnet


def depth_model():
    global _depth
    if _depth is None:
        from transformers import pipeline

        _depth = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf", device=DEV)
    return _depth


MEAN = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
STD = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)


@torch.no_grad()
def alpha_of(img: Image.Image, size=1024) -> np.ndarray:
    """float32 HxW in 0..1"""
    w, h = img.size
    x = torch.from_numpy(np.asarray(img.convert("RGB").resize((size, size), Image.BICUBIC))).permute(2, 0, 1).float() / 255
    x = ((x - MEAN) / STD).unsqueeze(0).to(DEV)
    pred = birefnet()(x)[-1].sigmoid()[0, 0].float().cpu().numpy()
    a = Image.fromarray((pred * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return np.asarray(a).astype(np.float32) / 255


def depth_of(img: Image.Image) -> np.ndarray:
    d = np.asarray(depth_model()(img.convert("RGB"))["depth"].resize(img.size, Image.BICUBIC)).astype(np.float32)
    return (d - d.min()) / max(1e-6, d.max() - d.min())  # 1 = near


def save_gray(a: np.ndarray, path: str):
    Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8)).save(path)


def cmd_frames(a):
    os.makedirs(a.out, exist_ok=True)
    for f in sorted(glob.glob(os.path.join(a.inp, "*.png")) + glob.glob(os.path.join(a.inp, "*.jpg"))):
        n = os.path.splitext(os.path.basename(f))[0]
        img = Image.open(f)
        save_gray(alpha_of(img, a.size), os.path.join(a.out, f"{n}_a.png"))
        if a.depth:
            save_gray(depth_of(img), os.path.join(a.out, f"{n}_d.png"))
        print(n, flush=True)


def cmd_clip(a):
    os.makedirs(a.out, exist_ok=True)
    subprocess.run(
        [FFMPEG, "-v", "error", "-y", "-ss", str(a.start), "-t", str(a.dur), "-i", a.src, "-q:v", "2",
         os.path.join(a.out, "rgb_%04d.jpg")],
        check=True,
    )
    frames = sorted(glob.glob(os.path.join(a.out, "rgb_*.jpg")))
    raw = []
    for i, f in enumerate(frames):
        img = Image.open(f)
        raw.append(alpha_of(img, a.size))
        if a.depth and i % a.depth_every == 0:
            d = depth_of(img)
            for j in range(i, min(i + a.depth_every, len(frames))):
                save_gray(d, os.path.join(a.out, f"depth_{j + 1:04d}.png"))
        print(f"{i + 1}/{len(frames)}", end="\r", flush=True)
    # temporal smoothing: 3-tap weighted average kills edge shimmer without ghosting
    for i in range(len(raw)):
        prev = raw[max(0, i - 1)]
        nxt = raw[min(len(raw) - 1, i + 1)]
        sm = 0.25 * prev + 0.5 * raw[i] + 0.25 * nxt
        save_gray(sm, os.path.join(a.out, f"alpha_{i + 1:04d}.png"))
    print(f"\n{len(frames)} frames -> {a.out}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("frames")
    f.add_argument("inp"); f.add_argument("out"); f.add_argument("--depth", action="store_true"); f.add_argument("--size", type=int, default=1024)
    c = sub.add_parser("clip")
    c.add_argument("src"); c.add_argument("start", type=float); c.add_argument("dur", type=float); c.add_argument("out")
    c.add_argument("--depth", action="store_true"); c.add_argument("--depth-every", type=int, default=1); c.add_argument("--size", type=int, default=1024)
    a = p.parse_args()
    {"frames": cmd_frames, "clip": cmd_clip}[a.cmd](a)
