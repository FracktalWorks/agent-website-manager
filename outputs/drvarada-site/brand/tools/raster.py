"""Rasterise brand SVGs at exact pixel sizes using headless Chrome.

Chrome is used rather than a Python SVG library because it is the same renderer the
icons will actually face in a browser tab -- what it produces is what users will see.
"""
import pathlib
import subprocess

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
BRAND = pathlib.Path(__file__).resolve().parent.parent
ICONS = BRAND / "icons"

TMP = pathlib.Path(__file__).resolve().parent / "_work"
PNG = TMP / "png"
PNG.mkdir(parents=True, exist_ok=True)

WRAP = TMP / "_wrap.html"


def shot(svg: pathlib.Path, size: int, out: pathlib.Path, bg="transparent"):
    """Render `svg` at exactly `size` CSS pixels square."""
    WRAP.write_text(
        f'<style>html,body{{margin:0;padding:0;background:{bg}}}'
        f'img{{width:{size}px;height:{size}px;display:block}}</style>'
        f'<img src="{svg.as_uri()}">', encoding="utf-8")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1",
                    "--default-background-color=00000000",
                    f"--screenshot={out}", f"--window-size={size},{size}",
                    WRAP.as_uri()],
                   check=True, capture_output=True)


def shot_box(svg: pathlib.Path, w: int, h: int, out: pathlib.Path, bg="transparent"):
    """Render `svg` into an exact w x h box, for artwork that is not square."""
    WRAP.write_text(
        f'<style>html,body{{margin:0;padding:0;background:{bg}}}'
        f'img{{width:{w}px;height:{h}px;display:block}}</style>'
        f'<img src="{svg.as_uri()}">', encoding="utf-8")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1",
                    "--default-background-color=00000000",
                    f"--screenshot={out}", f"--window-size={w},{h}",
                    WRAP.as_uri()],
                   check=True, capture_output=True)


def render_png(svg_name, size, out_name, bg="transparent"):
    from PIL import Image
    out = PNG / out_name
    shot(ICONS / svg_name, size, out, bg)
    im = Image.open(out).convert("RGBA")
    if im.size != (size, size):     # Chrome enforces a minimum window width
        im.crop((0, 0, size, size)).save(out)
    return out
