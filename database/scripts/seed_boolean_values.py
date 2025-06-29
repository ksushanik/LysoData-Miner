#!/usr/bin/env python3
"""Seed boolean test values for all boolean tests"""
import psycopg2, argparse, sys

VALUES = [
    ('+', 'Positive', 1),
    ('-', 'Negative', 2),
    ('+/-', 'Intermediate', 3),
    ('n.d.', 'No Data', 4),
]

def get_db_conn(args):
    return psycopg2.connect(host=args.db_host, port=args.db_port, dbname=args.db_name, user=args.db_user, password=args.db_password)

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--db-host', default='localhost')
    p.add_argument('--db-port', type=int, default=5434)
    p.add_argument('--db-name', default='lysobacter_db')
    p.add_argument('--db-user', default='lysobacter_user')
    p.add_argument('--db-password', required=True)
    args = p.parse_args()
    conn = get_db_conn(args)
    conn.autocommit=False
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT test_id FROM lysobacter.tests WHERE test_type='boolean' AND is_active=TRUE")
            boolean_tests = [row[0] for row in cur.fetchall()]
            for test_id in boolean_tests:
                for code, name, order in VALUES:
                    cur.execute(
                        """
                        INSERT INTO lysobacter.test_values (test_id,value_code,value_name,sort_order)
                        VALUES (%s,%s,%s,%s)
                        ON CONFLICT (test_id,value_code) DO NOTHING
                        """,(test_id,code,name,order))
            print(f"✓ Seeded boolean values for {len(boolean_tests)} tests")
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"✗ Seeding failed: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__=='__main__':
    main() 