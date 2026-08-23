# BLEY Dashboard
### Borough-Level Early Years Dashboard for Greater London

An interactive business analytics dashboard developed as part of the MSc Business Analytics dissertation at the University of Greenwich.

The Borough-Level Early Years (BLEY) Dashboard integrates publicly available government datasets into a single interactive decision-support platform that enables users to explore early years educational outcomes across Greater London's 32 boroughs.

---

## Project Overview

Early years data in England are published across multiple government organisations, making borough-level comparison difficult for policymakers, practitioners and families.

The BLEY Dashboard addresses this challenge by integrating educational, socioeconomic, demographic and childcare datasets into an accessible web application developed using **Python**, **Shiny for Python** and **Plotly**.

The dashboard enables users to:

- Explore Good Level of Development (GLD) outcomes across London boroughs
- Compare borough-level educational, demographic and socioeconomic indicators
- Investigate statistical relationships between GLD and explanatory variables
- View borough profiles through interactive maps and visualisations
- Identify boroughs that best match user preferences using the **What Fits Me** recommendation module

---

## Project Objectives

This project aimed to:

- Integrate borough-level datasets from the Department for Education (DfE), Office for National Statistics (ONS), Ofsted and the Ministry of Housing, Communities and Local Government (MHCLG).
- Construct analytical indicators relating to deprivation, educational needs, childcare provision, demographics and childcare quality.
- Identify statistical associations between contextual variables and Good Level of Development (GLD) using exploratory data analysis, correlation analysis and multiple linear regression.
- Develop an interactive dashboard using Python and Shiny that enables users to explore borough-level patterns and interpret analytical findings.
- Evaluate the dashboard through quality assurance and user acceptance testing.

---

## Dashboard Features

The dashboard consists of the following modules:

- Overview
- Borough Explorer
- Relationships
- Regression Results
- Borough Insights
- What Fits Me
- Policy Simulator
- About

Key functionality includes:

- Interactive borough comparison
- KPI summaries
- Correlation visualisations
- Regression outputs
- Interactive London borough mapping
- Borough recommendations
- Contextual housing information
- Responsive filtering and visual analytics

---

## Technology Stack

- Python
- Shiny for Python
- Plotly
- Pandas
- NumPy
- Statsmodels
- GeoJSON
- Git
- GitHub

---

## Data Sources

Official publicly available datasets were obtained from:

- Department for Education (GLD, FSM, SEN- 2022-2023)
- Office for National Statistics (Population Estimates and Census 2021)
- Ofsted (Childcare providers and inspection outcomes)
- Ministry of Housing, Communities and Local Government (Income Deprivation Affecting Children Index)
- UK House Price Data (Average Borough House Prices for 2025)

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

Clone the repository and enter the dashboard directory

```bash
git clone https://github.com/ijnicole-debug/BLEY-Dashboard-Dissertation.git
cd BLEY-Dashboard-Dissertation/dashboard
```

Create a virtual environment

```bash
python -m venv shiny_env
```

Activate the environment

Windows

```bash
shiny_env\Scripts\activate
```

macOS and Linux

```bash
source shiny_env/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Launch the application

```bash
shiny run app.py
```

The application must be launched from the `dashboard/` directory. On startup it validates the master dataset and will not start if any check fails.

---

## Live Dashboard

The deployed dashboard is available at:

**https://bleydashboard.shinyapps.io/dashboard1/**

---

## Research Outputs

The dissertation includes:

- Data integration pipeline
- Exploratory Data Analysis (EDA)
- Correlation analysis
- Multiple Linear Regression
- Interactive dashboard development
- Product validation
- User Acceptance Testing
- Implementation and commercialisation planning

---

## London Borough Coverage

The dashboard currently supports:

- 32 Greater London boroughs

Future versions are intended to support all English local authorities.

---

## Licence

This repository is provided for academic purposes.

---

## Author

-Chiamaka Ofomata

MSc Business Analytics| University of Greenwich| 2026
