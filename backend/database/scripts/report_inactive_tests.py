#!/usr/bin/env python3
"""
Report inactive tests and their result counts.
Run:
  python database/scripts/report_inactive_tests.py --db-password lysobacter_password
"""
import psycopg2, argparse, tabulate, sys

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--db-host', default='localhost')
    p.add_argument('--db-port', type=int, default=5434)
    p.add_argument('--db-name', default='lysobacter_db')
    p.add_argument('--db-user', default='lysobacter_user')
    p.add_argument('--db-password', required=True)
    p.add_argument('--limit', type=int, default=50)
    args=p.parse_args()

    conn=psycopg2.connect(host=args.db_host, port=args.db_port, dbname=args.db_name, user=args.db_user, password=args.db_password)
    cur=conn.cursor()
    cur.execute(f"""
        SELECT t.test_code,
               t.test_name,
               (SELECT count(*) FROM lysobacter.test_results_boolean b WHERE b.test_id=t.test_id) +
               (SELECT count(*) FROM lysobacter.test_results_numeric n WHERE n.test_id=t.test_id) +
               (SELECT count(*) FROM lysobacter.test_results_text txt WHERE txt.test_id=t.test_id) AS total_results
        FROM lysobacter.tests t
        WHERE is_active=FALSE
        ORDER BY total_results DESC
        LIMIT %s;
    """, (args.limit,))
    rows=cur.fetchall()
    print(tabulate.tabulate(rows, headers=["test_code","test_name","total_results"], tablefmt="github"))
    conn.close()

if __name__=='__main__':
    try:
        import tabulate
    except ImportError:
        print("Please pip install tabulate first (pip install tabulate)")
        sys.exit(1)
    main() 