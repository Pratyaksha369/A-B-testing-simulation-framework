import math
from scipy import stats
import numpy as np


def run_ttest(control_data: list[float], treatment_data: list[float]) -> dict:
    """
    Two-sample t-test.
    Answers: Is the difference between groups statistically significant?

    Returns:
        t_statistic — how many standard deviations apart the means are
        p_value     — probability this difference happened by chance
        significant — True if p < 0.05 (the standard threshold)
    """
    # Compare the two samples
    t_stat, p_value = stats.ttest_ind(control_data, treatment_data)

    # This happens if both samples have zero variance
    # NaN < 0.05 evaluates to False -> misleading result
    if math.isnan(t_stat) or math.isnan(p_value):
        return {
            "t_statistic": None,
            "p_value":     None,
            "significant": False,
            "method":      "Two-sample t-test",
            "error":       "Test could not run — insufficient variance in one or both groups.",
        }

    return {
        "t_statistic": round(float(t_stat), 4),
        "p_value":     round(float(p_value), 4),
        "significant": p_value < 0.05,
        "method":      "Two-sample t-test",
    }


def run_bayesian(control_conversions: int, control_total: int,
                 treatment_conversions: int, treatment_total: int,
                 simulations: int = 100_000) -> dict:
    """
    Bayesian A/B test using Beta distribution simulation.

    Answers: What's the probability that Treatment is better than Control?

    How it works:
      - We model each group's conversion rate as a Beta distribution
      - Beta(1 + successes, 1 + failures)
      - We draw 100,000 random samples from each and count when treatment wins
    """
    control_alpha    = 1 + control_conversions
    control_beta_p   = 1 + (control_total - control_conversions)    # ✅ renamed to avoid shadowing built-in 'beta'
    treatment_alpha  = 1 + treatment_conversions
    treatment_beta_p = 1 + (treatment_total - treatment_conversions)
 
    # Draw random samples from both distributions
    control_samples   = np.random.beta(control_alpha,   control_beta_p,   simulations)
    treatment_samples = np.random.beta(treatment_alpha, treatment_beta_p, simulations)

    # Estimate probability treatment beats control
    prob_treatment_wins = (treatment_samples > control_samples).mean()

    return {
        "prob_treatment_better": round(float(prob_treatment_wins), 4),
        "method":     "Bayesian Beta-Binomial simulation",
        "simulations": simulations,
    }
