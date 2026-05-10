from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any


class SpecimenTemplateError(RuntimeError):
    pass


def render_template_text(template: str, context: dict[str, Any]) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1).strip()
        if key not in context:
            raise SpecimenTemplateError(f"Missing template value: {key}")
        return str(context[key])
    return re.sub(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}", replace, template)


class TemplateStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self._cache: dict[str, str] = {}

    def read(self, relative_path: str) -> str:
        if relative_path not in self._cache:
            path = self.root / relative_path
            if not path.exists():
                raise SpecimenTemplateError(f"Missing template: {path}")
            self._cache[relative_path] = path.read_text()
        return self._cache[relative_path]

    def render(self, relative_path: str, context: dict[str, Any]) -> str:
        return render_template_text(self.read(relative_path), context)


_CURRENT_DATA: dict[str, Any] = {}
_CURRENT_TEMPLATES: TemplateStore | None = None


def configure(data: dict[str, Any] | None, templates: TemplateStore | None) -> None:
    global _CURRENT_DATA, _CURRENT_TEMPLATES
    _CURRENT_DATA = data or {}
    _CURRENT_TEMPLATES = templates


def current_data() -> dict[str, Any]:
    return _CURRENT_DATA


def current_metadata() -> dict[str, Any]:
    return current_data().get("metadata", {})


def current_templates() -> TemplateStore:
    if _CURRENT_TEMPLATES is None:
        raise SpecimenTemplateError("TemplateStore has not been configured")
    return _CURRENT_TEMPLATES

def e(text: object) -> str:
    return html.escape(str(text), quote=True)


def attr_style(items: dict[str, object]) -> str:
    return "; ".join(f"{key}: {value}" for key, value in items.items())


def page_shell(number: int, title: str, content: str, classes: str = "") -> str:
    metadata = current_metadata()
    header = metadata.get("header", {})
    footer = metadata.get("footer", {})
    return current_templates().render(
        "page.html",
        {
            "classes": classes,
            "title": title,
            "header_left": header.get("left", metadata.get("display_name", "SQUARE BOT SANS")),
            "header_center": header.get("center", metadata.get("handle", "@ap.cx")),
            "content": content,
            "footer_left": footer.get("left", metadata.get("foundry", "Another Planet Creative Experience")),
            "footer_center": footer.get("center", metadata.get("version", "v2.003")),
            "page_number": "__PAGE_NUMBER__",
            "total_pages": "__TOTAL_PAGES__",
        },
    )


def back_cover_shell() -> str:
    metadata = current_metadata()
    return current_templates().render(
        "pages/back-cover.html",
        {"back_cover_mark": metadata.get("back_cover", {}).get("mark", "AP.CX")},
    )


def label_value(label: str, value: str, note: str = "") -> str:
    note_html = f'<div class="note">{e(note)}</div>' if note else ""
    return f"""
      <div class="meta-item">
        <div class="label">{e(label)}</div>
        <div class="value">{e(value)}</div>
        {note_html}
      </div>"""


def stat_card(label: str, value: str, note: str = "") -> str:
    return f"""
      <div class="stat-card">
        <div class="label">{e(label)}</div>
        <div class="stat-value">{e(value)}</div>
        <div class="note">{e(note)}</div>
      </div>"""


def axis_row(text: str, label: str, settings: dict[str, object], note: str = "") -> str:
    style = attr_style({"font-variation-settings": ", ".join(f'"{k}" {v}' for k, v in settings.items())})
    return f"""
      <div class="axis-row">
        <div class="axis-label">
          <span>{e(label)}</span>
          <small>{e(note)}</small>
        </div>
        <div class="axis-sample" style='{style}'>{e(text)}</div>
      </div>"""


def feature_row(name: str, tag: str, off: str, on: str, on_css: str, note: str = "") -> str:
    note_html = f'<div class="feature-note">{e(note)}</div>' if note else ""
    return f"""
      <div class="feature-row">
        <div>
          <div class="label">{e(tag)}</div>
          <div class="feature-name">{e(name)}</div>
          {note_html}
        </div>
        <div>
          <div class="label">OFF</div>
          <div class="feature-sample">{e(off)}</div>
        </div>
        <div>
          <div class="label">ON</div>
          <div class="feature-sample feature-on" style='{on_css}'>{e(on)}</div>
        </div>
      </div>"""


def specimen_row(label: str, text: str, css: str = "", sub: str = "") -> str:
    if sub:
        return f"""
      <div class="specimen-row">
        <div class="label">{e(label)}</div>
        <div class="specimen-line" style='{css}'>{e(text)}</div>
        <small>{e(sub)}</small>
      </div>"""
    return f"""
      <div class="specimen-row">
        <div class="label">{e(label)}</div>
        <div class="specimen-line" style='{css}'>{e(text)}</div>
      </div>"""


def ss_row(tag: str, name: str, off: str, on: str, settings: str, off_label: str = "OFF / DEFAULT", on_label: str = "ON / FEATURE") -> str:
    return f"""
      <div class="ss-row">
        <div>
          <div class="label">{e(tag)}</div>
          <div class="feature-name">{e(name)}</div>
        </div>
        <div>
          <div class="label">{e(off_label)}</div>
          <div class="ss-sample">{e(off)}</div>
        </div>
        <div>
          <div class="label">{e(on_label)}</div>
          <div class="ss-sample feature-on" style='font-feature-settings:{settings};'>{e(on)}</div>
        </div>
      </div>"""


def glyph_cell(mark: str, name: str) -> str:
    return f"""
      <div class="glyph-cell">
        <div class="glyph-mark">{e(mark)}</div>
        <div class="glyph-name">{e(name)}</div>
      </div>"""


def glyph_board(items: list[tuple[str, str]], classes: str = "") -> str:
    board_class = f"glyph-board {classes}".strip()
    return f"""
      <div class="{board_class}">
        {"".join(glyph_cell(mark, name) for mark, name in items)}
      </div>"""


def _data_pairs(rows: object) -> list[tuple[str, str]]:
    if not isinstance(rows, list):
        return []
    pairs: list[tuple[str, str]] = []
    for row in rows:
        if isinstance(row, dict) and "mark" in row and "name" in row:
            pairs.append((str(row["mark"]), str(row["name"])))
    return pairs


def glyph_group(name: str, fallback: list[tuple[str, str]]) -> list[tuple[str, str]]:
    rows = current_data().get("glyph_groups", {}).get(name)
    return _data_pairs(rows) or fallback


def stylistic_set_group(name: str, fallback: list[tuple[str, str]]) -> list[tuple[str, str]]:
    rows = current_data().get("glyph_groups", {}).get("stylistic_sets", {}).get(name)
    return _data_pairs(rows) or fallback


