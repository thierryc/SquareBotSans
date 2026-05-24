#!/usr/bin/env python3
"""Build SquareBot Sans distribution VFs.

This script creates the two public distribution tracks used by this repo:

1. A local/GitHub VF that exposes roman and italic positions on the italic axis.
2. Google Fonts candidate VFs split into Roman and Italic files.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from shutil import copy2
import math
import shutil
import subprocess
import sys

from fontTools.otlLib.builder import buildStatTable
from fontTools.ttLib.tables._f_v_a_r import NamedInstance
from fontTools.ttLib.tables._g_l_y_f import (
    GlyphComponent,
    NON_OVERLAPPING,
    OVERLAP_COMPOUND,
    ROUND_XY_TO_GRID,
    SCALED_COMPONENT_OFFSET,
    UNSCALED_COMPONENT_OFFSET,
    USE_MY_METRICS,
)
from fontTools.misc.transform import Transform
from fontTools.ttLib import TTFont, newTable
from fontTools.varLib.hvar import add_HVAR
from fontTools.varLib.instancer import instantiateVariableFont


ROOT = Path(__file__).resolve().parents[1]
LOCAL_SOURCE_VF = ROOT / "fonts" / "variable" / "SquareBotSansVF-Regular.ttf"
LOCAL_SOURCE_WOFF2 = ROOT / "fonts" / "variable" / "SquareBotSansVF-Regular.woff2"
GF_STAGING_DIR = ROOT / "build" / "googlefonts" / "squarebotsans"

LOCAL_TTF = ROOT / "fonts" / "variable" / "SquareBotSans[ital,wdth,wght].ttf"
LOCAL_WOFF2 = ROOT / "fonts" / "variable" / "SquareBotSans[ital,wdth,wght].woff2"

GF_ROMAN_TTF = ROOT / "fonts" / "googlefonts" / "SquareBotSans[wdth,wght].ttf"
GF_ITALIC_TTF = ROOT / "fonts" / "googlefonts" / "SquareBotSans-Italic[wdth,wght].ttf"
GF_STAGING_ROMAN_TTF = GF_STAGING_DIR / GF_ROMAN_TTF.name
GF_STAGING_ITALIC_TTF = GF_STAGING_DIR / GF_ITALIC_TTF.name

VERSION = "2.008"
FAMILY = "Square Bot Sans"
LOCAL_FAMILY = FAMILY
GF_FAMILY = FAMILY
PS_FAMILY = "SquareBotSans"
COPYRIGHT = "Copyright 2024 The Square Bot Sans Project Authors (https://github.com/thierryc/SquareBotSans)"
LICENSE = (
    "This Font Software is licensed under the SIL Open Font License, "
    "Version 1.1. This license is available with a FAQ at: "
    "https://openfontlicense.org"
)

LOCAL_WIDTH_VALUES = [
    (80, "Condensed", 0),
    (100, "Normal", 0x2),
    (120, "Expanded", 0),
]
GF_WIDTH_RANGE = (75, 100, 125)
GF_WIDTH_VALUES = [(100, "Normal", 0x2)]
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
GF_SUPPORT_FILES = [
    ROOT / "fonts" / "googlefonts" / "METADATA.pb",
    ROOT / "fonts" / "googlefonts" / "OFL.txt",
    ROOT / "fonts" / "googlefonts" / "upstream.yaml",
]
GF_SUPPORT_DIRS = [
    ROOT / "fonts" / "googlefonts" / "article",
]


def _tool(name: str) -> str:
    sibling = Path(sys.executable).with_name(name)
    if sibling.exists():
        return str(sibling)
    resolved = shutil.which(name)
    if resolved:
        return resolved
    raise SystemExit(f"Required tool not found: {name}")


def _run(args: list[str]) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


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
        ('with Reserved Font Name "Hubot Sans"', ""),
    ]
    for record in name.names:
        text = record.toUnicode().strip()
        for old, new in replacements:
            text = text.replace(old, new)
        record.string = text.encode(record.getEncoding())


def _set_name(font: TTFont, name_id: int, value: str) -> None:
    name = font["name"]
    name.setName(value, name_id, 3, 1, 0x409)


def _set_head_version(font: TTFont) -> None:
    if "head" in font:
        font["head"].fontRevision = float(VERSION)


def _add_name(font: TTFont, value: str) -> int:
    return font["name"].addMultilingualName({"en": value}, windows=True, mac=False)


def _drop_mac_name_records(font: TTFont) -> None:
    font["name"].names = [record for record in font["name"].names if record.platformID != 1]


def _drop_name_ids(font: TTFont, name_ids: set[int]) -> None:
    font["name"].names = [record for record in font["name"].names if record.nameID not in name_ids]


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


def _ensure_identity_avar(font: TTFont) -> None:
    if "fvar" not in font:
        return
    if "avar" not in font:
        font["avar"] = newTable("avar")
    font["avar"].segments = {
        axis.axisTag: {-1.0: -1.0, 0.0: 0.0, 1.0: 1.0}
        for axis in font["fvar"].axes
    }


def _set_meta_script_lang_tags(font: TTFont) -> None:
    meta = newTable("meta")
    meta.data = {
        "dlng": "Latn",
        "slng": "Latn",
    }
    font["meta"] = meta


def _set_basic_names(
    font: TTFont,
    style: str,
    postscript_suffix: str,
    *,
    family: str = LOCAL_FAMILY,
) -> None:
    full_name = f"{family} {style}"
    ps_name = f"{PS_FAMILY}-{postscript_suffix}"

    _set_name(font, 0, COPYRIGHT)
    _set_head_version(font)
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
    _set_name(font, 25, PS_FAMILY if style == "Regular" else f"{PS_FAMILY}{style}")


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


def _set_italic_caret_slope(font: TTFont, italic: bool) -> None:
    if "hhea" not in font or "head" not in font:
        return
    if not italic:
        font["hhea"].caretSlopeRise = 1
        font["hhea"].caretSlopeRun = 0
        return
    angle = -1 * font["post"].italicAngle if "post" in font else 12
    font["hhea"].caretSlopeRise = font["head"].unitsPerEm
    font["hhea"].caretSlopeRun = round(math.tan(math.radians(angle)) * font["head"].unitsPerEm)


def _set_gasp(font: TTFont) -> None:
    gasp = newTable("gasp")
    gasp.gaspRange = {65535: 0x000F}
    font["gasp"] = gasp


def _stat_axes(
    include_italic_axis: bool,
    italic_value: int | None,
    *,
    width_values: list[tuple[int, str, int]],
) -> list[dict]:
    axes: list[dict] = [
        {
            "tag": "wdth",
            "name": "Width",
            "ordering": 0,
            "values": [
                {"value": value, "name": name, "flags": flags}
                for value, name, flags in width_values
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


def _rebuild_stat(
    font: TTFont,
    include_italic_axis: bool,
    italic_value: int | None,
    *,
    width_values: list[tuple[int, str, int]],
) -> None:
    if "STAT" in font:
        del font["STAT"]
    buildStatTable(
        font,
        _stat_axes(include_italic_axis, italic_value, width_values=width_values),
        macNames=False,
    )


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
            match = NamedInstance()
            match.flags = 0
        style_name = "Italic" if italic and weight == 400 else f"{name} Italic" if italic else name
        match.subfamilyNameID = _add_name(font, style_name)
        match.postscriptNameID = 0xFFFF
        match.coordinates = {"wdth": 100.0, "wght": float(weight)}
        instances.append(match)
    font["fvar"].instances = instances


def _normalize_gf_width_axis(font: TTFont) -> None:
    if "fvar" not in font:
        return
    for axis in font["fvar"].axes:
        if axis.axisTag == "wdth":
            axis.minValue, axis.defaultValue, axis.maxValue = GF_WIDTH_RANGE


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


def _component_from_transform(
    glyph_name: str,
    transform: Transform,
    flags: int,
) -> GlyphComponent:
    xx, xy, yx, yy, dx, dy = transform
    component = GlyphComponent()
    component.glyphName = glyph_name
    component.x = round(dx)
    component.y = round(dy)
    component.flags = flags & (
        ROUND_XY_TO_GRID
        | USE_MY_METRICS
        | SCALED_COMPONENT_OFFSET
        | UNSCALED_COMPONENT_OFFSET
        | OVERLAP_COMPOUND
        | NON_OVERLAPPING
    )
    if (round(xx, 10), round(xy, 10), round(yx, 10), round(yy, 10)) != (1, 0, 0, 1):
        component.transform = [[xx, xy], [yx, yy]]
    return component


def _flatten_nested_components(font: TTFont) -> None:
    """Flatten composite references whose components are also composites.

    Google Fonts rejects nested TrueType composites. Rewriting those references
    changes the composite point model, so any glyph-level gvar deltas for the
    rewritten composites must be dropped; their child components still carry the
    outline interpolation.
    """

    if "glyf" not in font:
        return

    glyf = font["glyf"]
    changed: list[str] = []

    def flatten_component(
        component,
        parent_transform: Transform = Transform(),
        inherited_flags: int = 0,
    ) -> list[GlyphComponent]:
        child_name, child_transform = component.getComponentInfo()
        combined_transform = parent_transform.transform(child_transform)
        child = glyf[child_name]
        if not child.isComposite():
            return [
                _component_from_transform(
                    child_name,
                    combined_transform,
                    component.flags | inherited_flags,
                )
            ]

        flattened: list[GlyphComponent] = []
        for index, child_component in enumerate(child.components):
            flags = inherited_flags
            if index == 0 and component.flags & USE_MY_METRICS:
                flags |= USE_MY_METRICS
            flattened.extend(flatten_component(child_component, combined_transform, flags))
        return flattened

    for glyph_name in font.getGlyphOrder():
        glyph = glyf[glyph_name]
        if not glyph.isComposite():
            continue
        if not any(glyf[c.glyphName].isComposite() for c in glyph.components if c.glyphName in glyf.glyphs):
            continue
        glyph.components = [
            flattened
            for component in glyph.components
            for flattened in flatten_component(component)
        ]
        changed.append(glyph_name)

    if "gvar" in font:
        for glyph_name in changed:
            font["gvar"].variations[glyph_name] = []
    if "maxp" in font and changed:
        font["maxp"].maxComponentDepth = 1


def _drop_unreadable_gvar_entries(font: TTFont) -> None:
    if "gvar" not in font:
        return
    gvar = font["gvar"]
    for glyph_name in font.getGlyphOrder():
        try:
            gvar.variations.get(glyph_name)
        except Exception:
            gvar.variations[glyph_name] = []


def _add_hvar(font: TTFont) -> None:
    if "fvar" not in font or "gvar" not in font:
        return
    add_HVAR(font)


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


def _prepare_font(
    font: TTFont,
    style: str,
    postscript_suffix: str,
    *,
    italic: bool,
    family: str = LOCAL_FAMILY,
    flatten_nested_components: bool = False,
) -> None:
    _normalize_avar(font)
    _ensure_identity_avar(font)
    _dedupe_composite_components(font)
    _drop_unreadable_gvar_entries(font)
    _strip_reserved_names(font)
    _set_basic_names(font, style, postscript_suffix, family=family)
    _set_axis_names(font)
    _set_style_bits(font, italic)
    _set_italic_caret_slope(font, italic)
    _set_gasp(font)
    if flatten_nested_components:
        _flatten_nested_components(font)
    _add_hvar(font)
    _drop_mac_name_records(font)


def _prepare_google_font(font: TTFont, style: str, postscript_suffix: str, *, italic: bool) -> None:
    _prepare_font(
        font,
        style,
        postscript_suffix,
        italic=italic,
        family=GF_FAMILY,
        flatten_nested_components=True,
    )
    _set_meta_script_lang_tags(font)
    _normalize_gf_width_axis(font)
    _drop_name_ids(font, {16, 17})


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


def _expand_glyf_bounds(path: Path) -> None:
    font = TTFont(path, recalcBBoxes=False)
    if "glyf" not in font:
        return
    glyf = font["glyf"]
    changed = False
    font_x_min = font_y_min = math.inf
    font_x_max = font_y_max = -math.inf

    for glyph_name in font.getGlyphOrder():
        glyph = glyf[glyph_name]
        if glyph.numberOfContours == 0 and not glyph.isComposite():
            continue
        coords, _, _ = glyph.getCoordinates(glyf)
        if not coords:
            continue
        xs = [point[0] for point in coords]
        ys = [point[1] for point in coords]
        x_min = math.floor(min(xs))
        y_min = math.floor(min(ys))
        x_max = math.ceil(max(xs))
        y_max = math.ceil(max(ys))
        font_x_min = min(font_x_min, x_min)
        font_y_min = min(font_y_min, y_min)
        font_x_max = max(font_x_max, x_max)
        font_y_max = max(font_y_max, y_max)
        if (glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax) != (x_min, y_min, x_max, y_max):
            glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax = x_min, y_min, x_max, y_max
            changed = True

    if "head" in font and font_x_min != math.inf:
        head = font["head"]
        head_bounds = (font_x_min, font_y_min, font_x_max, font_y_max)
        if (head.xMin, head.yMin, head.xMax, head.yMax) != head_bounds:
            head.xMin, head.yMin, head.xMax, head.yMax = head_bounds
            changed = True

    if changed:
        font.recalcBBoxes = False
        font.save(path, reorderTables=False)


def _fix_nonhinting(path: Path) -> None:
    tmp_path = path.with_suffix(".nonhinting.ttf")
    _run([_tool("gftools"), "fix-nonhinting", "--no-backup", "-q", str(path), str(tmp_path)])
    tmp_path.replace(path)
    _sanitize_saved_gvar(path)
    _expand_glyf_bounds(path)


def _save_woff2(ttf_path: Path, woff2_path: Path) -> None:
    font = TTFont(ttf_path)
    font.flavor = "woff2"
    font.save(woff2_path)


def _local_source_font() -> TTFont:
    font = TTFont(LOCAL_SOURCE_VF)
    _clean_gdef_varstore(font)
    if "avar" in font:
        del font["avar"]
    return font


def _gf_source_font() -> TTFont:
    # Use the Glyphs-exported source VF for both distribution tracks so the
    # Google Fonts split keeps the same outline deltas as the local VF.
    return _local_source_font()


def normalize_source_exports() -> None:
    font = TTFont(LOCAL_SOURCE_VF)
    _ensure_identity_avar(font)
    font.save(LOCAL_SOURCE_VF)
    _save_woff2(LOCAL_SOURCE_VF, LOCAL_SOURCE_WOFF2)


def build_local() -> None:
    font = instantiateVariableFont(_local_source_font(), {"wdth": (80, 100, 120)}, inplace=False)
    _prepare_font(font, "Regular", "Regular", italic=False)
    _rename_local_instances(font)
    _rebuild_stat(
        font,
        include_italic_axis=True,
        italic_value=None,
        width_values=LOCAL_WIDTH_VALUES,
    )
    _save_ttf(font, LOCAL_TTF)
    _save_woff2(LOCAL_TTF, LOCAL_WOFF2)


def build_googlefonts() -> None:
    roman = instantiateVariableFont(
        _gf_source_font(), {"ital": 0, "wdth": GF_WIDTH_RANGE}, inplace=False
    )
    _prepare_google_font(roman, "Regular", "Regular", italic=False)
    _filter_gf_instances(roman, italic=False)
    _rebuild_stat(
        roman,
        include_italic_axis=True,
        italic_value=0,
        width_values=GF_WIDTH_VALUES,
    )
    _save_ttf(roman, GF_ROMAN_TTF)
    _fix_nonhinting(GF_ROMAN_TTF)

    italic = instantiateVariableFont(
        _gf_source_font(), {"ital": 12, "wdth": GF_WIDTH_RANGE}, inplace=False
    )
    _prepare_google_font(italic, "Italic", "Italic", italic=True)
    _filter_gf_instances(italic, italic=True)
    _rebuild_stat(
        italic,
        include_italic_axis=True,
        italic_value=1,
        width_values=GF_WIDTH_VALUES,
    )
    _save_ttf(italic, GF_ITALIC_TTF)
    _fix_nonhinting(GF_ITALIC_TTF)

    stage_googlefonts()


def stage_googlefonts() -> None:
    if GF_STAGING_DIR.exists():
        shutil.rmtree(GF_STAGING_DIR)
    GF_STAGING_DIR.mkdir(parents=True, exist_ok=True)
    copy2(GF_ROMAN_TTF, GF_STAGING_ROMAN_TTF)
    copy2(GF_ITALIC_TTF, GF_STAGING_ITALIC_TTF)
    for support_file in GF_SUPPORT_FILES:
        if support_file.exists():
            copy2(support_file, GF_STAGING_DIR / support_file.name)
    for support_dir in GF_SUPPORT_DIRS:
        if support_dir.exists():
            target = GF_STAGING_DIR / support_dir.name
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(support_dir, target)


def main() -> None:
    if not LOCAL_SOURCE_VF.exists():
        raise SystemExit(f"Local source VF not found: {LOCAL_SOURCE_VF}")
    normalize_source_exports()
    build_local()
    build_googlefonts()
    print(f"Built {LOCAL_TTF.relative_to(ROOT)}")
    print(f"Built {LOCAL_WOFF2.relative_to(ROOT)}")
    print(f"Built {GF_ROMAN_TTF.relative_to(ROOT)}")
    print(f"Built {GF_ITALIC_TTF.relative_to(ROOT)}")
    print(f"Staged Google Fonts QA files in {GF_STAGING_DIR.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
