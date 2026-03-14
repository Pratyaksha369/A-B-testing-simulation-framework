import sqlite3
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from database import DB_NAME


COLORS = {"control": "#4C72B0", "treatment": "#DD8452"}
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor":   "#F7F7F7",
    "axes.grid":        True,
    "grid.color":       "white",
    "grid.linewidth":   1.2,
    "font.family":      "sans-serif",
})



def fetch_metrics(event_type: str = "purchase") -> dict:
    """Pull summary metrics for both groups from the DB."""
    results = {}
    for group in ("control", "treatment"):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    COUNT(DISTINCT a.user_id)   AS total_users,
                    COUNT(DISTINCT e.user_id)   AS converters,
                    COALESCE(AVG(e.revenue), 0) AS avg_revenue,
                    ROUND(100.0 * COUNT(DISTINCT e.user_id) /
                          NULLIF(COUNT(DISTINCT a.user_id), 0), 2) AS cvr
                FROM assignments a
                LEFT JOIN events e
                    ON a.user_id = e.user_id AND e.event_type = ?
                WHERE a.group_name = ?
            """, (event_type, group))
            row = cursor.fetchone()
        results[group] = {
            "total_users": row[0],
            "converters":  row[1],
            "avg_revenue": row[2],
            "cvr":         row[3] or 0.0,
        }
    return results


def fetch_revenue_distributions(event_type: str = "purchase") -> dict:
    """Fetch per-user revenue (0 for non-converters) for both groups."""
    result = {}
    for group in ("control", "treatment"):
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COALESCE(SUM(e.revenue), 0.0)
                FROM assignments a
                LEFT JOIN events e
                    ON a.user_id = e.user_id AND e.event_type = ?
                WHERE a.group_name = ?
                GROUP BY a.user_id
            """, (event_type, group))
            result[group] = [row[0] for row in cursor.fetchall()]
    return result


def fetch_bayesian_samples(metrics: dict, simulations: int = 100_000) -> dict:
    """Draw Beta distribution samples for the Bayesian credible interval plot."""
    samples = {}
    for group, m in metrics.items():
        alpha = 1 + m["converters"]
        beta  = 1 + (m["total_users"] - m["converters"])
        samples[group] = np.random.beta(alpha, beta, simulations)
    return samples


#Chart 1: Conversion Rate Bar Chart
def plot_conversion_rate(metrics: dict, ax: plt.Axes):
    groups = list(metrics.keys())
    cvrs   = [metrics[g]["cvr"] for g in groups]
    colors = [COLORS[g] for g in groups]

    bars = ax.bar(groups, cvrs, color=colors, width=0.4, edgecolor="white", linewidth=1.5)

    for bar, val in zip(bars, cvrs):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                f"{val:.2f}%", ha="center", va="bottom", fontweight="bold", fontsize=11)

    # Lift annotation
    ctrl, treat = cvrs
    if ctrl > 0:
        lift = (treat - ctrl) / ctrl * 100
        color = "#2ecc71" if lift >= 0 else "#e74c3c"
        ax.annotate(f"Lift: {lift:+.1f}%", xy=(1, treat), xytext=(0.5, max(cvrs) * 1.15),
                    fontsize=10, color=color, fontweight="bold", ha="center",
                    arrowprops=dict(arrowstyle="->", color=color, lw=1.5))

    ax.set_title("Conversion Rate by Group", fontsize=13, fontweight="bold", pad=12)
    ax.set_ylabel("Conversion Rate (%)")
    ax.set_ylim(0, max(cvrs) * 1.4)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Control", "Treatment"], fontsize=11)