def alternate_cell(mark: str, name: str, feature_tags: tuple[str, ...]) -> str:
    features = '"kern" 1, "liga" 1, ' + ", ".join(f'"{tag}" 1' for tag in feature_tags)
    return f"""
      <div class="glyph-cell alternate-cell" style='--glyph-features: {features};'>
        <div class="glyph-mark">{e(mark)}</div>
        <div class="glyph-name">{e(name)}</div>
      </div>"""


def alternate_board(items: list[tuple[str, str]], feature_tags: tuple[str, ...], classes: str = "") -> str:
    board_class = f"glyph-board alternate-board {classes}".strip()
    return f"""
      <div class="{board_class}">
        {"".join(alternate_cell(mark, name, feature_tags) for mark, name in items)}
      </div>"""


def alternate_focus(mark: str, default_name: str, alternate_name: str, feature_tags: tuple[str, ...], classes: str = "") -> str:
    features = '"kern" 1, "liga" 1, ' + ", ".join(f'"{tag}" 1' for tag in feature_tags)
    focus_class = f"alternate-focus {classes}".strip()
    return f"""
      <div class="{focus_class}">
        <div class="alternate-focus-cell">
          <div class="label">OFF / default</div>
          <div class="focus-mark">{e(mark)}</div>
          <div class="focus-name">{e(default_name)}</div>
        </div>
        <div class="alternate-focus-cell is-on" style='--glyph-features: {features};'>
          <div class="label">ON / ss01 alternate</div>
          <div class="focus-mark">{e(mark)}</div>
          <div class="focus-name">{e(alternate_name)}</div>
        </div>
      </div>"""


def alternate_group(title: str, items: list[tuple[str, str]], feature_tags: tuple[str, ...], classes: str = "") -> str:
    return f"""
      <div class="alternate-group">
        <h3>{e(title)}</h3>
        {alternate_board(items, feature_tags, classes)}
      </div>"""


DEFAULT_INSTANCE_WEIGHTS = [
    ("ExtraLight", 200),
    ("Light", 300),
    ("Regular", 400),
    ("Medium", 500),
    ("SemiBold", 600),
    ("Bold", 700),
    ("ExtraBold", 800),
    ("Black", 900),
]

DEFAULT_INSTANCE_WIDTHS = [
    ("Condensed", 80),
    ("Regular", 100),
    ("Expanded", 120),
]


def instance_weights() -> list[tuple[str, int]]:
    rows = current_data().get("instances", {}).get("weights") or []
    return [(str(row["name"]), int(row["value"])) for row in rows] or DEFAULT_INSTANCE_WEIGHTS


def instance_widths() -> list[tuple[str, int]]:
    rows = current_data().get("instances", {}).get("widths") or []
    return [(str(row["name"]), int(row["value"])) for row in rows] or DEFAULT_INSTANCE_WIDTHS


def instance_name(width_label: str, weight_label: str, italic: bool) -> str:
    if italic:
        if width_label == "Regular" and weight_label == "Regular":
            return "Italic"
        if width_label == "Regular":
            return f"{weight_label} Italic"
        if weight_label == "Regular":
            return f"{width_label} Italic"
        return f"{width_label} {weight_label} Italic"
    if width_label == "Regular":
        return weight_label
    return f"{width_label} {weight_label}"


def instance_cell(width_label: str, width: int, weight_label: str, weight: int, italic: bool) -> str:
    ital = 1 if italic else 0
    name = instance_name(width_label, weight_label, italic)
    return f"""
      <div class="instance-cell" style='font-variation-settings:"wdth" {width}, "wght" {weight}, "ital" {ital}'>
        <div class="instance-name">{e(name)}</div>
        <div class="instance-sample">ORBIT</div>
        <div class="instance-meta">wdth {width} / wght {weight} / ital {ital}</div>
      </div>"""


def instance_column(width_label: str, width: int, italic: bool) -> str:
    ital = 1 if italic else 0
    return f"""
      <div class="instance-column">
        <div class="instance-column-head">
          <strong>{e(width_label)}</strong>
          <span>wdth {width} / ital {ital}</span>
        </div>
        {"".join(instance_cell(width_label, width, weight_label, weight, italic) for weight_label, weight in instance_weights())}
      </div>"""


def instance_page(italic: bool) -> str:
    mode = "Italic" if italic else "Roman"
    label = "Instance map / Italic" if italic else "Instance map / Roman"
    note = "Italic instances across the same width and weight system." if italic else "Roman instances across condensed, regular, and expanded widths."
    return f"""
      <div class="instance-page-layout">
        <div class="section-title">
          <div class="label">{e(label)}</div>
          <h2>{e(mode)} instances.</h2>
          <p>{e(note)}</p>
        </div>
        <div class="instance-map">
          {"".join(instance_column(width_label, width, italic) for width_label, width in instance_widths())}
        </div>
      </div>"""


def cover_content() -> str:
    metadata = current_metadata()
    cover = metadata.get("cover", {})
    wordmark = cover.get("wordmark", "R2BOT")
    if wordmark != "R2BOT":
        wordmark_html = e(wordmark)
    else:
        wordmark_html = """
          <span class="wordmark-R0" style='font-variation-settings:"wdth" 100, "wght" 900, "ital" 0'>R</span>
          <span class="wordmark-21" style='font-variation-settings:"wdth" 100, "wght" 360, "ital" 1'>2</span>
          <span class="wordmark-B2 wordmark-b" style='font-stretch:120%; font-variation-settings:"wdth" 120, "wght" 900, "ital" 1'>B</span>
          <span class="wordmark-O3" style='font-stretch:80%; font-variation-settings:"wdth" 80, "wght" 720, "ital" 0'>O</span>
          <span class="wordmark-T4" style='font-variation-settings:"wdth" 100, "wght" 260, "ital" 0'>T</span>
        """
    axis_strip = "".join(f"<span>{e(item)}</span>" for item in cover.get("axis_strip", []))
    return current_templates().render(
        "pages/cover.html",
        {
            "cover_kicker": cover.get("kicker", ""),
            "cover_title": cover.get("title", metadata.get("family", "SquareBot Sans")),
            "cover_wordmark": wordmark,
            "cover_wordmark_html": wordmark_html,
            "cover_axis_strip": axis_strip,
        },
    )


def axis_demo_rows(axis_name: str) -> list[dict[str, object]]:
    rows = current_data().get("axes", {}).get(axis_name, {}).get("rows") or []
    return [dict(row) for row in rows]


def axis_demo_title(axis_name: str, fallback: str) -> str:
    return str(current_data().get("axes", {}).get(axis_name, {}).get("title") or fallback)


