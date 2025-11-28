import sys
import traceback
from sqlalchemy import text

from shared.database import engine


def check_connection():
    try:
        with engine.connect() as conn:
            # run a simple query
            result = conn.execute(text("SELECT 1"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("OK: database reachable and returned SELECT 1")
                return 0
            else:
                print("ERROR: unexpected result from SELECT 1:", row)
                return 2
    except Exception as e:
        print("ERROR: could not connect to database:\n", file=sys.stderr)
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    rc = check_connection()
    sys.exit(rc)
