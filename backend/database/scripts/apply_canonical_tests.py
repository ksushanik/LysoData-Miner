#!/usr/bin/env python3
"""
Apply Canonical Tests
====================
Reads canonical_tests.yaml and synchronises the lysobacter.tests table so that
only the approved parameters are active. Existing rows are updated / inserted
as needed. Non-canonical tests are deactivated (is_active = FALSE).

Usage:
    python apply_canonical_tests.py --db-host localhost --db-port 5434 \
        --db-name lysobacter_db --db-user lysobacter_user --db-password secret

The script is idempotent and safe to run multiple times.
"""

import yaml
import psycopg2
import psycopg2.extras
import argparse
import sys
from typing import Dict, List

CANONICAL_YAML_PATH = "database/reference/canonical_tests.yaml"

CATEGORY_ORDER = {
    "morphological": 1,
    "physiological": 2,
    "biochemical_enzymes": 3,
    "biochemical_breakdown": 4,
    "biochemical_utilization": 5,
    "other_biochemical": 6,
}


def parse_yaml(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, list):
        raise ValueError("canonical_tests.yaml must be a list at top level")
    return data


def get_db_conn(args):
    return psycopg2.connect(
        host=args.db_host,
        port=args.db_port,
        dbname=args.db_name,
        user=args.db_user,
        password=args.db_password,
    )


def ensure_categories(cur, canonical_tests: List[Dict]):
    """Insert categories if they don't exist and return mapping name->id"""
    # Unique set preserving order
    category_names = list({t["category"] for t in canonical_tests})
    mapping = {}
    for name in category_names:
        cur.execute(
            """
            INSERT INTO lysobacter.test_categories (category_name, description, sort_order)
            VALUES (%s, %s, %s)
            ON CONFLICT (category_name) DO UPDATE SET description = EXCLUDED.description
            RETURNING category_id
            """,
            (name, name.capitalize(), CATEGORY_ORDER.get(name, 0)),
        )
        mapping[name] = cur.fetchone()[0]
    return mapping


def upsert_tests(cur, canonical_tests: List[Dict], cat_map: Dict[str, int]):
    canonical_codes = []
    for test in canonical_tests:
        code = test["code"]
        canonical_codes.append(code)
        cur.execute(
            """
            INSERT INTO lysobacter.tests (
                category_id, test_name, test_code, test_type, description, measurement_unit, is_active
            ) VALUES (%s, %s, %s, %s, %s, %s, TRUE)
            ON CONFLICT (test_code) DO UPDATE SET
                category_id = EXCLUDED.category_id,
                test_name = EXCLUDED.test_name,
                test_type = EXCLUDED.test_type,
                description = EXCLUDED.description,
                measurement_unit = EXCLUDED.measurement_unit,
                is_active = TRUE
            """,
            (
                cat_map[test["category"]],
                test.get("label", test["code"].replace("_", " ").title()),
                code,
                test["type"],
                test.get("label"),
                test.get("unit"),
            ),
        )
    # Deactivate non-canonical tests
    cur.execute(
        "UPDATE lysobacter.tests SET is_active = FALSE WHERE test_code <> ALL(%s)",
        (canonical_codes,),
    )

    # Clean up results linked to inactive tests to avoid orphan data
    cur.execute(
        "DELETE FROM lysobacter.test_results_boolean WHERE test_id IN (SELECT test_id FROM lysobacter.tests WHERE is_active = FALSE)"
    )
    cur.execute(
        "DELETE FROM lysobacter.test_results_numeric WHERE test_id IN (SELECT test_id FROM lysobacter.tests WHERE is_active = FALSE)"
    )
    cur.execute(
        "DELETE FROM lysobacter.test_results_text WHERE test_id IN (SELECT test_id FROM lysobacter.tests WHERE is_active = FALSE)"
    )


def main():
    parser = argparse.ArgumentParser(description="Apply canonical test definitions to database")
    parser.add_argument("--db-host", default="localhost")
    parser.add_argument("--db-port", type=int, default=5434)
    parser.add_argument("--db-name", default="lysobacter_db")
    parser.add_argument("--db-user", default="lysobacter_user")
    parser.add_argument("--db-password", required=True)
    args = parser.parse_args()

    canonical_tests = parse_yaml(CANONICAL_YAML_PATH)
    conn = get_db_conn(args)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            cat_map = ensure_categories(cur, canonical_tests)
            upsert_tests(cur, canonical_tests, cat_map)
        conn.commit()
        print("✓ Canonical tests applied successfully")
    except Exception as e:
        conn.rollback()
        print(f"✗ Error applying canonical tests: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main() 