def axis_demo_settings(axis_name: str, row: dict[str, object]) -> dict[str, object]:
    value = row.get("value")
    if axis_name == "width":
        return {"wdth": value, "wght": 700, "ital": 0}
    if axis_name == "weight":
        return {"wdth": 100, "wght": value, "ital": 0}
    return {"wdth": 105, "wght": 520, "ital": value}


def tech_block(label: str, body: str) -> str:
    return f"""
      <div class="tech-block">
        <div class="tech-label">{e(label)}</div>
        <div class="tech-copy">{body}</div>
      </div>"""


def technical_specs_content() -> str:
    metadata = current_metadata()
    technical = current_data().get("technical", {})
    metrics = technical.get("metrics", {})
    counts = technical.get("counts", {})
    formats = technical.get("formats", {})
    language_list = ", ".join(str(language) for language in technical.get("languages", []))
    sections = [
        tech_block(
            "File formats",
            f"<p>Desktop: {e(formats.get('desktop', 'OTF'))}<br>Web: {e(formats.get('web', 'WOFF2'))}<br>App: {e(formats.get('app', 'OTF / TTF'))}</p>",
        ),
        tech_block(
            "Design space",
            f"<p>Width 80-120<br>Weight 200-900<br>Italic positions 0 / 1<br>{e(counts.get('masters', 12))} masters / {e(counts.get('instances', 49))} exporting instances</p>",
        ),
        tech_block(
            "Metrics",
            f"<p>UPM 1000<br>Ascender {e(metrics.get('ascender', 729))} / Cap height {e(metrics.get('cap_height', 729))} / Descender {e(metrics.get('descender', -167))}<br>x-height range {e(metrics.get('x_height', '515-546'))}</p>",
        ),
        tech_block(
            "Glyph production",
            f"<p>{e(counts.get('glyphs', 947))} glyphs total<br>{e(counts.get('exporting_glyphs', 909))} exporting / {e(counts.get('non_exporting_glyphs', 38))} non-exporting<br>{e(counts.get('unicode_encoded_glyphs', 574))} Unicode-encoded glyphs<br>All glyphs include 12 production layers</p>",
        ),
        tech_block(
            "SIL Font",
            '<p>SIL Open Font License<br><a href="https://ap.cx">ap.cx</a></p>',
        ),
        tech_block(
            "About",
            f"<p>{e(metadata.get('foundry', 'Another Planet Creative Experience'))} develops type systems for display typography, interface density, technical signage, and speculative visual identities.</p>",
        ),
        tech_block("Contact", '<p><a href="mailto:hello@ap.cx">hello@ap.cx</a></p>'),
    ]
    return current_templates().render(
        "pages/technical-specifications.html",
        {
            "technical_title": f"{metadata.get('family', 'Square Bot Sans')} {metadata.get('version', 'v2.003')}",
            "language_list": e(language_list),
            "technical_sections": "".join(sections),
        },
    )


