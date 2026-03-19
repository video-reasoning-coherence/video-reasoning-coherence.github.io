#!/usr/bin/env python3
"""
Generate first-frame thumbnails for visualization gifs.

It extracts the first frame of every:
  static/images/videos_gif/visualization/**/*.gif
and saves it as:
  static/images/videos_gif/visualization_thumbs/***.png

The website's index.html expects the thumbs to exist.

Usage (from this directory):
  python3 generate_visualization_gif_first_frames.py
"""

from pathlib import Path

from PIL import Image


def main() -> None:
    repo_dir = Path(__file__).resolve().parent
    in_root = repo_dir / "static/images/videos_gif/visualization"
    out_root = repo_dir / "static/images/videos_gif/visualization_thumbs"

    if not in_root.exists():
        raise FileNotFoundError(f"Input not found: {in_root}")

    out_root.mkdir(parents=True, exist_ok=True)

    gif_paths = sorted(in_root.rglob("*.gif"))
    if not gif_paths:
        print(f"No gifs found under: {in_root}")
        return

    ok = 0
    fail = 0
    for gif_path in gif_paths:
        rel = gif_path.relative_to(in_root)
        out_path = (out_root / rel).with_suffix(".png")
        out_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            im = Image.open(gif_path)
            im.seek(0)  # first frame
            im = im.convert("RGBA")
            im.save(out_path, "PNG", optimize=True)
            ok += 1
        except Exception as e:
            fail += 1
            print(f"[FAIL] {gif_path} -> {out_path}: {e}")

    print(f"Done. success={ok}, fail={fail}, total={len(gif_paths)}")


if __name__ == "__main__":
    main()

