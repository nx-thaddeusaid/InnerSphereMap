#!/usr/bin/env python3
"""
Validates all JSON files in the InnerSphereMap mod pack.

Checks:
  1. Every .json file is syntactically valid
  2. No duplicate keys within a single JSON object
  3. starsystemdef_* files have required top-level fields
  4. Description.Id matches the filename stem for starsystemdef_* files
  5. Description.Id is unique across all starsystemdef files

Exit code 0 = clean, non-zero = failures found.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

REQUIRED_FIELDS: dict[str, list[str]] = {
    "starsystemdef": ["Description", "Position", "ownerID"],
    "heraldrydef":   ["Description"],
}

MOD_JSON_REQUIRED = ["Name"]

# DocsToSystemJSON is a C# converter tool, not game data — skip it entirely.
SKIP_DIRS = {"docstosystemjson"}


def _make_dup_key_hook(dup_collector: list[str]):
    def hook(pairs: list[tuple[str, object]]) -> dict:
        seen: set[str] = set()
        result: dict = {}
        for key, value in pairs:
            if key in seen:
                dup_collector.append(key)
            seen.add(key)
            result[key] = value
        return result
    return hook


def file_prefix(name: str) -> str:
    return name.split("_")[0].lower()


def check_description(data: dict, path: str, errors: list[str]) -> None:
    desc = data.get("Description")
    if not isinstance(desc, dict):
        return
    for field in ("Id", "Name"):
        if field not in desc:
            errors.append(f"{path}: Description missing '{field}'")


ERA_DIRS = {"is3025", "is3040", "is3063"}


def era_of(path: Path) -> str:
    """Return the era directory name (e.g. 'IS3025') a file belongs to, or '' if none."""
    for part in path.parts:
        if part.lower() in ERA_DIRS:
            return part
    return ""


def validate_file(
    path: Path,
    errors: list[str],
    # id_registry[era][id_val] -> list of file paths
    id_registry: dict[str, dict[str, list[str]]],
) -> None:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as e:
        errors.append(f"{path}: cannot read: {e}")
        return

    dup_keys: list[str] = []
    try:
        data = json.loads(text, object_pairs_hook=_make_dup_key_hook(dup_keys))
    except json.JSONDecodeError as e:
        errors.append(f"{path}: invalid JSON: {e}")
        return

    if dup_keys:
        errors.append(f"{path}: duplicate JSON keys: {sorted(set(dup_keys))}")

    if not isinstance(data, dict):
        return

    name = path.name.lower()

    if name == "mod.json":
        manifest_keys = {"Name", "Enabled", "Active", "DLL", "Manifest", "DependsOn"}
        if data.keys() & manifest_keys:
            for field in MOD_JSON_REQUIRED:
                if field not in data:
                    errors.append(f"{path}: mod.json missing required field '{field}'")
        return

    prefix = file_prefix(name)
    required = REQUIRED_FIELDS.get(prefix)
    if not required:
        return

    for field in required:
        if field not in data:
            errors.append(f"{path}: missing required field '{field}'")
    check_description(data, str(path), errors)

    desc = data.get("Description")
    if isinstance(desc, dict):
        id_val = desc.get("Id")
        if isinstance(id_val, str) and id_val:
            # Description.Id must match the filename stem
            stem = path.stem
            if id_val != stem:
                errors.append(f"{path}: Description.Id '{id_val}' does not match filename stem '{stem}'")
            # Register for within-era uniqueness check.
            # The same system exists in each era dir (IS3025/IS3040/IS3063) by design —
            # scope uniqueness to the era so cross-era duplicates aren't flagged.
            if prefix == "starsystemdef":
                era = era_of(path)
                id_registry[era][id_val].append(str(path))


def main() -> int:
    root = Path(__file__).parent.parent.parent
    errors: list[str] = []
    total = 0
    id_registry: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))

    for json_file in sorted(root.rglob("*.json")):
        parts_lower = [p.lower() for p in json_file.parts]
        if any(part.startswith(".") for part in json_file.parts):
            continue
        if any(skip in parts_lower for skip in SKIP_DIRS):
            continue
        total += 1
        validate_file(json_file, errors, id_registry)

    for era in sorted(id_registry):
        for id_val, paths in sorted(id_registry[era].items()):
            if len(paths) > 1:
                filenames = [Path(p).name for p in paths]
                label = f"[{era}] " if era else ""
                errors.append(
                    f"Duplicate Description.Id {label}'{id_val}' in {len(paths)} files: {filenames}"
                )

    if errors:
        print(f"FAILED — {len(errors)} error(s) across {total} files:\n")
        for err in errors:
            print(f"  {err}")
        return 1

    print(f"OK — {total} JSON files passed validation")
    return 0


if __name__ == "__main__":
    sys.exit(main())
