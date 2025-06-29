#!/usr/bin/env python3
"""
convert_to_canonical_codes.py
-----------------------------
Проходит по всем *.json в указанной папке (по умолчанию ../data/),
заменяет устаревшие test_code ("temperature", "ph_level") на
канонические temperature_min/opt/max и ph_min/opt/max согласно value_type.
Файл `lysobacters.json` пропускается.

Запуск:
    python3 database/scripts/convert_to_canonical_codes.py --dir data
"""
import json
import argparse
import pathlib
import sys
from typing import Dict

TEMP_MAP = {
    "minimum": "temperature_min",
    "optimal": "temperature_opt",
    "maximum": "temperature_max",
    None: "temperature_opt"  # fallback
}
PH_MAP = {
    "minimum": "ph_min",
    "optimal": "ph_opt",
    "maximum": "ph_max",
    None: "ph_opt"
}

def convert_file(fp: pathlib.Path, dry_run: bool = False) -> Dict[str, int]:
    changed = 0
    skipped = 0
    with fp.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if "strains" not in data:
        return {"changed": 0, "skipped": 0}

    for strain in data["strains"]:
        if "test_results" not in strain:
            continue
        for test in strain["test_results"]:
            code = test.get("test_code")
            if code not in ("temperature", "ph_level"):
                continue
            val_type = (test.get("value_type") or "").lower() or None
            if code == "temperature":
                new_code = TEMP_MAP.get(val_type, TEMP_MAP[None])
            else:
                new_code = PH_MAP.get(val_type, PH_MAP[None])
            test["test_code"] = new_code
            changed += 1
    if changed and not dry_run:
        backup = fp.with_suffix(".json.bak")
        if not backup.exists():
            fp.rename(backup)
        else:
            # если .bak уже существует, не трогаем, просто перезапишем основной файл
            pass
        fp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"changed": changed, "skipped": skipped}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="data", help="Directory with JSON files")
    ap.add_argument("--dry-run", action="store_true", help="Only show stats, do not overwrite files")
    args = ap.parse_args()

    folder = pathlib.Path(args.dir)
    if not folder.exists():
        print(f"Directory {folder} not found")
        sys.exit(1)

    total_changed = 0
    for fp in folder.glob("*.json"):
        if fp.name == "lysobacters.json":
            continue
        res = convert_file(fp, dry_run=args.dry_run)
        if res["changed"]:
            print(f"{fp.name}: updated {res['changed']} entries")
            total_changed += res["changed"]
    print(f"Done. Total updated entries: {total_changed}")

if __name__ == "__main__":
    main() 