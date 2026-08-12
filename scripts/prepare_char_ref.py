"""Prepare a character reference image for the 3-segment workflow.

Crops the non-white / transparent bounding box of a character PNG and places it
at ~20% of canvas height on a white 1920x1088 canvas. This makes MiniMax H3
render the character small (cookie-box scale) instead of giant.

Usage:
    python prepare_char_ref.py <input.png> [output.png] [height_ratio]

Examples:
    python prepare_char_ref.py my_char.png chenqianyu_mid20.png 0.20
"""

import sys

import numpy as np
from PIL import Image


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else "char_ref_mid20.png"
    ratio = float(sys.argv[3]) if len(sys.argv) > 3 else 0.20

    im = Image.open(src).convert("RGBA")
    a = np.array(im)
    alpha = a[..., 3] > 128
    nonwhite = alpha & (np.abs(a[..., :3].astype(np.int16) - 255).max(axis=2) > 30)
    ys, xs = np.where(nonwhite)
    if len(xs) == 0:
        print("no character content found in image")
        return 1

    crop = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    canvas = Image.new("RGBA", (1920, 1088), (255, 255, 255, 255))
    target_h = max(1, int(1088 * ratio))
    scale = target_h / crop.size[1]
    w = max(1, int(crop.size[0] * scale))
    small = crop.resize((w, target_h), Image.LANCZOS)
    canvas.paste(small, ((1920 - w) // 2, (1088 - target_h) // 2), small)
    canvas.convert("RGB").save(dst)
    print("saved:", dst, "| char height px:", target_h)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
