"""Rasterise the shipping PNGs and assemble a multi-resolution favicon.ico.

Each PNG is rendered from the tier that matches its DISPLAY size, not its file size --
a 512 px upload that Practo shows at 48 px must be built from the compact tier, or the
platform's own downscaler turns it to mush.
"""
import pathlib
import struct
from PIL import Image
import raster

BRAND = pathlib.Path(
    r"c:\Users\VijayRaghavVarada\Documents\Github\agent-website-manager"
    r"\outputs\drvarada-site\brand")
ICONS = BRAND / "icons"

# (output png, source svg, px, why)
JOBS = [
    ("favicon-16.png",         "icon-nano-navy.svg",           16),
    ("favicon-32.png",         "icon-micro-navy.svg",          32),
    ("favicon-48.png",         "icon-micro-navy.svg",          48),
    ("apple-touch-icon.png",   "icon-compact-navy-square.svg", 180),
    ("icon-192.png",           "icon-compact-navy.svg",        192),
    ("icon-512.png",           "icon-full-navy.svg",           512),
    ("profile-512.png",        "icon-compact-navy.svg",        512),
    ("profile-light-512.png",  "icon-compact-light.svg",       512),
]


def ico(pngs, out):
    """ICO container holding the PNG payloads verbatim -- so each size is its own
    purpose-built render rather than one image resampled three times."""
    blobs = [p.read_bytes() for p in pngs]
    sizes = [Image.open(p).size[0] for p in pngs]
    n = len(blobs)
    header = struct.pack("<HHH", 0, 1, n)
    offset = 6 + 16 * n
    entries, data = b"", b""
    for sz, blob in zip(sizes, blobs):
        entries += struct.pack("<BBBBHHII", sz % 256, sz % 256, 0, 0, 1, 32,
                               len(blob), offset)
        offset += len(blob)
        data += blob
    out.write_bytes(header + entries + data)


def main():
    for name, svg, px in JOBS:
        raster.render_png(svg, px, name)
        src = raster.PNG / name
        dst = ICONS / name
        dst.write_bytes(src.read_bytes())
        print(f"  {name:24} {px:>4} px  from {svg}")
    ico([ICONS / "favicon-16.png", ICONS / "favicon-32.png",
         ICONS / "favicon-48.png"], ICONS / "favicon.ico")
    print("  favicon.ico             16+32+48 px")


if __name__ == "__main__":
    main()
