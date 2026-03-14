# A/B Testing Simulation Framework

A self-contained A/B testing engine built in Python that simulates user traffic, stores experiment data in SQLite, and performs both **frequentist and Bayesian statistical analysis** to evaluate experiment results.

The project demonstrates how **data-driven product teams test new features using controlled experiments** before launching them to all users.

---

## What is this?

This project was built to understand how companies like **Swiggy, Razorpay, Flipkart, Amazon, and Netflix** determine whether a product change actually improves user behavior.

Instead of relying on intuition, product teams run **A/B experiments** to compare two versions of a feature.

This system simulates that workflow:

- Users are randomly split into **control** and **treatment** groups
- Each group experiences a different product variation
- User actions (such as purchases) are tracked
- Statistical analysis determines whether the treatment actually improves performance or if the observed difference is just random noise

The project implements both:

- **Frequentist analysis** (Two-sample t-test)
- **Bayesian analysis** (Beta-Binomial simulation)

to evaluate experiment results.

---

## Features

- Randomized **Control vs Treatment assignment**
- **Sticky user assignment** ensuring users remain in the same experiment group
- Event tracking using **SQLite database**
- Simulation of user behavior and purchase conversions
- Experiment metric computation:
  - Total users
  - Conversions
  - Conversion rate
  - Average revenue
- **Frequentist statistical testing**
  - Two-sample t-test
- **Bayesian experiment analysis**
  - Beta-Binomial simulation
  - Probability that treatment outperforms control
- Automated **experiment report generation**

---

## Project Structure

```
ab-testing-simulation-framework
│
├── main.py          # Main workflow to run the experiment
├── experiment.py    # User assignment and event logging
├── analysis.py      # Statistical analysis (t-test + Bayesian)
├── database.py      # SQLite database schema and setup
├── report.py        # Experiment report generation
├── config.yaml      # Experiment configuration
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Experiment Configuration

Experiment parameters are defined in `config.yaml`.

Example configuration:

```
experiment:
  name: "New Checkout Button"
  users: 5000
  event_type: "purchase"

metrics:
  control_cvr: 0.032
  treatment_cvr: 0.038
  avg_order_value: 45.0
```

This simulates a real-world scenario where a **new checkout button design** is tested to determine whether it improves purchase conversions.

---

## Statistical Methods

### Frequentist Approach

A **two-sample t-test** is used to determine whether the difference in revenue between control and treatment groups is statistically significant.

The test provides:

- t-statistic
- p-value
- statistical significance indicator

---

### Bayesian Approach

A **Beta-Binomial simulation** estimates the probability that the treatment performs better than the control.

Steps:

1. Model conversion rates using Beta distributions
2. Draw thousands of samples from both distributions
3. Estimate the probability that treatment conversion rate exceeds control

This provides a more intuitive interpretation of experiment results.

---

## Example Output

```
=======================================================
EXPERIMENT REPORT
New Checkout Button
=======================================================

Metric                      Control      Treatment
-------------------------------------------------------
Users in group               2498         2502
Conversions                   80           96
Conversion rate (%)          3.20         3.83
Avg revenue ($)             44.82        46.10

Relative lift in conversion rate: +19.7%

STATISTICAL RESULTS

[Two-sample t-test]
t-statistic : 2.01
p-value     : 0.044
Result      : STATISTICALLY SIGNIFICANT

[Bayesian Beta-Binomial simulation]
Probability treatment is better: 96.1%
Conclusion  : Strong evidence — ship Treatment
```

---

## Installation

Clone the repository:

```
git clone https://github.com/yourusername/ab-testing-simulation-framework.git
cd ab-testing-simulation-framework
```

Install dependencies:

```
pip install -r requirements.txt
```

---

## Running the Experiment

Run the main script:

```
python main.py
```

The script will:

1. Initialize the database
2. Simulate user behavior
3. Compute experiment metrics
4. Perform statistical analysis
5. Generate an experiment report

---

## Technologies Used

- Python
- NumPy
- SciPy
- SQLite
- YAML configuration
- Statistical inference

---

## Learning Objectives

This project demonstrates:

- Experiment design for product features
- Product analytics workflows
- Statistical significance testing
- Bayesian inference for A/B testing
- Data pipeline design using Python and SQL

---

## Future Improvements

Possible enhancements include:

- Visualization of experiment results
- Streamlit analytics dashboard
- Support for multiple experiments
- Sequential experimentation methods
- Real-time experiment monitoring

---

## License

This project is licensed under the MIT License.
