# BLEY Dashboard
### Borough-Level Early Years Dashboard for Greater London

An interactive business analytics dashboard developed as part of the MSc Business Analytics dissertation at the University of Greenwich.

The Borough-Level Early Years (BLEY) Dashboard integrates publicly available government datasets into a single interactive decision-support platform that enables users to explore early years educational outcomes across Greater London's 32 boroughs.

**Live dashboard:** https://bleydashboard.shinyapps.io/dashboard1/

---

## Project Overview

Early years data in England are published across multiple government organisations, in different formats and at different levels of aggregation, which makes borough-level comparison difficult for policymakers, practitioners and families.

The BLEY Dashboard addresses this by integrating educational, socioeconomic, demographic and childcare datasets into an accessible web application built with **Python**, **Shiny for Python** and **Plotly**.

The dashboard enables users to:

- Explore Good Level of Development (GLD) outcomes across London boroughs
- Compare borough-level educational, demographic and socioeconomic indicators
- Investigate statistical associations between GLD and explanatory variables
- View borough profiles through an interactive map
- Rank boroughs against priorities they set themselves, using the **What Fits Me Best** module

---

## Project Objectives

- Integrate borough-level datasets from the Department for Education (DfE), Office for National Statistics (ONS), Ofsted and the Ministry of Housing, Communities and Local Government (MHCLG).
- Construct analytical indicators covering deprivation, educational need, childcare provision, childcare quality and demography.
- Identify statistical associations between contextual variables and GLD using exploratory data analysis, correlation analysis and multiple linear regression.
- Develop an interactive dashboard that enables non-technical users to explore borough-level patterns and interpret analytical findings.
- Evaluate the dashboard through quality assurance and user acceptance testing.

---

## Dashboard Modules

| Module | Purpose |
|---|---|
| Overview | Headline indicators and the distribution of GLD across boroughs |
| Borough Explorer | Interactive choropleth map and per-borough indicator profile |
| Relationships | Scatter plots and correlations between any two indicators |
| Regression Results | Model output in plain language, with statistical detail and robustness checks |
| Policy Simulator | Modelled GLD values for different combinations of indicators |
| What Fits Me Best | Boroughs ranked against user-selected priorities |
| About | Sources, methods, model specification and limitations |

---

## Key Findings

Multiple linear regression, GLD as the outcome, 32 boroughs, six predictors:

- **Full model:** R² = 0.372, adjusted R² = 0.221, F(6, 25) = 2.46, p = 0.052
- **Childcare accessibility** was the only predictor significant within the full model (b = 0.145, p = 0.048)
- **IDACI** (r = −0.395) and **FSM eligibility** (r = −0.395) were each significantly associated with GLD individually, but neither retained significance in the full model. The two correlate at 0.803 with one another and compete to explain the same variation.
- **Ethnic diversity, SEN prevalence and Ofsted quality** showed no reliable association on either test
- **Reduced model** (childcare accessibility and FSM only): R² = 0.311, adjusted R² = 0.263, F(2, 29) = 6.53, p = 0.005 — both predictors significant

Assumption checks on the full model: Shapiro-Wilk p = 0.179, Breusch-Pagan p = 0.488, maximum VIF 4.85.

---

## Interpretation and Limitations

Please read these before drawing conclusions from anything in this repository.

- The analysis identifies **statistical associations, not causal effects**. Nothing here shows that changing one indicator would change outcomes.
- Every variable is a **borough average**. An association between borough averages may be stronger, weaker or opposite in direction to the relationship holding for individual children. Inferring the second from the first is the ecological fallacy.
- With **32 boroughs**, the analysis can detect only reasonably large associations. An indicator showing no reliable association may still matter.
- The significant associations **depend heavily on one borough**. Removing Richmond upon Thames, an outlier on childcare provision at 78.8 places per 100 children against a mean of 44.4, renders all three non-significant (childcare r falls to 0.267, p = 0.146).
- Rankings and colour scales show **relative position within Greater London**, not performance. Many indicators reflect conditions outside a local authority's control.

---

## Data Sources

All datasets are publicly available and published under the Open Government Licence v3.0.

