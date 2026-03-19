#!/usr/bin/env python3
"""
Convert all mp4 files under `static/images/videos/` into gifs under a new folder,
while keeping the directory structure and base filenames consistent.

Notes:
- This script does NOT touch existing mp4 files.
- "Cropped" behavior is approximated by applying a zoom-in (scale then crop back)
  only for `compare/` videos, matching the previous CSS white-bar removal approach.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def main() -> None:
    here = Path(__file__).resolve().parent
    input_root = here / "static" / "images" / "videos"
    output_root = here / "static" / "images" / "videos_gif"

    if not input_root.exists():
        raise FileNotFoundError(f"Input folder not found: {input_root}")

    mp4_paths = sorted(input_root.rglob("*.mp4"))
    if not mp4_paths:
        print(f"No .mp4 files found under {input_root}")
        return

    zoom = 1.15
    fps = 12

    for mp4 in mp4_paths:
        rel = mp4.relative_to(input_root)
        out = (output_root / rel).with_suffix(".gif")
        out.parent.mkdir(parents=True, exist_ok=True)

        if out.exists() and out.stat().st_size > 0:
            print(f"[skip] {rel} -> {out.relative_to(here)} (exists)")
            continue

        if rel.parts[0] == "compare":
            # Zoom in and crop back to remove padding/white bars (approximation).
            vf = f"fps={fps},scale=iw*{zoom}:ih*{zoom}:flags=lanczos,crop=iw:ih"
        else:
            vf = f"fps={fps}"

        filter_complex = (
            f"[0:v]{vf},split[a][b];"
            f"[a]palettegen[p];"
            f"[b][p]paletteuse=dither=bayer:bayer_scale=5:diff_mode=1"
        )

        print(f"[conv] {rel} -> {out.relative_to(here)}")
        cmd = [
            "ffmpeg",
            "-y",
            "-nostdin",
            "-loglevel",
            "error",
            "-i",
            str(mp4),
            "-filter_complex",
            filter_complex,
            str(out),
        ]
        run(cmd)

    print(f"Done. Output gifs in: {output_root}")


if __name__ == "__main__":
    main()