def build_pages(data: dict | None = None, templates: TemplateStore | None = None) -> list[str]:
    configure(data, templates)
    pages: list[str] = []

    pages.append(
        page_shell(
            1,
            "Cover",
            cover_content(),
            "cover",
        )
    )

    pages.append(
        page_shell(
            2,
            "Identity",
            f"""
            <div class="grid identity-grid">
              <div class="section-title col-1-5">
                <div class="label">Identity / Concept</div>
                <h2>Squared technical forms for titles, signal, and sci-fi display systems.</h2>
              </div>
              <div class="intro-copy col-6-12">
                <p>SquareBot Sans is a display-first modular sans for cinematic titles, speculative systems, technical signage, and identity-scale typography. Its squared rhythm gives large words a controlled sci-fi voice without leaning on decorative effects.</p>
              </div>
              <div class="meta-panel col-1-12">
                """ +
            label_value("Designed for", "Sci-fi display", "Title systems, signage, and identity scale")
            + label_value("Masters", "12", "Condensed and expanded extremes across three weights and two styles")
            + label_value("Instances", "49 exporting", "Static family map for production delivery")
            + label_value("Glyph system", "947 glyphs", "Latin, symbols, numerals, marks, and technical punctuation")
            + """
              </div>
            </div>
            """,
        )
    )

    pages.append(
        page_shell(
            3,
            "Administrative Data",
            f"""
            <div class="diagnostic">
              <div class="diagnostic-title">
                <div class="label">Administrative Data Card</div>
                <h2>SquareBot Sans / production state</h2>
              </div>
              <div class="diagnostic-grid">
                """
            + stat_card("Family", "SquareBot Sans", "Squared technical sans")
            + stat_card("Version", current_metadata().get("version", "v2.003").lstrip("v"), "UPM 1000")
            + stat_card("Production", "49 instances", "Active/exporting")
            + stat_card("Design Space", "3 axes", "wdth / wght / ital")
            + stat_card("Metrics", "729 / 729 / -167", "Ascender / cap height / descender")
            + stat_card("Glyph System", "947 total", "909 exporting / 38 non-exporting")
            + stat_card("Unicode", "574 encoded", "Latin plus marks and symbols")
            + stat_card("Layers", "11,364", "947 glyphs x 12 masters")
            + """
              </div>
            </div>
            """,
            "data-card",
        )
    )

    weights = [("ExtraLight 200", 200), ("Regular 400", 400), ("Black 900", 900)]
    widths = [("Condensed", 80), ("Regular", 100), ("Expanded", 120)]
    matrix_cells = []
    for wlabel, weight in weights:
        for dlabel, width in widths:
            matrix_cells.append(
                f"""
                <div class="matrix-cell" style='font-variation-settings:"wdth" {width}, "wght" {weight}, "ital" 0'>
                  <div class="label">{e(wlabel)} / {e(dlabel)}</div>
                  <div>Aa</div>
                  <small>R0 Data</small>
                </div>"""
            )
    pages.append(
        page_shell(
            4,
            "Design Space Matrix",
            f"""
            <div class="section-title">
              <div class="label">Design Space Matrix</div>
              <h2>Width and weight system at a glance.</h2>
            </div>
            <div class="family-matrix">
              <div class="matrix-head empty"></div>
              <div class="matrix-head">Condensed</div>
              <div class="matrix-head">Regular</div>
              <div class="matrix-head">Expanded</div>
              <div class="matrix-row-label">ExtraLight 200</div>
              {"".join(matrix_cells[0:3])}
              <div class="matrix-row-label">Regular 400</div>
              {"".join(matrix_cells[3:6])}
              <div class="matrix-row-label">Black 900</div>
              {"".join(matrix_cells[6:9])}
            </div>
            """,
            "matrix-page",
        )
    )

    pages.append(
        page_shell(
            5,
            "Roman Instances",
            instance_page(False),
            "instance-page roman-instance-page",
        )
    )

    pages.append(
        page_shell(
            6,
            "Italic Instances",
            instance_page(True),
            "instance-page italic-instance-page",
        )
    )

    pages.append(
        page_shell(
            5,
            "Width Axis",
            f"""
            <div class="section-title">
              <div class="label">Axis / wdth</div>
              <h2>{e(axis_demo_title("width", "External width range 80-120."))}</h2>
            </div>
            <div class="axis-stack width-stack">
              """
            + "\n".join(
                axis_row(
                    str(row.get("text", "")),
                    str(row.get("label", "")),
                    axis_demo_settings("width", row),
                    str(row.get("note", "")),
                )
                for row in axis_demo_rows("width")
            )
            + """
            </div>
            """,
        )
    )

    pages.append(
        page_shell(
            6,
            "Weight Axis",
            f"""
            <div class="section-title">
              <div class="label">Axis / wght</div>
              <h2>{e(axis_demo_title("weight", "Weight range from ExtraLight to Black."))}</h2>
            </div>
            <div class="axis-stack weight-stack">
              """
            + "\n".join(
                axis_row(
                    str(row.get("text", "")),
                    str(row.get("label", "")),
                    axis_demo_settings("weight", row),
                    str(row.get("note", "")),
                )
                for row in axis_demo_rows("weight")
            )
            + """
            </div>
            """,
        )
    )

    pages.append(
        page_shell(
            7,
            "Italic Positions",
            f"""
            <div class="section-title">
              <div class="label">Positions / ital</div>
              <h2>{e(axis_demo_title("italic", "Italic positions: roman and italic."))}</h2>
            </div>
            <div class="axis-stack italic-stack">
              """
            + "\n".join(
                axis_row(
                    str(row.get("text", "")),
                    str(row.get("label", "")),
                    axis_demo_settings("italic", row),
                    str(row.get("note", "")),
                )
                for row in axis_demo_rows("italic")
            )
            + """
            </div>
            """,
        )
    )

    feature_groups = [
        ("Core Typography", "kern, liga, case", "Implemented in the current export. calt is not present."),
        ("Numerals", "tnum, pnum, zero, frac, numr, dnom, ordn", "Implemented numeral features. zero maps zero to zero.slash; lnum and onum are not present in current export."),
        ("Position", "numr, dnom, ordn", "Used for fractions and ordinals. sups/subs are not present in current export."),
        ("Stylistic Sets", "ss01-ss04", "Functional in the current variable font export."),
        ("Symbols", "arrows, math, separators, marks", "Glyph coverage plus mark/mkmk positioning in GPOS."),
    ]
    pages.append(
        page_shell(
            8,
            "OpenType Overview",
            """
            <div class="section-title">
              <div class="label">OpenType Feature Taxonomy</div>
              <h2>Functional features in the current variable export.</h2>
            </div>
            <div class="feature-taxonomy">
              """
            + "\n".join(
                f"""
                <div class="feature-card">
                  <div class="label">{e(group)}</div>
                  <div class="feature-tags">{e(tags)}</div>
                  <p>{e(note)}</p>
                </div>"""
                for group, tags, note in feature_groups
            )
            + """
              <div class="feature-card muted-card">
                <div class="label">Not presented as active features</div>
                <div class="feature-tags">ss05-ss16 / lnum / onum / sups / subs</div>
                <p>These labels appeared in the creative brief, but are not functional tags in the inspected variable WOFF2.</p>
              </div>
            </div>
            """,
        )
    )

    pages.append(
        page_shell(
            9,
            "OpenType Comparisons",
            """
            <div class="section-title compact-title">
              <div class="label">OpenType ON/OFF Comparisons</div>
              <h2>Functional checks for layout engines and buyers.</h2>
            </div>
            <div class="feature-table">
              """
            + feature_row("Tabular figures", "tnum", "1,000,000", "1,000,000", 'font-feature-settings:"tnum" 1, "pnum" 0;')
            + feature_row("Proportional figures", "pnum", "$1,204.89", "$1,204.89", 'font-feature-settings:"pnum" 1, "tnum" 0;')
            + feature_row("Slashed zero", "zero", "O0 1000", "O0 1000", 'font-feature-settings:"zero" 1;', "GSUB maps zero to zero.slash.")
            + feature_row("Automatic fractions", "frac", "5/32 kg", "5/32 kg", 'font-feature-settings:"frac" 1;')
            + feature_row("Case-sensitive punctuation", "case", "{[(HEIGHT)]}", "{[(HEIGHT)]}", 'font-feature-settings:"case" 1;')
            + feature_row("Ordinal indicators", "ordn", "Station 1a", "Station 1a", 'font-feature-settings:"ordn" 1;')
            + feature_row("Discretionary ligatures", "dlig", "<- -> => =< !=", "<- -> => =< !=", 'font-feature-settings:"dlig" 1;')
            + """
            </div>
            """,
        )
    )

    ss_cards = [
        ("SS01", "Alternate a + rounded punctuation", "area grid: [a07]?", "area grid: [a07]?", '"ss01" 1', "OFF / default a", "ON / ss01 a"),
        ("SS02", "Alternate l / fl forms", "low orbital flight", "low orbital flight", '"ss02" 1', "OFF / default l", "ON / ss02 l"),
        ("SS03", "Compact r forms", "rare reactor corridor", "rare reactor corridor", '"ss03" 1', "OFF / default r", "ON / compact r"),
        ("SS04", "Code zero + technical I/J", "O0 I1 / JIG / INDEX", "O0 I1 / JIG / INDEX", '"ss04" 1', "OFF / default zero/I/J", "ON / ss04 zero/I/J"),
    ]
    pages.append(
        page_shell(
            10,
            "Stylistic Sets",
            """
            <div class="section-title">
              <div class="label">Stylistic Sets</div>
              <h2>Stylistic sets with OFF / ON comparisons.</h2>
            </div>
            <div class="ss-table">
              """
            + "\n".join(
                ss_row(tag, name, off, on, settings, off_label, on_label)
                for tag, name, off, on, settings, off_label, on_label in ss_cards
            )
            + """
            </div>
            """,
        )
    )

    pages.append(
        page_shell(
            11,
            "Feature Story",
            """
            <div class="story-page">
              <div class="story-row default-row">
                <span class="label">DEFAULT</span>
                <strong>Orbital index</strong>
              </div>
              <div class="story-row" style='font-feature-settings:"ss01" 1; font-variation-settings:"wdth" 90, "wght" 900, "ital" 0;'>
                <span class="label">SS01 ALT A / ROUND PUNCT.</span>
                <strong>Area: [a07]?</strong>
              </div>
              <div class="story-row" style='font-feature-settings:"ss02" 1; font-variation-settings:"wdth" 120, "wght" 760, "ital" 0;'>
                <span class="label">SS02 ALT L / FL</span>
                <strong>Low orbital flight</strong>
              </div>
              <div class="story-row" style='font-feature-settings:"ss03" 1, "ss04" 1; font-variation-settings:"wdth" 100, "wght" 420, "ital" 1;'>
                <span class="label">SS03 COMPACT R / SS04 I/J</span>
                <strong>JIG rare corridor</strong>
              </div>
            </div>
            """,
            "feature-story",
        )
    )

    pages.append(
        page_shell(
            12,
            "Numerals",
            """
            <div class="section-title">
              <div class="label">Numeral System</div>
              <h2>Financial, data, and technical samples.</h2>
            </div>
            <div class="numeral-grid">
              """
            + specimen_row("Proportional", "$1,204.89 / €8,760.00", 'font-feature-settings:"pnum" 1;')
            + specimen_row("Tabular", "$1,204.89 / €8,760.00", 'font-feature-settings:"tnum" 1;')
            + specimen_row("Date", "2026-05-08  /  ID 000742", 'font-feature-settings:"tnum" 1;')
            + specimen_row("Fractions", "5/32  7/16  13/64", 'font-feature-settings:"frac" 1;')
            + specimen_row("Constants", "3.14159 / 2.71828 / 1.61803", 'font-feature-settings:"tnum" 1;')
            + specimen_row("Slashed zero", "O0 / 1000 / 2026", 'font-feature-settings:"zero" 1;')
            + specimen_row("Not in current export", "oldstyle figures", "font-size:22pt; white-space:normal; line-height:1.05;", "onum is not present")
            + """
            </div>
            """,
        )
    )

    pages.append(
        page_shell(
            13,
            "Signage",
            """
            <div class="signage">
              <div style='font-variation-settings:"wdth" 120, "wght" 900, "ital" 0'>GATE 04</div>
              <div style='font-variation-settings:"wdth" 80, "wght" 700, "ital" 0'>SECTION 729</div>
              <div style='font-variation-settings:"wdth" 100, "wght" 400, "ital" 1'>EXPORT READY</div>
              <div style='font-variation-settings:"wdth" 120, "wght" 300, "ital" 0'>LOW ORBIT</div>
              <div style='font-variation-settings:"wdth" 90, "wght" 900, "ital" 0'>TYPE CONTROL</div>
            </div>
            """,
            "signage-page",
        )
    )

    para = (
        "SquareBot Sans is intended to lead with title-scale presence. "
        "At smaller sizes it can support labels and short captions, but its strongest voice appears in display typography, signage, identity lockups, and sci-fi editorial systems. "
        "The family stays engineered and controlled without becoming theatrical."
    )
    pages.append(
        page_shell(
            14,
            "Display Settings",
            """
            <div class="section-title">
              <div class="label">Display Settings</div>
              <h2>Title scale, captions, and short technical copy.</h2>
            </div>
            <div class="text-settings">
              """
            + "\n".join(
                f"""
                <div class="text-sample" style='font-size:{size}pt; line-height:{line};'>
                  <div class="label">{size} pt</div>
                  <p>{e(para)}</p>
                </div>"""
                for size, line in ((8, 1.45), (10, 1.42), (12, 1.36), (16, 1.25))
            )
            + """
            </div>
            """,
        )
    )

    character_blocks = [
        ("Uppercase Latin", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
        ("Lowercase Latin", "abcdefghijklmnopqrstuvwxyz"),
        ("Numerals", "0123456789 00 11 24 68 90"),
        ("Punctuation", ".,:;!?/\\()[]{}-_'\""),
        ("Currency", "$ € £ ¥ ¢ ₩ ₽ ₹ ₺ ₿"),
        ("Math", "+ − × ÷ = ≠ < > ≤ ≥ ± ≈ ∞ ∑ ∆ √"),
        ("Arrows", "← ↑ → ↓ ↔ ↕ ↖ ↗ ↘ ↙"),
        ("Symbols", "@ # % & * § ¶ © ® ™ ◊ ● ○"),
        ("Diacritics", "ÁÂÄÀÅÃ ĆČÇ ĖĘË È ÍÏ Ñ ÓÖØ ÚÜ Ý ŹŽ"),
    ]
    pages.append(
        page_shell(
            15,
            "Character Set",
            """
            <div class="section-title compact-title">
              <div class="label">Character Set Overview</div>
              <h2>Grouped coverage for inspection.</h2>
            </div>
            <div class="character-grid">
              """
            + "\n".join(
                f"""
                <div class="character-block">
                  <div class="label">{e(label)}</div>
                  <p>{e(chars)}</p>
                </div>"""
                for label, chars in character_blocks
            )
            + """
            </div>
            """,
        )
    )

    uppercase_board = [
        ("A", "A"), ("B", "B"), ("C", "C"), ("D", "D"), ("E", "E"), ("F", "F"), ("G", "G"), ("H", "H"), ("I", "I"), ("J", "J"), ("K", "K"), ("L", "L"), ("M", "M"), ("N", "N"), ("O", "O"),
        ("P", "P"), ("Q", "Q"), ("R", "R"), ("S", "S"), ("T", "T"), ("U", "U"), ("V", "V"), ("W", "W"), ("X", "X"), ("Y", "Y"), ("Z", "Z"), ("Á", "Aacute"), ("Ă", "Abreve"), ("Â", "Acircumflex"), ("Ä", "Adieresis"),
        ("À", "Agrave"), ("Ā", "Amacron"), ("Ą", "Aogonek"), ("Å", "Aring"), ("Ã", "Atilde"), ("Æ", "AE"), ("Ć", "Cacute"), ("Č", "Ccaron"), ("Ç", "Ccedilla"), ("Ĉ", "Ccircumflex"), ("Ċ", "Cdotaccent"), ("Ð", "Eth"), ("Ď", "Dcaron"), ("Đ", "Dcroat"), ("É", "Eacute"),
        ("Ě", "Ecaron"), ("Ê", "Ecircumflex"), ("Ë", "Edieresis"), ("Ė", "Edotaccent"), ("È", "Egrave"), ("Ē", "Emacron"), ("Ę", "Eogonek"), ("Ğ", "Gbreve"), ("Ĝ", "Gcircumflex"), ("Ģ", "Gcommaaccent"), ("Ġ", "Gdotaccent"), ("Ħ", "Hbar"), ("Ĥ", "Hcircumflex"), ("Í", "Iacute"), ("Ĭ", "Ibreve"),
        ("Î", "Icircumflex"), ("Ï", "Idieresis"), ("İ", "Idotaccent"), ("Ì", "Igrave"), ("Ĳ", "IJ"), ("Ī", "Imacron"), ("Į", "Iogonek"), ("Ĩ", "Itilde"), ("Ĵ", "Jcircumflex"), ("Ķ", "Kcommaaccent"), ("Ĺ", "Lacute"), ("Ľ", "Lcaron"), ("Ļ", "Lcommaaccent"), ("Ł", "Lslash"), ("Ń", "Nacute"),
        ("Ň", "Ncaron"), ("Ņ", "Ncommaaccent"), ("Ñ", "Ntilde"), ("Ŋ", "Eng"), ("Ó", "Oacute"), ("Ŏ", "Obreve"), ("Ô", "Ocircumflex"), ("Ö", "Odieresis"), ("Œ", "OE"), ("Ò", "Ograve"), ("Ő", "Ohungarumlaut"), ("Ō", "Omacron"), ("Ø", "Oslash"), ("Õ", "Otilde"), ("Ŕ", "Racute"),
        ("Ř", "Rcaron"), ("Ŗ", "Rcommaaccent"), ("Ś", "Sacute"), ("Š", "Scaron"), ("Ş", "Scedilla"), ("Ŝ", "Scircumflex"), ("Ș", "Scommaaccent"), ("Ŧ", "Tbar"), ("Ť", "Tcaron"), ("Ţ", "Tcedilla"), ("Ț", "Tcommaaccent"), ("Þ", "Thorn"), ("Ú", "Uacute"), ("Ŭ", "Ubreve"), ("Û", "Ucircumflex"),
        ("Ü", "Udieresis"), ("Ù", "Ugrave"), ("Ű", "Uhungarumlaut"), ("Ū", "Umacron"), ("Ų", "Uogonek"), ("Ů", "Uring"), ("Ũ", "Utilde"), ("Ŵ", "Wcircumflex"), ("Ẅ", "Wdieresis"), ("Ẁ", "Wgrave"), ("Ý", "Yacute"), ("Ŷ", "Ycircumflex"), ("Ÿ", "Ydieresis"), ("Ỳ", "Ygrave"), ("Ź", "Zacute"),
        ("Ž", "Zcaron"), ("Ż", "Zdotaccent"), ("ẞ", "Germandbls"),
    ]
    uppercase_board = glyph_group("uppercase", uppercase_board)
    pages.append(
        page_shell(
            16,
            "Glyph Preview Uppercase",
            """
            <div class="section-title compact-title">
              <div class="label">Glyph Preview Board</div>
              <h2>Uppercase Latin</h2>
            </div>
            """
            + glyph_board(uppercase_board, "uppercase-board"),
            "glyph-page",
        )
    )

    lowercase_board = [
        ("a", "a"), ("b", "b"), ("c", "c"), ("d", "d"), ("e", "e"), ("f", "f"), ("g", "g"), ("h", "h"), ("i", "i"), ("j", "j"), ("k", "k"), ("l", "l"), ("m", "m"), ("n", "n"), ("o", "o"),
        ("p", "p"), ("q", "q"), ("r", "r"), ("s", "s"), ("t", "t"), ("u", "u"), ("v", "v"), ("w", "w"), ("x", "x"), ("y", "y"), ("z", "z"), ("á", "aacute"), ("ă", "abreve"), ("â", "acircumflex"), ("ä", "adieresis"),
        ("à", "agrave"), ("ā", "amacron"), ("ą", "aogonek"), ("å", "aring"), ("ã", "atilde"), ("æ", "ae"), ("ć", "cacute"), ("č", "ccaron"), ("ç", "ccedilla"), ("ĉ", "ccircumflex"), ("ċ", "cdotaccent"), ("ď", "dcaron"), ("đ", "dcroat"), ("ð", "eth"), ("é", "eacute"),
        ("ě", "ecaron"), ("ê", "ecircumflex"), ("ë", "edieresis"), ("ė", "edotaccent"), ("è", "egrave"), ("ē", "emacron"), ("ę", "eogonek"), ("ğ", "gbreve"), ("ĝ", "gcircumflex"), ("ģ", "gcommaaccent"), ("ġ", "gdotaccent"), ("ĥ", "hcircumflex"), ("ħ", "hbar"), ("í", "iacute"), ("ĭ", "ibreve"),
        ("î", "icircumflex"), ("ï", "idieresis"), ("ı", "idotless"), ("ì", "igrave"), ("ĳ", "ij"), ("ī", "imacron"), ("į", "iogonek"), ("ĩ", "itilde"), ("ĵ", "jcircumflex"), ("ķ", "kcommaaccent"), ("ĸ", "kgreenlandic"), ("ĺ", "lacute"), ("ľ", "lcaron"), ("ļ", "lcommaaccent"), ("ł", "lslash"),
        ("ń", "nacute"), ("ň", "ncaron"), ("ņ", "ncommaaccent"), ("ñ", "ntilde"), ("ŋ", "eng"), ("ó", "oacute"), ("ŏ", "obreve"), ("ô", "ocircumflex"), ("ö", "odieresis"), ("œ", "oe"), ("ò", "ograve"), ("ő", "ohungarumlaut"), ("ō", "omacron"), ("ø", "oslash"), ("õ", "otilde"),
        ("ŕ", "racute"), ("ř", "rcaron"), ("ŗ", "rcommaaccent"), ("ś", "sacute"), ("š", "scaron"), ("ş", "scedilla"), ("ŝ", "scircumflex"), ("ș", "scommaaccent"), ("ß", "germandbls"), ("ŧ", "tbar"), ("ť", "tcaron"), ("ţ", "tcedilla"), ("ț", "tcommaaccent"), ("þ", "thorn"), ("ú", "uacute"),
        ("ŭ", "ubreve"), ("û", "ucircumflex"), ("ü", "udieresis"), ("ù", "ugrave"), ("ű", "uhungarumlaut"), ("ū", "umacron"), ("ų", "uogonek"), ("ů", "uring"), ("ũ", "utilde"), ("ŵ", "wcircumflex"), ("ẅ", "wdieresis"), ("ẁ", "wgrave"), ("ý", "yacute"), ("ŷ", "ycircumflex"), ("ÿ", "ydieresis"),
        ("ỳ", "ygrave"), ("ź", "zacute"), ("ž", "zcaron"), ("ż", "zdotaccent"),
    ]
    lowercase_board = glyph_group("lowercase", lowercase_board)
    pages.append(
        page_shell(
            17,
            "Glyph Preview Lowercase",
            """
            <div class="section-title compact-title">
              <div class="label">Glyph Preview Board</div>
              <h2>Lowercase Latin</h2>
            </div>
            """
            + glyph_board(lowercase_board, "lowercase-board"),
            "glyph-page",
        )
    )

    symbol_board = [
        ("`", "grave"), ("´", "acute"), ("ˆ", "circumflex"), ("˜", "tilde"), ("ˇ", "caron"), ("¨", "dieresis"), ("¯", "macron"), ("˘", "breve"), ("˚", "ring"), ("˝", "hungarumlaut"), ("˙", "dotaccent"), (",", "comma"), (";", "semicolon"), (":", "colon"), (".", "period"),
        ("…", "ellipsis"), ("-", "hyphen"), ("–", "endash"), ("—", "emdash"), ("_", "underscore"), ("!", "exclam"), ("¡", "exclamdown"), ("?", "question"), ("¿", "questiondown"), ("'", "quotesingle"), ('"', "quotedbl"), ("“", "quotedblleft"), ("”", "quotedblright"), ("‘", "quoteleft"), ("’", "quoteright"),
        ("/", "slash"), ("\\", "backslash"), ("|", "bar"), ("(", "parenleft"), (")", "parenright"), ("[", "bracketleft"), ("]", "bracketright"), ("{", "braceleft"), ("}", "braceright"), ("@", "at"), ("&", "ampersand"), ("#", "numbersign"), ("%", "percent"), ("‰", "perthousand"), ("№", "numero"),
        ("0", "zero"), ("1", "one"), ("2", "two"), ("3", "three"), ("4", "four"), ("5", "five"), ("6", "six"), ("7", "seven"), ("8", "eight"), ("9", "nine"), ("¼", "onequarter"), ("½", "onehalf"), ("¾", "threequarters"), ("⅓", "onethird"), ("⅔", "twothirds"),
        ("$", "dollar"), ("¢", "cent"), ("£", "sterling"), ("¥", "yen"), ("€", "euro"), ("₩", "won"), ("₽", "ruble"), ("₹", "rupee"), ("₺", "lira"), ("₿", "bitcoin"), ("©", "copyright"), ("®", "registered"), ("™", "trademark"), ("§", "section"), ("¶", "paragraph"),
        ("+", "plus"), ("−", "minus"), ("×", "multiply"), ("÷", "divide"), ("=", "equal"), ("≠", "notequal"), ("<", "less"), (">", "greater"), ("≤", "lessequal"), ("≥", "greaterequal"), ("±", "plusminus"), ("≈", "approxequal"), ("∞", "infinity"), ("√", "radical"), ("∑", "summation"),
        ("∆", "increment"), ("Ω", "Omega"), ("π", "pi"), ("µ", "micro"), ("●", "blackcircle"), ("○", "whitecircle"), ("◊", "lozenge"), ("•", "bullet"), ("*", "asterisk"), ("←", "leftarrow"), ("↑", "uparrow"), ("→", "rightarrow"), ("↓", "downarrow"), ("↔", "leftrightarrow"), ("↕", "updownarrow"),
        ("↖", "northwest"), ("↗", "northeast"), ("↘", "southeast"), ("↙", "southwest"),
    ]
    symbol_board = glyph_group("symbols", symbol_board)
    pages.append(
        page_shell(
            18,
            "Glyph Preview Symbols",
            """
            <div class="section-title compact-title">
              <div class="label">Glyph Preview Board</div>
              <h2>Figures, punctuation, symbols</h2>
            </div>
            """
            + glyph_board(symbol_board, "symbol-board"),
            "glyph-page",
        )
    )

    # Stylistic-set substitutions read from Glyphs App OpenType features via MCP.
    ss01_alternates = [
        ("Ặ", "uni1EB6.ss01"), ("Ậ", "uni1EAC.ss01"), ("Ä", "Adieresis.ss01"), ("Ạ", "uni1EA0.ss01"), ("Ċ", "Cdotaccent.ss01"), ("Ệ", "uni1EC6.ss01"), ("Ë", "Edieresis.ss01"), ("Ė", "Edotaccent.ss01"), ("Ẹ", "uni1EB8.ss01"), ("Ġ", "Gdotaccent.ss01"), ("Ï", "Idieresis.ss01"), ("İ", "Idotaccent.ss01"), ("Ị", "uni1ECA.ss01"), ("Ŀ", "Ldot.ss01"), ("Ộ", "uni1ED8.ss01"),
        ("Ö", "Odieresis.ss01"), ("Ọ", "uni1ECC.ss01"), ("Ợ", "uni1EE2.ss01"), ("Q", "Q.ss01"), ("Ü", "Udieresis.ss01"), ("Ụ", "uni1EE4.ss01"), ("Ừ", "uni1EF0.ss01"), ("Ẅ", "Wdieresis.ss01"), ("Ÿ", "Ydieresis.ss01"), ("Ỵ", "uni1EF4.ss01"), ("Ż", "Zdotaccent.ss01"), ("a", "a.ss01"), ("á", "aacute.ss01"), ("ă", "abreve.ss01"), ("ắ", "uni1EAF.ss01"),
        ("ặ", "uni1EB7.ss01"), ("ằ", "uni1EB1.ss01"), ("ẳ", "uni1EB3.ss01"), ("ẵ", "uni1EB5.ss01"), ("â", "acircumflex.ss01"), ("ấ", "uni1EA5.ss01"), ("ậ", "uni1EAD.ss01"), ("ầ", "uni1EA7.ss01"), ("ẩ", "uni1EA9.ss01"), ("ẫ", "uni1EAB.ss01"), ("ä", "adieresis.ss01"), ("ạ", "uni1EA1.ss01"), ("à", "agrave.ss01"), ("ả", "uni1EA3.ss01"), ("ā", "amacron.ss01"),
        ("ą", "aogonek.ss01"), ("å", "aring.ss01"), ("ã", "atilde.ss01"), ("ċ", "cdotaccent.ss01"), ("ệ", "uni1EC7.ss01"), ("ë", "edieresis.ss01"), ("ė", "edotaccent.ss01"), ("ẹ", "uni1EB9.ss01"), ("ġ", "gdotaccent.ss01"), ("i", "i.ss01"), ("ï", "idieresis.ss01"), ("ị", "uni1ECB.ss01"), ("j", "j.ss01"), ("ŀ", "ldot.ss01"), ("ộ", "uni1ED9.ss01"),
        ("ö", "odieresis.ss01"), ("ọ", "uni1ECD.ss01"), ("ợ", "uni1EE3.ss01"), ("ü", "udieresis.ss01"), ("ụ", "uni1EE5.ss01"), ("ừ", "uni1EF1.ss01"), ("ẅ", "wdieresis.ss01"), ("y", "y.ss01"), ("ý", "yacute.ss01"), ("ŷ", "ycircumflex.ss01"), ("ÿ", "ydieresis.ss01"), ("ỵ", "uni1EF5.ss01"), ("ỳ", "ygrave.ss01"), ("ż", "zdotaccent.ss01"), (".", "period.ss01"),
        (",", "comma.ss01"), (":", "colon.ss01"), (";", "semicolon.ss01"), ("…", "ellipsis.ss01"), ("!", "exclam.ss01"), ("¡", "exclamdown.ss01"), ("?", "question.ss01"), ("¿", "questiondown.ss01"), ("·", "periodcentered.ss01"), ("‚", "quotesinglbase.ss01"), ("„", "quotedblbase.ss01"), ("“", "quotedblleft.ss01"), ("”", "quotedblright.ss01"), ("‘", "quoteleft.ss01"), ("’", "quoteright.ss01"),
        ("÷", "divide.ss01"),
    ]
    ss01_alternates = stylistic_set_group("ss01", ss01_alternates)
    pages.append(
        page_shell(
            19,
            "Stylistic Alternates 01",
            """
            <div class="section-title compact-title">
              <div class="label">OpenType Alternates / ss01</div>
              <h2>Alternates - Stylistic Set 01</h2>
            </div>
            """
            + alternate_focus("a", "a", "a.ss01", ("ss01",), "ss01-focus")
            + alternate_board(ss01_alternates, ("ss01",), "ss01-board"),
            "glyph-page alternate-page",
        )
    )

    ss02_alternates = [
        ("l", "l.ss02"), ("ĺ", "lacute.ss02"), ("ľ", "lcaron.ss02"), ("ļ", "uni013C.ss02"), ("ŀ", "ldot.ss02"), ("ł", "lslash.ss02"), ("ﬂ", "fl.ss02"), ("ffl", "f_f_l.liga.ss02"),
    ]
    ss02_alternates = stylistic_set_group("ss02", ss02_alternates)
    ss03_alternates = [
        ("r", "r.ss03"), ("ŕ", "racute.ss03"), ("ř", "rcaron.ss03"), ("ŗ", "uni0157.ss03"),
    ]
    ss03_alternates = stylistic_set_group("ss03", ss03_alternates)
    ss04_alternates = [
        ("0", "zero.ss04"), ("I", "I.ss04"), ("Ĳ", "IJ.ss04"), ("Í", "Iacute.ss04"), ("Ĭ", "Ibreve.ss04"), ("Î", "Icircumflex.ss04"), ("Ï", "Idieresis.ss04"), ("İ", "Idotaccent.ss04"), ("Ị", "uni1ECA.ss04"), ("Ì", "Igrave.ss04"), ("Ỉ", "uni1EC8.ss04"), ("Ī", "Imacron.ss04"), ("Į", "Iogonek.ss04"), ("Ĩ", "Itilde.ss04"),
    ]
    ss04_alternates = stylistic_set_group("ss04", ss04_alternates)
    pages.append(
        page_shell(
            20,
            "Stylistic Alternates 02-04",
            """
            <div class="section-title compact-title">
              <div class="label">OpenType Alternates / ss02-ss04</div>
              <h2>Alternates - Stylistic Sets 02-04</h2>
            </div>
            <div class="alternate-combo">
            """
            + alternate_group("Stylistic Set 02", ss02_alternates, ("ss02",), "ss02-board")
            + alternate_group("Stylistic Set 03", ss03_alternates, ("ss03",), "ss03-board")
            + alternate_group("Stylistic Set 04", ss04_alternates, ("ss04",), "ss04-board")
            + """
            </div>
            """,
            "glyph-page alternate-page",
        )
    )

    language_samples = [
        ("French", "Énergie orbitale prête"),
        ("German", "Übergrößen für Städte"),
        ("Spanish", "Señal rápida año cero"),
        ("Portuguese", "Órbita de ação técnica"),
        ("Italian", "Sistema titolo modulare"),
        ("Dutch", "IJssel data station"),
        ("Polish", "Zażółć gęślą jaźń"),
        ("Czech", "Příliš žluťoučký kůň"),
        ("Turkish", "Çağrı yönü hazır"),
        ("Danish", "Rød blå strøm"),
        ("Swedish", "Skärgård över månen"),
        ("Norwegian", "Kjølig blå strøm"),
        ("Finnish", "Yö näkyy äärellä"),
        ("Romanian", "Știință și țară"),
        ("Hungarian", "Árvíztűrő tükörfúrógép"),
    ]
    pages.append(
        page_shell(
            21,
            "Language Coverage",
            """
            <div class="section-title compact-title">
              <div class="label">Language Coverage</div>
              <h2>Latin language samples covered by the current export.</h2>
            </div>
            <div class="language-grid">
              """
            + "\n".join(
                f"""
                <div class="language-card">
                  <div class="label">{e(language)}</div>
                  <p>{e(sample)}</p>
                </div>"""
                for language, sample in language_samples
            )
            + """
            </div>
            """,
            "language-page",
        )
    )

    categories = [
        ("Letter", 612),
        ("Symbol", 98),
        ("Number", 90),
        ("Punctuation", 78),
        ("Mark", 53),
        ("Separator", 3),
        ("Uncategorized / components", 12),
    ]
    max_value = max(value for _, value in categories)
    pages.append(
        page_shell(
            22,
            "Glyph Categories",
            """
            <div class="section-title">
              <div class="label">Glyph Category Data</div>
              <h2>947 glyphs organized by production category.</h2>
            </div>
            <div class="bar-chart">
              """
            + "\n".join(
                f"""
                <div class="bar-row">
                  <div class="label">{e(name)}</div>
                  <div class="bar-track"><span style="width:{value / max_value * 100:.2f}%"></span></div>
                  <div class="bar-value">{value}</div>
                </div>"""
                for name, value in categories
            )
            + """
            </div>
            """,
        )
    )

    pages.append(
        page_shell(
            23,
            "Technical Specifications",
            technical_specs_content(),
            "technical-page",
        )
    )

    pages.append(
        page_shell(
            24,
            "Final Technical",
            f"""
            <div class="final-grid">
              <div class="final-title">
                <div class="label">Final Technical / SIL Font</div>
                <h2>{e(current_metadata().get("family", "Square Bot Sans"))} {e(current_metadata().get("version", "v2.003"))}</h2>
              </div>
              <div class="final-table">
                <div class="final-row">
                  <div class="label">Formats</div>
                  <p>Variable TTF / Static OTF / Web WOFF2</p>
                </div>
                <div class="final-row">
                  <div class="label">License</div>
                  <p>SIL Open Font License / <a href="https://ap.cx">ap.cx</a></p>
                </div>
                <div class="final-row">
                  <div class="label">Export State</div>
                  <p>12 masters / 49 active instances / 909 exporting glyphs / OpenType features verified against the live Glyphs source.</p>
                </div>
                <div class="final-row">
                  <div class="label">Foundry</div>
                  <p>Another Planet Creative Experience</p>
                </div>
                <div class="final-row">
                  <div class="label">Contact</div>
                  <p><a href="mailto:hello@ap.cx">hello@ap.cx</a></p>
                </div>
              </div>
            </div>
            """,
            "final-page",
        )
    )

    pages.append(back_cover_shell())

    return pages
