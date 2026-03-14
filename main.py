import random
import sqlite3
import yaml

# Project modules
from logger import logger
from database import create_tables, DB_NAME
from experiment import assign_user, log_event, get_group_metrics
from analysis import run_ttest, run_bayesian
from report import print_report


# --------------------------------------------------
# Load experiment configuration
# --------------------------------------------------

with open("config.yaml") as f:
    config = yaml.safe_load(f)

# Experiment settings
EXPERIMENT_NAME = config["experiment"]["name"]
TOTAL_USERS     = config["experiment"]["users"]
EVENT_TYPE      = config["experiment"]["event_type"]

# Conversion assumptions for the simulation
CONTROL_CVR     = config["metrics"]["control_cvr"]
TREATMENT_CVR   = config["metrics"]["treatment_cvr"]
AVG_ORDER_VALUE = config["metrics"]["avg_order_value"]


# --------------------------------------------------
# User simulation
# --------------------------------------------------

def simulate_users():
    """
    Simulate users visiting the product and possibly converting.

    Each user:
    1. gets assigned to control or treatment
    2. converts with some probability (CVR)
    3. generates revenue if they convert
    """

    logger.info(f"Simulating {TOTAL_USERS} users...")

    for i in range(TOTAL_USERS):
        user_id = f"user_{i:04d}"

        # Assign user to an experiment group
        group = assign_user(user_id)

        # Choose conversion rate based on group
        cvr = TREATMENT_CVR if group == "treatment" else CONTROL_CVR

        # Simulate whether user converts
        if random.random() < cvr:

            # Revenue is normally distributed around AOV
            revenue = round(random.gauss(AVG_ORDER_VALUE, 10), 2)

            # Prevent negative revenue values
            log_event(user_id, EVENT_TYPE, revenue=max(0.0, revenue))

    logger.info("Simulation complete.")


# --------------------------------------------------
# Fetch user-level revenue for statistical testing
# --------------------------------------------------

def fetch_raw_revenues(group_name: str) -> list[float]:
    """
    Return revenue per user for a given group.

    The t-test requires individual observations,
    so we aggregate revenue per user here.
    """

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                a.user_id,
                COALESCE(SUM(e.revenue), 0.0) AS total_revenue
            FROM assignments a
            LEFT JOIN events e
                ON a.user_id = e.user_id AND e.event_type = ?
            WHERE a.group_name = ?
            GROUP BY a.user_id
        """, (EVENT_TYPE, group_name))

        return [row[1] for row in cursor.fetchall()]


# --------------------------------------------------
# Main experiment workflow
# --------------------------------------------------

def main():

    # Step 1 — initialize database (reset ensures clean runs)
    create_tables(reset=True)

    # Step 2 — simulate user behavior
    simulate_users()

    # Step 3 — compute summary metrics
    control   = get_group_metrics("control", EVENT_TYPE)
    treatment = get_group_metrics("treatment", EVENT_TYPE)

    # Step 4 — collect user-level revenue for t-test
    control_revenues   = fetch_raw_revenues("control")
    treatment_revenues = fetch_raw_revenues("treatment")

    # Step 5 — statistical analysis
    ttest_result = run_ttest(control_revenues, treatment_revenues)

    bayesian_result = run_bayesian(
        control_conversions   = control["converters"],
        control_total         = control["total_users"],
        treatment_conversions = treatment["converters"],
        treatment_total       = treatment["total_users"],
    )

    # Step 6 — display results
    print_report(
        EXPERIMENT_NAME,
        control,
        treatment,
        ttest_result,
        bayesian_result
    )


if __name__ == "__main__":
    main()
