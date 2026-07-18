# 🌊 Potential Fishing Zone (PFZ) Forecasting using Machine Learning

An end-to-end Machine Learning pipeline for **Potential Fishing Zone (PFZ) Forecasting** using historical fish catch records and satellite-derived oceanographic data.

This project combines **30 years of historical fish catch data (1993–2023)** with multiple oceanographic variables to classify fish catch potential into **High, Medium, and Low** categories. The system also includes an automated prediction pipeline using **Apache Airflow** and an interactive visualization dashboard built with **Streamlit**. :contentReference[oaicite:1]{index=1}

---

# Project Highlights

- Historical Fish Catch Data Processing
- Data Cleaning & Standardization
- Oceanographic Feature Extraction
- Advanced Feature Engineering
- Machine Learning Classification
- Apache Airflow Automation
- Interactive Streamlit Dashboard
- PFZ Map Generation

---

# Workflow

```
Historical Fish Catch Data
                │
                ▼
      Data Cleaning & Integration
                │
                ▼
 Satellite Oceanographic Data
                │
                ▼
      Feature Extraction
                │
                ▼
     Feature Engineering
                │
                ▼
   Machine Learning Training
                │
                ▼
      Model Serialization
                │
                ▼
 Apache Airflow Prediction Pipeline
                │
                ▼
      PFZ Map Generation
                │
                ▼
      Streamlit Dashboard
```

---

# Dataset

The project integrates historical fish catch records with multiple satellite-derived oceanographic datasets.

### Historical Dataset

- Fish Catch Records (1993–2023)

### Oceanographic Variables

- Sea Surface Temperature (SST)
- Chlorophyll-a (CHL)
- Sea Surface Height (SSH)
- Ocean Surface Currents
- Wind Speed
- Sea Surface Salinity (SSS)
- Bathymetry
- Thermal Fronts
- Ekman Drift
- Eddy Information

The oceanographic datasets were obtained from:

- Copernicus Marine Services
- ERA5 Reanalysis

---

# Data Cleaning

The raw datasets originated from multiple coastal regions and had different:

- Excel formats
- Sheet structures
- Column names
- Date formats
- Fish catch representations

Cleaning included:

- Standardizing column names
- Date normalization
- Coordinate validation
- Missing value handling
- Fish catch unit standardization
- Regional dataset integration

---

# Feature Engineering

Extracted Features

- SST
- SSH
- CHL
- Ocean Current Speed
- Wind Speed
- Sea Surface Salinity
- Bathymetric Depth

Engineered Features

- Thermal Front Magnitude (CCA)
- Log-transformed Chlorophyll
- SST × CHL Interaction
- Wind × Current Interaction
- Seasonal Encoding
- Distance to Coast
- Eddy Features
- Ekman Drift Components

---

# Machine Learning

The project compares three ensemble learning algorithms:

- Random Forest Classifier
- XGBoost Classifier
- Extra Trees Classifier

## Final Model

**Extra Trees Classifier**

Performance:

| Model | Accuracy | Macro F1 |
|--------|----------|----------|
| Random Forest | 72.35% | 0.6605 |
| XGBoost | 72.55% | 0.6674 |
| **Extra Trees** | **74.33%** | **0.6977** |

The Extra Trees Classifier was selected as the final prediction model because it achieved the best overall performance. :contentReference[oaicite:2]{index=2}

---

# Automation

The complete prediction workflow is automated using **Apache Airflow**.

Pipeline Stages:

- File Validation
- Dataset Loading
- Feature Extraction
- Feature Engineering
- Prediction
- PFZ Map Generation
- Output Generation

---

# Dashboard

An interactive dashboard was developed using **Streamlit**.

Features include:

- Home Page
- Prediction Classifier
- Analytics
- Trends
- Downloads
- PFZ Map Visualization

---

# Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn
- XGBoost
- Xarray
- NetCDF4
- Cartopy
- Matplotlib
- Streamlit
- Apache Airflow
- Joblib

---

# Repository Structure

```
PFZ-Prediction-System
│
├── algo/
├── Data/
├── Data_cleaning/
├── Model/
└── prediction&dashboard/
    ├── Models/
    ├── scripts/
    └── dashboard/
```

---

# Installation

Clone the repository

```bash
git clone https://github.com/nithinvodlakonda/PFZ-Prediction-System.git
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the dashboard

```bash
streamlit run prediction&dashboard/scripts/dashboard/app.py
```

---

# Notes

Large NetCDF datasets (`.nc`) and generated prediction outputs are not included in this repository because of their size.

The trained model file (`extra_trees_pfz_model.pkl`) has also been excluded due to GitHub's file size limitations. It can be regenerated using the training notebook in the `Model` directory.

---

# Author

**Nithin Vodlakonda**

GitHub: https://github.com/nithinvodlakonda

---

## Acknowledgement

This project was developed as part of an academic internship on **Potential Fishing Zone Forecasting**. The repository is intended to showcase the implementation and engineering work and is not an official product or release of INCOIS.
