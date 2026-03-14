import sqlite3

DB_NAME = "ab_test.db"


def create_tables(reset: bool = False):
    """
    Create the tables needed for the A/B testing simulation.
    Reset tables if requested
    """
    with sqlite3.connect(DB_NAME) as conn:  
        cursor = conn.cursor()

        if reset:
            cursor.execute("DROP TABLE IF EXISTS events")
            cursor.execute("DROP TABLE IF EXISTS assignments")
            cursor.execute("DROP TABLE IF EXISTS variants")
            cursor.execute("DROP TABLE IF EXISTS experiments")
        #Experimental schema (for future use)
        #These tables allow running multiple experiments with variants
        # Current simulation doesn't depend on them yet

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiments (
                experiment_id   TEXT PRIMARY KEY,
                experiment_name TEXT NOT NULL,
                start_date      DATETIME,
                end_date        DATETIME,
                status          TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS variants (
                variant_id    TEXT PRIMARY KEY,
                experiment_id TEXT,
                variant_name  TEXT,
                FOREIGN KEY (experiment_id) REFERENCES experiments(experiment_id)
            )
        """)
        # ────────────────────────────────────────────────────────────────────

        # Core tables used in current simulation ─────────────────

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assignments (
                user_id     TEXT PRIMARY KEY,
                group_name  TEXT NOT NULL,
                assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Stores user actions (purchases, signups, etc.)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     TEXT NOT NULL,
                event_type  TEXT NOT NULL,
                revenue     REAL DEFAULT 0.0,
                created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()

    print("Database ready.")


if __name__ == "__main__":
    create_tables()
