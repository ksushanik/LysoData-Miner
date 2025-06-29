#!/usr/bin/env python3
"""
Batch JSON Import Script for Lysobacter Database

This utility validates and imports multiple JSON files (or a single file) using the
existing LysobacterJSONImporter class. It is a convenience wrapper so that the user
can load an entire directory of JSON files with one command instead of invoking the
importer for each file manually.

Usage examples:

    # Import every *.json file inside ./data (non-recursive)
    $ python3 batch_import_json.py --path ./data \
        --db-host localhost --db-port 5434 --db-name lysobacter_db \
        --db-user lysobacter_user --db-password lysobacter_password

    # Import JSON files matching a glob pattern
    $ python3 batch_import_json.py --path "./data/Lysobacter_*_2025*.json"

    # Validate only (no import)
    $ python3 batch_import_json.py --path ./data --validate-only
"""

from __future__ import annotations

import argparse
import glob
import os
import sys
from pathlib import Path
from typing import List

# Local import of the existing single-file importer implementation
from import_json import LysobacterJSONImporter  # type: ignore  # local import

# Standard library
import json


def discover_json_files(path: str, recursive: bool) -> List[str]:
    """Return a sorted list of JSON files for the given path/pattern."""
    p = Path(path)

    # If the path is a directory, collect *.json files inside it
    if p.is_dir():
        pattern = "**/*.json" if recursive else "*.json"
        files = sorted(str(fp) for fp in p.glob(pattern))
    else:
        # Interpret the path as a glob pattern (file or wildcard)
        files = sorted(glob.glob(path))

    return [f for f in files if f.lower().endswith(".json")]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate and import multiple JSON files into the Lysobacter database",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--path",
        required=True,
        help="Path to a JSON file, directory containing JSON files, or a glob pattern",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively search for JSON files inside directories",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate JSON structure, do not import data",
    )
    # Database connection parameters
    parser.add_argument("--db-host", default="localhost", help="Database host")
    parser.add_argument("--db-port", default="5433", help="Database port")
    parser.add_argument("--db-name", default="lysobacter_db", help="Database name")
    parser.add_argument("--db-user", default="lysobacter_user", help="Database user")
    parser.add_argument("--db-password", default="lysobacter_password", help="Database password")

    args = parser.parse_args()

    json_files = discover_json_files(args.path, args.recursive)
    if not json_files:
        print(f"✗ No JSON files found for given path/pattern: {args.path}")
        sys.exit(1)

    print("📂 Files to process:")
    for idx, jf in enumerate(json_files, 1):
        print(f"  {idx:>2}. {jf}")

    if args.validate_only:
        # For validation only we do not need DB connection (but importer.validate_json_structure
        # currently does not require DB). Still instantiate importer without DB credentials.
        importer = LysobacterJSONImporter({})
        total_valid = 0
        for file in json_files:
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                print(f"✗ {file}: error reading JSON – {e}")
                continue
            if importer.validate_json_structure(data):
                total_valid += 1
                print(f"✓ {file}: valid")
        print(f"\n✅ Validation finished – {total_valid}/{len(json_files)} files are structurally valid")
        sys.exit(0 if total_valid == len(json_files) else 2)

    # Import mode – need DB connection
    db_config = {
        "host": args.db_host,
        "port": args.db_port,
        "database": args.db_name,
        "user": args.db_user,
        "password": args.db_password,
    }

    importer = LysobacterJSONImporter(db_config)
    importer.connect()
    importer.load_test_cache()

    total_strains = 0
    total_results = 0
    processed = 0

    for file in json_files:
        print("\n==============================")
        res = importer.import_from_json(file)
        total_strains += res.get("strains", 0)
        total_results += res.get("test_results", 0)
        processed += 1

    importer.disconnect()

    print("\n📊 Batch import summary:")
    print(f"  Files processed : {processed}")
    print(f"  Strains imported: {total_strains}")
    print(f"  Test results    : {total_results}")

    print("✅ Batch import completed successfully")


if __name__ == "__main__":
    main() 