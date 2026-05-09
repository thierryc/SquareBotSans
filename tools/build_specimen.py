from __future__ import annotations

import base64
import re
from pathlib import Path

from specimen_components import TemplateStore, build_pages
from specimen_data import ROOT, SRC, load_data

FONT_PATH = ROOT / "fonts/variable/SquareBotSans[ital,wdth,wght].woff2"
CSS_FILES = ["base.css", "formats.css", "pages.css"]
OUTPUTS = {
    "a4": ROOT / "specimen-squarebot-sans.html",
    "letter": ROOT / "specimen-squarebot-sans-letter.html",
}
PAGE_RULES = {
    "a4": "A4 landscape",
    "letter": "letter landscape",
}


def _font_face(font_b64: str) -> str:
    return f'''@font-face {{
  font-family: "SquareBot Sans";
  src: url("data:font/woff2;base64,{font_b64}") format("woff2-variations");
  font-weight: 200 900;
  font-stretch: 80% 120%;
  font-style: normal;
  font-display: block;
}}
'''


def _read_css() -> str:
    return "\n\n".join((SRC / "css" / name).read_text() for name in CSS_FILES)


def stylesheet(fmt: str, *, embed_font: bool) -> str:
    css = _read_css()
    if embed_font:
        css = re.sub(
            r"/\* DEV_FONT_FACE_START \*/.*?/\* DEV_FONT_FACE_END \*/\s*",
            "",
            css,
            flags=re.S,
        )
    page_rule = f"@page {{ size: {PAGE_RULES[fmt]}; margin: 0; }}\n"
    if embed_font:
        font_b64 = base64.b64encode(FONT_PATH.read_bytes()).decode("ascii")
        return _font_face(font_b64) + "\n" + page_rule + css
    return page_rule + css


def _dev_styles(fmt: str) -> str:
    links = "\n".join(f'<link rel="stylesheet" href="/specimen-src/css/{name}">' for name in CSS_FILES)
    return f'<style>@page {{ size: {PAGE_RULES[fmt]}; margin: 0; }}</style>\n{links}'


def _stamp_pages(pages: list[str]) -> str:
    total = f"{len(pages):02d}"
    body_parts = []
    for page_number, page in enumerate(pages, 1):
        body_parts.append(
            page.replace("__PAGE_NUMBER__", f"{page_number:02d}").replace("__TOTAL_PAGES__", total)
        )
    return "".join(body_parts)


def render(fmt: str, *, dev: bool = False, live_reload: bool = False) -> str:
    if fmt not in OUTPUTS:
        raise ValueError(f"Unsupported format: {fmt}")
    data = load_data(ROOT)
    templates = TemplateStore(SRC / "templates")
    pages = build_pages(data, templates)
    metadata = data["metadata"]
    title = metadata.get("title") if fmt == "a4" else metadata.get("letter_title", metadata.get("title"))
    dev_body = ""
    if live_reload:
        dev_body = '''<script>
(() => {
  let last = 0;
  async function poll() {
    try {
      const response = await fetch('/__mtime', { cache: 'no-store' });
      const data = await response.json();
      if (last && data.mtime !== last) location.reload();
      last = data.mtime;
    } catch (error) {}
    setTimeout(poll, 700);
  }
  poll();
})();
</script>'''
    return templates.render(
        "base.html",
        {
            "format_class": f"format-{fmt}",
            "title": title,
            "styles": _dev_styles(fmt) if dev else f"<style>\n{stylesheet(fmt, embed_font=True)}\n</style>",
            "dev_head": "",
            "body": _stamp_pages(pages),
            "dev_body": dev_body,
        },
    )


def write_outputs() -> None:
    for fmt, output in OUTPUTS.items():
        output.write_text(render(fmt), encoding="utf-8")
        print(f"Wrote {output.name}")


def main() -> None:
    write_outputs()


if __name__ == "__main__":
    main()
