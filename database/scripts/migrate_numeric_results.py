#!/usr/bin/env python3
"""
Migrate numeric test results to canonical tests
=============================================
Copies rows from generic 'temperature' and 'ph_level' tests into the new
canonical tests temperature_min/opt/max and ph_min/opt/max, preserving
value_type.

After migration rows in generic tests are removed.
"""

import psycopg2
import argparse
import sys

GENERIC_TO_CANONICAL = {
    "temperature": {
        "minimum": "temperature_min",
        "optimal": "temperature_opt",
        "maximum": "temperature_max",
    },
    "ph_level": {
        "minimum": "ph_min",
        "optimal": "ph_opt",
        "maximum": "ph_max",
    },
}


def get_db_conn(args):
    return psycopg2.connect(
        host=args.db_host,
        port=args.db_port,
        dbname=args.db_name,
        user=args.db_user,
        password=args.db_password,
    )


def main():
    parser = argparse.ArgumentParser(description="Migrate numeric results to canonical tests")
    parser.add_argument("--db-host", default="localhost")
    parser.add_argument("--db-port", type=int, default=5434)
    parser.add_argument("--db-name", default="lysobacter_db")
    parser.add_argument("--db-user", default="lysobacter_user")
    parser.add_argument("--db-password", required=True)
    args = parser.parse_args()

    conn = get_db_conn(args)
    conn.autocommit = False
    try:
        with conn.cursor() as cur:
            # Build mapping of test_code -> test_id
            cur.execute("SELECT test_id, test_code FROM lysobacter.tests")
            code_to_id = {row[1]: row[0] for row in cur.fetchall()}

            for generic_code, mapping in GENERIC_TO_CANONICAL.items():
                if generic_code not in code_to_id:
                    print(f"Generic test '{generic_code}' not found, skipping")
                    continue
                generic_id = code_to_id[generic_code]

                for value_type, canonical_code in mapping.items():
                    if canonical_code not in code_to_id:
                        print(f"Canonical test '{canonical_code}' missing, abort")
                        conn.rollback()
                        sys.exit(1)
                    canonical_id = code_to_id[canonical_code]
                    # Move rows
                    cur.execute(
                        """
                        UPDATE lysobacter.test_results_numeric
                        SET test_id = %s
                        WHERE test_id = %s AND value_type = %s
                        """,
                        (canonical_id, generic_id, value_type),
                    )
                    moved = cur.rowcount
                    if moved:
                        print(f"Moved {moved} rows {generic_code}:{value_type} -> {canonical_code}")

            # Delete remaining rows for generic tests (any value_type) and deactivate tests
            cur.execute(
                "DELETE FROM lysobacter.test_results_numeric WHERE test_id IN (SELECT test_id FROM lysobacter.tests WHERE test_code IN %s)",
                (tuple(GENERIC_TO_CANONICAL.keys()),),
            )
            cur.execute(
                "UPDATE lysobacter.tests SET is_active = FALSE WHERE test_code IN %s",
                (tuple(GENERIC_TO_CANONICAL.keys()),),
            )
        conn.commit()
        print("✓ Numeric results migrated successfully")
    except Exception as e:
        conn.rollback()
        print(f"✗ Migration failed: {e}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main() 