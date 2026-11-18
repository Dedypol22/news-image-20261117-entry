#!/usr/bin/env python3
"""Entry for make.fun's news-image-20261117: sum up 17 November 2026's world
news in one image.

The day's defining story, carried by every major news roundup of 17 November
2026, was Ukraine's strike on the Kerch Bridge linking Russia to Crimea --
severely damaged for a second consecutive day while Russia answered against
bridges in Kyiv: a war quite literally fought over bridges. The picture in
assets/entry.png shows it at dawn: the long sea bridge with its middle spans
collapsed into the strait, black smoke rising, drones overhead and warships
standing off in the distance.

This program validates the bundled image against the competition's own caps
(real PNG, at most 1024x1024, at most 1 MiB) and writes it, byte for byte, to
<output>/entry.png. It touches no network and is fully deterministic: run it
twice and both runs produce identical bytes.
"""

import hashlib
import os
import struct
import sys

MAX_BYTES = 1_048_576  # 1 MiB
MAX_SIDE = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def png_dimensions(data: bytes) -> tuple[int, int]:
    """Read width and height from the IHDR chunk of a PNG byte string."""
    if data[:8] != PNG_MAGIC:
        raise ValueError("asset is not a PNG file")
    if data[12:16] != b"IHDR":
        raise ValueError("asset is missing its IHDR chunk")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def load_validated_image(path: str) -> bytes:
    with open(path, "rb") as fh:
        data = fh.read()
    if len(data) > MAX_BYTES:
        raise ValueError(f"asset is {len(data)} bytes, over the {MAX_BYTES} cap")
    width, height = png_dimensions(data)
    if width > MAX_SIDE or height > MAX_SIDE:
        raise ValueError(f"asset is {width}x{height}, over the {MAX_SIDE}px cap")
    return data


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    asset = os.path.join(here, "assets", "entry.png")
    data = load_validated_image(asset)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    with open(out_path, "wb") as fh:
        fh.write(data)

    digest = hashlib.sha256(data).hexdigest()

    # Read the written file back and prove it is byte-identical to the
    # validated asset, so a short or corrupted write can never slip through.
    with open(out_path, "rb") as fh:
        written = fh.read()
    if hashlib.sha256(written).hexdigest() != digest:
        raise ValueError("written file does not match the validated asset")

    width, height = png_dimensions(data)
    print(f"wrote {out_path}: {len(data)} bytes, {width}x{height}, sha256 {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
