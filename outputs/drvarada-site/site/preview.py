#!/usr/bin/env python
"""Build and preview drvarada.com locally — no Open Design required.

    python preview.py            # build + serve http://127.0.0.1:8788 + open browser
    python preview.py --no-open  # build + serve only
"""

from __future__ import annotations

import subprocess
import sys
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).parent
PORT = 8788


def main() -> int:
    build = subprocess.run([sys.executable, str(ROOT / "build.py")])
    if build.returncode != 0:
        return build.returncode

    handler = partial(SimpleHTTPRequestHandler, directory=str(ROOT / "dist"))
    server = ThreadingHTTPServer(("127.0.0.1", PORT), handler)
    url = f"http://127.0.0.1:{PORT}/"
    print(f"serving dist/ at {url}  (Ctrl+C to stop)")
    if "--no-open" not in sys.argv:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