# Chart 2: Revenue Distribution Histogram 
def plot_revenue_distribution(distributions: dict, ax: plt.Axes):
    for group, values in distributions.items():
        # Only plot users who actually converted (revenue > 0)
        converted = [v for v in values if v > 0]
        ax.hist(converted, bins=30, color=COLORS[group], alpha=0.6,
                label=f"{group.capitalize()} (n={len(converted)})", edgecolor="white")
        if converted:
            mean_val = np.mean(converted)
            ax.axvline(mean_val, color=COLORS[group], linestyle="--", linewidth=1.8)
            ax.text(mean_val + 0.5, ax.get_ylim()[1] * 0.85,
                    f"μ={mean_val:.1f}", color=COLORS[group], fontsize=9)

    ax.set_title("Revenue Distribution (Converters Only)", fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel("Revenue per User ($)")
    ax.set_ylabel("Number of Users")
    ax.legend(framealpha=0.9)


# Chart 3: Group Size & Conversions Stacked Bar 
def plot_funnel(metrics: dict, ax: plt.Axes):
    groups     = list(metrics.keys())
    totals     = [metrics[g]["total_users"] for g in groups]
    converters = [metrics[g]["converters"]  for g in groups]
    non_conv   = [t - c for t, c in zip(totals, converters)]

    x = np.arange(len(groups))
    ax.bar(x, non_conv,   color=[COLORS[g] for g in groups], alpha=0.3, label="Did not convert")
    ax.bar(x, converters, color=[COLORS[g] for g in groups], alpha=1.0, label="Converted",
           bottom=non_conv)

    for i, (total, conv) in enumerate(zip(totals, converters)):
        ax.text(i, total + 5, f"{conv}/{total}", ha="center", fontsize=10, fontweight="bold")

    ax.set_title("Users vs Conversions by Group", fontsize=13, fontweight="bold", pad=12)
    ax.set_ylabel("Number of Users")
    ax.set_xticks(x)
    ax.set_xticklabels(["Control", "Treatment"], fontsize=11)
    ax.legend(framealpha=0.9)


# Chart 4: Bayesian Posterior Distributions 
def plot_bayesian_posteriors(samples: dict, ax: plt.Axes):
    for group, samps in samples.items():
        ax.hist(samps, bins=80, color=COLORS[group], alpha=0.55,
                label=group.capitalize(), density=True, edgecolor="white")
        mean_val = samps.mean()
        ax.axvline(mean_val, color=COLORS[group], linestyle="--", linewidth=1.8)
        ax.text(mean_val, ax.get_ylim()[1] * 0.6 if ax.get_ylim()[1] > 0 else 1,
                f" {mean_val*100:.2f}%", color=COLORS[group], fontsize=9)

    # Probability treatment wins
    prob = (samples["treatment"] > samples["control"]).mean() * 100
    ax.set_title(
        f"Bayesian Posterior: Conversion Rate\nP(Treatment > Control) = {prob:.1f}%",
        fontsize=13, fontweight="bold", pad=12
    )
    ax.set_xlabel("Estimated Conversion Rate")
    ax.set_ylabel("Probability Density")
    ax.legend(framealpha=0.9)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x*100:.1f}%"))


# Chart 5: Average Revenue per User 
def plot_avg_revenue(metrics: dict, ax: plt.Axes):
    groups  = list(metrics.keys())
    revenues = [metrics[g]["avg_revenue"] for g in groups]
    colors   = [COLORS[g] for g in groups]

    bars = ax.bar(groups, revenues, color=colors, width=0.4, edgecolor="white", linewidth=1.5)
    for bar, val in zip(bars, revenues):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f"${val:.2f}", ha="center", va="bottom", fontweight="bold", fontsize=11)

    ax.set_title("Avg Revenue per Converting User", fontsize=13, fontweight="bold", pad=12)
    ax.set_ylabel("Revenue ($)")
    ax.set_ylim(0, max(revenues) * 1.3)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Control", "Treatment"], fontsize=11)


# Main: build the dashboard
def generate_report_charts(event_type: str = "purchase", save_path: str = "ab_test_report.png"):
    metrics       = fetch_metrics(event_type)
    distributions = fetch_revenue_distributions(event_type)
    bay_samples   = fetch_bayesian_samples(metrics)

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle("A/B Test Report — New Checkout Button",
                 fontsize=16, fontweight="bold", y=1.01)

    plot_conversion_rate(metrics,          axes[0, 0])
    plot_funnel(metrics,                   axes[0, 1])
    plot_avg_revenue(metrics,              axes[0, 2])
    plot_revenue_distribution(distributions, axes[1, 0])
    plot_bayesian_posteriors(bay_samples,  axes[1, 1])

    # Panel 6: Summary text box
    ax = axes[1, 2]
    ax.axis("off")
    ctrl  = metrics["control"]
    treat = metrics["treatment"]
    lift  = ((treat["cvr"] - ctrl["cvr"]) / ctrl["cvr"] * 100) if ctrl["cvr"] else 0
    prob  = (bay_samples["treatment"] > bay_samples["control"]).mean() * 100
    summary = (
        f"  EXPERIMENT SUMMARY\n"
        f"  {'─'*28}\n"
        f"  Control CVR   :  {ctrl['cvr']:.2f}%\n"
        f"  Treatment CVR :  {treat['cvr']:.2f}%\n"
        f"  Lift          :  {lift:+.1f}%\n\n"
        f"  P(Treatment wins) :  {prob:.1f}%\n\n"
        f"  Verdict:\n"
        f"  {'Ship Treatment ✓' if prob >= 95 else 'Promising — run longer' if prob >= 80 else 'Inconclusive — do not ship'}"
    )
    ax.text(0.05, 0.95, summary, transform=ax.transAxes,
            fontsize=11, verticalalignment="top", fontfamily="monospace",
            bbox=dict(boxstyle="round,pad=0.8", facecolor="#F0F4FF", edgecolor="#4C72B0", linewidth=1.5))

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"Chart saved to {save_path}")
    plt.show()


if __name__ == "__main__":
    generate_report_charts()
