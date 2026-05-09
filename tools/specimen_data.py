from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "specimen-src"
DATA_DIR = SRC / "data"


class SpecimenDataError(RuntimeError):
    pass


def _read_yaml(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
    except yaml.YAMLError as exc:
        raise SpecimenDataError(f"Malformed YAML in {path}: {exc}") from exc
    except OSError as exc:
        raise SpecimenDataError(f"Cannot read {path}: {exc}") from exc
    if data is None:
        raise SpecimenDataError(f"Empty YAML file: {path}")
    return data


def _read_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as exc:
        raise SpecimenDataError(f"Malformed JSON in {path}: {exc}") from exc
    except OSError as exc:
        raise SpecimenDataError(f"Cannot read {path}: {exc}") from exc


def _require_mapping(data: Any, path: Path) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise SpecimenDataError(f"Expected a mapping in {path}")
    return data


def _require_keys(name: str, data: dict[str, Any], keys: list[str]) -> None:
    missing = [key for key in keys if key not in data]
    if missing:
        joined = ", ".join(missing)
        raise SpecimenDataError(f"Missing key(s) in {name}: {joined}")


def _validate_italic_positions(axes: dict[str, Any]) -> None:
    rows = axes.get("italic", {}).get("rows", [])
    if not isinstance(rows, list):
        raise SpecimenDataError("axes.yaml italic.rows must be a list")
    allowed = {0.0, 1.0}
    invalid: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            raise SpecimenDataError("axes.yaml italic.rows entries must be mappings")
        try:
            value = float(row.get("value"))
        except (TypeError, ValueError):
            invalid.append(str(row.get("value")))
            continue
        if value not in allowed:
            invalid.append(str(row.get("value")))
    if invalid:
        values = ", ".join(invalid)
        raise SpecimenDataError(f"Only italic positions 0 and 1 are allowed in axes.yaml; found: {values}")


def load_data(root: Path = ROOT) -> dict[str, Any]:
    data_dir = root / "specimen-src" / "data"
    files = {
        "metadata": data_dir / "metadata.yaml",
        "axes": data_dir / "axes.yaml",
        "features": data_dir / "features.yaml",
        "technical": data_dir / "technical.yaml",
        "pages": data_dir / "pages.yaml",
        "glyph_groups": data_dir / "glyph-groups.json",
        "instances": data_dir / "instances.json",
    }
    data: dict[str, Any] = {}
    for name, path in files.items():
        if not path.exists():
            raise SpecimenDataError(f"Missing data file: {path}")
        loaded = _read_json(path) if path.suffix == ".json" else _read_yaml(path)
        data[name] = _require_mapping(loaded, path)

    _require_keys("metadata.yaml", data["metadata"], ["family", "version", "header", "footer", "cover"])
    _require_keys("axes.yaml", data["axes"], ["width", "weight", "italic"])
    _require_keys("features.yaml", data["features"], ["groups", "comparisons", "stylistic_sets"])
    _require_keys("technical.yaml", data["technical"], ["metrics", "counts", "formats", "licensing", "languages"])
    _require_keys("pages.yaml", data["pages"], ["pages"])
    _require_keys("instances.json", data["instances"], ["weights", "widths"])
    _validate_italic_positions(data["axes"])
    return data