| Indicator | Publisher | Reference period |
|---|---|---|
| Good Level of Development | DfE, EYFS Profile results | 2022/23 |
| Free School Meals eligibility | DfE, School pupils and their characteristics | 2022/23 |
| Special Educational Needs | DfE, Special educational needs in England | 2022/23 |
| IDACI | MHCLG, English Indices of Deprivation | 2019 |
| Childcare quality and places | Ofsted, Childcare providers and inspections (management information) | As at 31 December 2023 |
| Under-five population | ONS, Population estimates for England and Wales | Mid-2022 |
| Ethnic group composition | ONS, Census 2021 (table TS021) | 2021 |
| Average house prices (contextual only) | HM Land Registry, UK House Price Index | 2025 |
| Borough boundaries | Greater London Authority, London Datastore | Current release |

Contains public sector information licensed under the Open Government Licence v3.0. Contains National Statistics data © Crown copyright and database right. Borough boundary data © Greater London Authority.

---

## Notes on Derived Indicators

Two indicators are constructed rather than published, and behave differently from the raw source data.

**Ofsted quality score.** Ofsted publishes overall effectiveness on a four-point scale where **1 is Outstanding and 4 is Inadequate**. The borough score is a places-weighted mean of the most recent judgement for each provider, then **reversed so that 4 is Outstanding** and higher means better. Providers with no inspection judgement are excluded from the quality score but retained in the count of registered places, since the capacity exists whether or not the provider has been inspected. Inspection coverage varies between boroughs from 62% to 80% of registered places (mean 71%) and is carried in the dataset as `inspection_coverage`.

**Ethnic Diversity Index.** Simpson's index of diversity, calculated as 1 − Σ(pᵢ²) across the 20 Census 2021 ethnic group categories. Values run from 0 to 1, higher meaning more diverse. The index is sensitive to the number of categories used, so values are comparable between boroughs but not with figures derived from a different classification.

---

## Technology Stack

Python 3.13 · Shiny for Python · Plotly · pandas · NumPy · Statsmodels · SciPy · GeoJSON · Git

---

## Repository Structure

```
BLEY-Dashboard-Dissertation/
│
├── dashboard/
│   ├── assets/
│   │   └── style.css
│   ├── components/
│   │   └── cards.py
│   ├── data/
│   │   ├── master_dataset.csv
│   │   ├── london_boroughs.geojson
│   │   └── london_boroughs_wgs84.geojson
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── about.py
│   │   ├── explorer.py
│   │   ├── overview.py
│   │   ├── recommendations.py
│   │   ├── regression.py
│   │   ├── relationships.py
│   │   └── simulator.py
│   ├── app.py
│   └── requirements.txt
│
├── notebooks/
├── data_clean/
├── images/
├── .gitignore
├── README.md
└── LICENSE
```

---

## Running the Dashboard

Clone the repository and enter the dashboard directory:

```bash
git clone https://github.com/ijnicole-debug/BLEY-Dashboard-Dissertation.git
cd BLEY-Dashboard-Dissertation/dashboard
```

Create a virtual environment:

```bash
python -m venv shiny_env
```

Activate the environment.

Windows:

```bash
shiny_env\Scripts\activate
```

macOS and Linux:

```bash
source shiny_env/bin/activate
```

Install dependencies and launch:

```bash
pip install -r requirements.txt
shiny run app.py
```

The application must be launched from the `dashboard/` directory. On startup it validates the master dataset — column names, row count, missing values, and that the Ofsted scale has been correctly reversed — and refuses to start if any check fails.

---

## Reproducing the Dataset

`master_dataset.csv` is generated by the notebooks in `notebooks/`. Run the cleaning notebooks first, then the merge notebook:

1. Cleaning notebooks — one per source dataset, writing to `data_clean/`
2. `08_clean_childcare_places_per_100_under_5s.ipynb` — derives the accessibility indicator
3. `03_merge_variables.ipynb` — joins all cleaned datasets on local authority code and writes `master_dataset.csv`

Restart the kernel and run all cells in order, since out-of-order execution can produce inconsistent output.

---

## Research Outputs

Data integration pipeline · exploratory data analysis · correlation analysis · multiple linear regression with sensitivity analysis · interactive dashboard development · product validation · user acceptance testing · implementation and commercialisation planning.

---

## Coverage

The dashboard currently covers the 32 Greater London boroughs. Extending it to all English local authorities would substantially increase the sample size and address the statistical power limitation noted above.

---

## Licence

This repository is provided for academic purposes.

---

## Author

**Chiamaka Ofomata**

MSc Business Analytics | University of Greenwich | 2026
