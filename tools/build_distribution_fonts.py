#!/usr/bin/env python3
"""Build SquareBot Sans distribution VFs from the current source export.

This script creates the two public distribution tracks used by this repo:

1. A local/GitHub VF that keeps the continuous italic axis.
2. Google Fonts candidate VFs split into Roman and Italic files.

The current implementation starts from the checked-in Glyphs export at
fonts/variable/SquareBotSansVF-Regular.ttf. The long-term Google Fonts path is
to build from sources/config.yaml with gftools builder after the Glyphs source
has been split/exported for Roman and Italic production sources.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from fontTools.otlLib.builder import buildStatTable
from fontTools.ttLib import TTFont, newTable
from fontTools.varLib.instancer import instantiateVariableFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE_VF = ROOT / "fonts" / "variable" / "SquareBotSansVF-Regular.ttf"

LOCAL_TTF = ROOT / "fonts" / "variable" / "SquareBotSans[ital,wdth,wght].ttf"
LOCAL_WOFF2 = ROOT / "fonts" / "variable" / "SquareBotSans[ital,wdth,wght].woff2"

GF_ROMAN_TTF = ROOT / "fonts" / "googlefonts" / "SquareBotSans[wdth,wght].ttf"
GF_ITALIC_TTF = ROOT / "fonts" / "googlefonts" / "SquareBotSans-Italic[wdth,wght].ttf"

VERSION = "2.000"
COPYRIGHT = "Copyright 2024 The SquareBot Sans Project Authors (https://github.com/thierryc/SquareBotSans)"
LICENSE = (
    "This Font Software is licensed under the SIL Open Font License, "
    "Version 1.1. This license is available with a FAQ at: "
    "https://openfontlicense.org"
)

WIDTH_VALUES = [
    (80, "Condensed", 0),
    (100, "Normal", 0x2),
    (120, "Expanded", 0),
]
WEIGHT_VALUES = [
    (200, "ExtraLight"),
    (300, "Light"),
    (400, "Regular"),
    (500, "Medium"),
    (600, "SemiBold"),
    (700, "Bold"),
    (800, "ExtraBold"),
    (900, "Black"),
]


def _clean_gdef_varstore(font: TTFont) -> None:
    """Remove the broken GDEF VarStore from the current export.

    The current preview VF has a malformed GDEF VarStore that prevents
    fontTools.varLib.instancer from creating partial variable fonts. Keeping
    the base GDEF table and lowering it to version 1.2 preserves non-variable
    GDEF data while removing the invalid variation store.
    """

    if "GDEF" not in font:
        return
    table = font["GDEF"].table
    if hasattr(table, "VarStore"):
        table.VarStore = None
        table.Version = 0x00010002


def _strip_reserved_names(font: TTFont) -> None:
    name = font["name"]
    replacements = [
        (', with Reserved Font Name "Hubot Sans"', ""),
        (', with Reserved Font Names "SquareBot Sans" and "SquareBot Sans VF"', ""),
        ('with Reserved Font Name "Hubot Sans"', ""),
        ('with Reserved Font Names "SquareBot Sans" and "SquareBot Sans VF"', ""),
    ]
    for record in name.names:
        text = record.toUnicode().strip()
        for old, new in replacements:
            text = text.replace(old, new)
        record.string = text.encode(record.getEncoding())


def _set_name(font: TTFont, name_id: int, value: str) -> None:
    name = font["name"]
    name.setName(value, name_id, 3, 1, 0x409)


def _add_name(font: TTFont, value: str) -> int:
    return font["name"].addMultilingualName({"en": value}, windows=True, mac=False)


def _drop_mac_name_records(font: TTFont) -> None:
    font["name"].names = [record for record in font["name"].names if record.platformID != 1]


def _set_axis_names(font: TTFont) -> None:
    labels = {"wdth": "Width", "wght": "Weight", "ital": "Italic"}
    if "fvar" not in font:
        return
    for axis in font["fvar"].axes:
        axis.axisNameID = _add_name(font, labels.get(axis.axisTag, axis.axisTag))


def _normalize_avar(font: TTFont) -> None:
    if "avar" not in font or "fvar" not in font:
        return
    axis_tags = [axis.axisTag for axis in font["fvar"].axes]
    segments = font["avar"].segments
    for tag in list(segments):
        if tag not in axis_tags:
            del segments[tag]
    for tag in axis_tags:
        mapping = segments.get(tag) or {}
        mapping.setdefault(-1.0, -1.0)
        mapping.setdefault(0.0, 0.0)
        mapping.setdefault(1.0, 1.0)
        segments[tag] = dict(sorted(mapping.items()))


def _set_basic_names(font: TTFont, style: str, postscript_suffix: str) -> None:
    family = "SquareBot Sans"
    full_name = f"{family} {style}"
    ps_name = f"SquareBotSans-{postscript_suffix}"

    _set_name(font, 0, COPYRIGHT)
    _set_name(font, 1, family)
    _set_name(font, 2, style)
    _set_name(font, 3, f"{VERSION};APCX;{ps_name}")
    _set_name(font, 4, full_name)
    _set_name(font, 5, f"Version {VERSION}")
    _set_name(font, 6, ps_name)
    _set_name(font, 8, "ap.cx")
    _set_name(font, 9, "Thierry Charbonnel")
    _set_name(font, 11, "https://ap.cx")
    _set_name(font, 13, LICENSE)
    _set_name(font, 14, "https://openfontlicense.org")
    _set_name(font, 16, family)
    _set_name(font, 17, style)
    _set_name(font, 25, "SquareBotSans" if style == "Regular" else f"SquareBotSans{style}")


def _set_style_bits(font: TTFont, italic: bool) -> None:
    if "head" in font:
        if italic:
            font["head"].macStyle |= 0x2
        else:
            font["head"].macStyle &= ~0x2
    if "OS/2" in font:
        if italic:
            font["OS/2"].fsSelection |= 0x1
            font["OS/2"].fsSelection &= ~0x40
        else:
            font["OS/2"].fsSelection &= ~0x1
            font["OS/2"].fsSelection |= 0x40
    if "post" in font:
        font["post"].italicAngle = -12 if italic else 0


def _set_gasp(font: TTFont) -> None:
    gasp = newTable("gasp")
    gasp.gaspRange = {65535: 0x000F}
    font["gasp"] = gasp


def _stat_axes(include_italic_axis: bool, italic_value: int | None) -> list[dict]:
    axes: list[dict] = [
        {
            "tag": "wdth",
            "name": "Width",
            "ordering": 0,
            "values": [
                {"value": value, "name": name, "flags": flags}
                for value, name, flags in WIDTH_VALUES
            ],
        },
        {
            "tag": "wght",
            "name": "Weight",
            "ordering": 1,
            "values": [
                {"value": 200, "name": "ExtraLight"},
                {"value": 300, "name": "Light"},
                {"value": 400, "name": "Regular", "flags": 0x2, "linkedValue": 700},
                {"value": 500, "name": "Medium"},
                {"value": 600, "name": "SemiBold"},
                {"value": 700, "name": "Bold"},
                {"value": 800, "name": "ExtraBold"},
                {"value": 900, "name": "Black"},
            ],
        },
    ]

    if include_italic_axis:
        values = []
        if italic_value in (None, 0):
            values.append({"value": 0, "name": "Roman", "flags": 0x2, "linkedValue": 1})
        if italic_value in (None, 1):
            values.append({"value": 1, "name": "Italic"})
        axes.append({"tag": "ital", "name": "Italic", "ordering": 2, "values": values})

    return axes


def _rebuild_stat(font: TTFont, include_italic_axis: bool, italic_value: int | None) -> None:
    if "STAT" in font:
        del font["STAT"]
    buildStatTable(font, _stat_axes(include_italic_axis, italic_value), macNames=False)


def _filter_gf_instances(font: TTFont, italic: bool) -> None:
    if "fvar" not in font:
        return
    instances = []
    for weight, name in WEIGHT_VALUES:
        match = None
        for instance in font["fvar"].instances:
            coords = instance.coordinates
            if abs(float(coords.get("wdth", 100)) - 100) < 0.01 and abs(float(coords.get("wght", 0)) - weight) < 0.01:
                match = deepcopy(instance)
                break
        if match is None:
            continue
        style_name = "Italic" if italic and weight == 400 else f"{name} Italic" if italic else name
        match.subfamilyNameID = _add_name(font, style_name)
        match.postscriptNameID = 0xFFFF
        match.coordinates = {"wdth": 100, "wght": weight}
        instances.append(match)
    font["fvar"].instances = instances


def _dedupe_composite_components(font: TTFont) -> None:
    if "glyf" not in font:
        return
    for glyph in font["glyf"].glyphs.values():
        if not glyph.isComposite():
            continue
        components = []
        seen = set()
        changed = False
        for component in glyph.components:
            key = component.getComponentInfo()
            if key in seen:
                changed = True
                continue
            seen.add(key)
            components.append(component)
        if changed:
            glyph.components = components


def _drop_unreadable_gvar_entries(font: TTFont) -> None:
    if "gvar" not in font:
        return
    gvar = font["gvar"]
    for glyph_name in font.getGlyphOrder():
        try:
            gvar.variations.get(glyph_name)
        except Exception:
            gvar.variations[glyph_name] = []


def _local_instance_name(coords: dict) -> str:
    weight = int(round(float(coords.get("wght", 400))))
    width = int(round(float(coords.get("wdth", 100))))
    italic = int(round(float(coords.get("ital", 0))))
    weight_name = dict(WEIGHT_VALUES).get(weight, str(weight))
    width_prefix = {80: "Condensed", 100: "", 120: "Expanded"}.get(width, str(width))

    if italic:
        style = "Italic" if weight == 400 else f"{weight_name} Italic"
    else:
        style = weight_name

    return f"{width_prefix} {style}".strip()


def _rename_local_instances(font: TTFont) -> None:
    if "fvar" not in font:
        return
    for instance in font["fvar"].instances:
        instance.subfamilyNameID = _add_name(font, _local_instance_name(instance.coordinates))
        instance.postscriptNameID = 0xFFFF


def _prepare_font(font: TTFont, style: str, postscript_suffix: str, *, italic: bool) -> None:
    _normalize_avar(font)
    _dedupe_composite_components(font)
    _drop_unreadable_gvar_entries(font)
    _strip_reserved_names(font)
    _set_basic_names(font, style, postscript_suffix)
    _set_axis_names(font)
    _set_style_bits(font, italic)
    _set_gasp(font)
    _drop_mac_name_records(font)


def _save_ttf(font: TTFont, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    font.save(path)
    _sanitize_saved_gvar(path)


def _sanitize_saved_gvar(path: Path) -> None:
    font = TTFont(path)
    if "gvar" not in font:
        return
    changed = False
    gvar = font["gvar"]
    for glyph_name in font.getGlyphOrder():
        try:
            gvar.variations.get(glyph_name)
        except Exception:
            gvar.variations[glyph_name] = []
            changed = True
    if changed:
        font.save(path)


def _save_woff2(ttf_path: Path, woff2_path: Path) -> None:
    font = TTFont(ttf_path)
    font.flavor = "woff2"
    font.save(woff2_path)


def _source_font() -> TTFont:
    font = TTFont(SOURCE_VF)
    _clean_gdef_varstore(font)
    if "avar" in font:
        del font["avar"]
    return font


def build_local() -> None:
    font = instantiateVariableFont(_source_font(), {"wdth": (80, 100, 120)}, inplace=False)
    _prepare_font(font, "Regular", "Regular", italic=False)
    _rename_local_instances(font)
    _rebuild_stat(font, include_italic_axis=True, italic_value=None)
    _save_ttf(font, LOCAL_TTF)
    _save_woff2(LOCAL_TTF, LOCAL_WOFF2)


def build_googlefonts() -> None:
    roman = instantiateVariableFont(
        _source_font(), {"ital": 0, "wdth": (80, 100, 120)}, inplace=False
    )
    _prepare_font(roman, "Regular", "Regular", italic=False)
    _filter_gf_instances(roman, italic=False)
    _rebuild_stat(roman, include_italic_axis=True, italic_value=0)
    _save_ttf(roman, GF_ROMAN_TTF)

    italic = instantiateVariableFont(
        _source_font(), {"ital": 1, "wdth": (80, 100, 120)}, inplace=False
    )
    _prepare_font(italic, "Italic", "Italic", italic=True)
    _filter_gf_instances(italic, italic=True)
    _rebuild_stat(italic, include_italic_axis=True, italic_value=1)
    _save_ttf(italic, GF_ITALIC_TTF)


def main() -> None:
    if not SOURCE_VF.exists():
        raise SystemExit(f"Source VF not found: {SOURCE_VF}")
    build_local()
    build_googlefonts()
    print(f"Built {LOCAL_TTF.relative_to(ROOT)}")
    print(f"Built {LOCAL_WOFF2.relative_to(ROOT)}")
    print(f"Built {GF_ROMAN_TTF.relative_to(ROOT)}")
    print(f"Built {GF_ITALIC_TTF.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
