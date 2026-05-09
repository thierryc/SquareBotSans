from __future__ import annotations

import argparse
import json
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

from build_specimen import render  # noqa: E402

WATCH_DIRS = [ROOT / "specimen-src", ROOT / "tools"]
WATCH_SUFFIXES = {".html", ".css", ".yaml", ".yml", ".json", ".py"}


def latest_mtime() -> int:
    latest = 0
    for base in WATCH_DIRS:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix in WATCH_SUFFIXES:
                latest = max(latest, path.stat().st_mtime_ns)
    return latest


class SpecimenPreviewHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def _send_text(self, text: str, content_type: str = "text/html; charset=utf-8") -> None:
        payload = text.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:  # noqa: N802 - stdlib hook
        path = urlparse(self.path).path.rstrip("/") or "/a4"
        if path in {"/a4", "/letter"}:
            fmt = "letter" if path == "/letter" else "a4"
            try:
                self._send_text(render(fmt, dev=True, live_reload=True))
            except Exception as exc:
                self.send_response(500)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(str(exc).encode("utf-8"))
            return
        if path == "/__mtime":
            self._send_text(json.dumps({"mtime": latest_mtime()}), "application/json; charset=utf-8")
            return
        super().do_GET()


def main() -> None:
    parser = argparse.ArgumentParser(description="Live preview server for the SquareBot Sans specimen.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), SpecimenPreviewHandler)
    print(f"Preview A4:     http://{args.host}:{args.port}/a4")
    print(f"Preview Letter: http://{args.host}:{args.port}/letter")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
