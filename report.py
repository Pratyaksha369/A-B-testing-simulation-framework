def print_report(experiment_name: str, control: dict, treatment: dict,
                 ttest_result: dict, bayesian_result: dict):
    sep = "=" * 55

    print(f"\n{sep}")
    print(f"  EXPERIMENT REPORT")
    print(f"  {experiment_name}")
    print(sep)

    print(f"\n{'Metric':<28} {'Control':>12} {'Treatment':>12}")
    print("-" * 55)
    print(f"{'Users in group':<28} {control['total_users']:>12} {treatment['total_users']:>12}")
    print(f"{'Conversions':<28} {control['converters']:>12} {treatment['converters']:>12}")
    print(f"{'Conversion rate (%)':<28} {control['conversion_rate']:>12} {treatment['conversion_rate']:>12}")
    print(f"{'Avg revenue ($)':<28} {control['avg_revenue']:>12} {treatment['avg_revenue']:>12}")

    # Calculate relative improvement of treatment vs control
    if control['conversion_rate'] and control['conversion_rate'] > 0:
        lift = ((treatment['conversion_rate'] - control['conversion_rate'])
                / control['conversion_rate'] * 100)
        print(f"\n  Relative lift in conversion rate: {lift:+.1f}%")

    print(f"\n{sep}")
    print("  STATISTICAL RESULTS")
    print(sep)

    # T-test
    print(f"\n  [{ttest_result['method']}]")
    if ttest_result.get("error"):  # ✅ gracefully handle NaN / failed test
        print(f"  ⚠  {ttest_result['error']}")
    else:
        print(f"  t-statistic : {ttest_result['t_statistic']}")
        print(f"  p-value     : {ttest_result['p_value']}")
        if ttest_result['significant']:
            print("  Result      : STATISTICALLY SIGNIFICANT (p < 0.05) ✓")
        else:
            print("  Result      : Not significant — need more data")

    # Bayesian
    print(f"\n  [{bayesian_result['method']}]")
    prob = bayesian_result['prob_treatment_better'] * 100
    print(f"  Probability treatment is better: {prob:.1f}%")
    if prob >= 95:
        print("  Conclusion  : Strong evidence — ship Treatment ✓")
    elif prob >= 80:
        print("  Conclusion  : Promising — run longer to be sure")
    else:
        print("  Conclusion  : Inconclusive — do not ship yet")

    print(f"\n{sep}\n")
