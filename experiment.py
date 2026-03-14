import sqlite3
import random
from database import DB_NAME


def assign_user(user_id: str) -> str:
    """
    Assign a user to either control or treatment.

    The assignment is sticky: once a user is assigned,
    they will always stay in the same group.    """

    with sqlite3.connect(DB_NAME) as conn:  # ✅ context manager
        cursor = conn.cursor()

        # Check if this user was already assigned earlier
        cursor.execute("SELECT group_name FROM assignments WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()

        # If assignment already exists, return it
        if row:
            return row[0]

        # Otherwise randomly assign the user
        group = random.choice(["control", "treatment"])
        
        cursor.execute(
            "INSERT INTO assignments (user_id, group_name) VALUES (?, ?)",
            (user_id, group)
        )
        conn.commit()
    return group


def get_daily_conversions() -> list[tuple]:
    """
    Return daily purchase counts.

    Output format:
        [(date, number_of_unique_buyers), ...]
    """
    with sqlite3.connect(DB_NAME) as conn:  # ✅ context manager
        cursor = conn.cursor()

        # Count unique users who made purchases each day
        cursor.execute("""
            SELECT DATE(created_at), COUNT(DISTINCT user_id)
            FROM events
            WHERE event_type = 'purchase'
            GROUP BY DATE(created_at)
            ORDER BY DATE(created_at)
        """)
        return cursor.fetchall()  # list of (date_str, count) tuples


def log_event(user_id: str, event_type: str, revenue: float = 0.0):
    """Record a user action (e.g. a purchase)."""
    with sqlite3.connect(DB_NAME) as conn:  # ✅ context manager
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO events (user_id, event_type, revenue) VALUES (?, ?, ?)",
            (user_id, event_type, revenue)
        )
        conn.commit()


def get_group_metrics(group_name: str, event_type: str = "purchase") -> dict:
    """
    Calculate summary metrics for a group:
    total users, converters, avg revenue, conversion rate.
    """
    with sqlite3.connect(DB_NAME) as conn:  # ✅ context manager
        cursor = conn.cursor()
        # Join assignments with events to calculate metrics
        cursor.execute("""
            SELECT
                COUNT(DISTINCT a.user_id)                        AS total_users,
                COUNT(DISTINCT e.user_id)                        AS converters,
                COALESCE(AVG(e.revenue), 0.0)                    AS avg_revenue,
                ROUND(
                    100.0 * COUNT(DISTINCT e.user_id) /
                    NULLIF(COUNT(DISTINCT a.user_id), 0), 2
                )                                                AS conversion_rate
            FROM assignments a
            LEFT JOIN events e
                ON a.user_id = e.user_id AND e.event_type = ?
            WHERE a.group_name = ?
        """, (event_type, group_name))
        row = cursor.fetchone()

    return {
        "group":           group_name,
        "total_users":     row[0],
        "converters":      row[1],
        "avg_revenue":     round(row[2], 2),
        "conversion_rate": row[3],
    }
