# PrivacyRisq – Interactive Privacy Risk Analysis Dashboard

## Overview

**PrivacyRisq** is an interactive dashboard application designed to analyze and visualize privacy-related incidents using structured datasets.

The project transforms complex privacy and risk-related data into clear, interactive visualizations that are easy to explore and understand — even for users without programming knowledge.

The dashboard is built using:

- Python  
- Plotly  
- Dash  

Users interact with the system through a web-based interface.

---

## Purpose of the Project

The main objectives of this project are:

- Analyze privacy and data protection incidents
- Identify patterns in actors, motivations, assets, exposure, and technical aspects
- Present findings in a visual and accessible format
- Enable interactive exploration of structured incident data

This project is useful for:

- Students and researchers  
- Privacy and security analysts  
- Academic reviewers  
- Decision-makers interested in data-driven insights  

---

## High-Level Architecture

The system consists of:

1. **Data files (CSV format)**
2. **Data processing layer**
3. **Visualization components**
4. **Interactive dashboard interface**

The user only interacts with the dashboard — no programming knowledge is required to use the dashboard.

---

## Project Structure
privacyRisq/
│
├── dashboard.py
├── analysis.ipynb
│
├── components/
│ ├── data_handler.py
│ ├── graph_actor.py
│ ├── graph_actor_protection.py
│ ├── graph_heatmap.py
│ ├── graph_motiv_asset.py
│ ├── graph_motiv_exposure.py
│ ├── graph_tech_sensitivity.py
│ └── graph_tech_sophistication.py
│
├── data/
│ └── incidents-export-2026-02-01.csv
│
├── assets/
│ └── style.css
│
└── requirements.txt


---

## Explanation of Key Components

### 1. `dashboard.py` 
This file starts the dashboard application.

It:
- Starts the web-based dashboard
- Defines the layout (what the user sees on the screen)
- Combines multiple graphs into one interactive interface
- Launches the application locally

---

### 2. `analysis.ipynb`

This is a Jupyter Notebook used for:

 - Initial data exploration
 - Understanding trends and patterns
 - Experimenting before finalizing the dashboard

This file is mainly for analysis and learning, not required to run the dashboard.

---

### 3. `components/`
This folder contains modular building blocks of the dashboard.
Each file is responsible for one specific type of visualization.

Examples:

- `graph_actor.py` → Visualizes different actors involved in incidents using various techniques

- `graph_motiv_asset.py` → Displays motivation vs asset analysis

- `graph_tech_sensitivity.py` → Technical sensitivity insights

These are the independent chart modules that are plugged into the dashboard.

This modular design improves clarity and maintainability.

---

### 4. `data_handler.py`
Responsible for:

- Loading CSV files  
- Cleaning and preparing data  
- Ensuring compatibility with visualization modules  

It acts as the bridge between raw data and visual output.

---

### 5. `data/`
Contains all CSV datasets used in the dashboard.

- CSV files store incident records
- Each row represents an incident
- Columns describe attributes like motivation, actor, exposure, etc.

These files can be opened in Excel for inspection.

---

### 6. `assets/style.css`
Controls layout and visual styling of the dashboard:

- Colors  
- Spacing  
- Fonts  
- Design consistency  

---

### 7. `requirements.txt`

This file lists all software libraries required to run the project.
It ensures the project can be set up consistently on different machines.

---

## How to Run the Dashboard

### Step 1: Install Python  
Ensure Python 3.9+ is installed.

### Step 2: Install Dependencies

`pip install -r requirements.txt`

### Step 3: Start the dashboard
`python dashboard.py`

### Ste 4 : Open the provided local web address in a browser
 - Example: `http://127.0.0.1:8050`

# Troubleshooting Guide

This section provides clear, step-by-step solutions for common issues when running the PrivacyRisq dashboard.

---

## 1. CSV File Not Loading Correctly (Separator Issue)

### Problem
- Graphs are empty  
- Data looks incorrect  
- Errors occur when loading CSV files  

### Cause
Some CSV files use:
- `,` (comma) as separator  
- `;` (semicolon) as separator (common in European Excel exports)

If the wrong separator is used, the data will not load properly.

### Solution

#### Step 1: Check the CSV File
1. Open the CSV file in a text editor.
2. Look at how values are separated:
   - `value1,value2,value3` → use comma
   - `value1;value2;value3` → use semicolon

#### Step 2: Update the Code (if needed)

Open `data_handler.py` and modify the CSV loading line:

```python
pd.read_csv("data/your_file.csv", sep=";")
```
---

## 2. File Not Found Error

### Problem
- FileNotFoundError: No such file or directory
### Cause
- File is not inside the data/ folder
- Filename mismatch
- Script run from wrong directory

### Solution
- Ensure the CSV file is located in:
  `privacyRisq/data/`
- Verify the filename matches exactly (case-sensitive).
- Run the application from the project root:
```bash
cd privacyRisq
python dashboard.py
```
---
## 3. Missing Python Library

### Problem
```python
ModuleNotFoundError: No module named 'dash'
```
### solution
- Install dependencies:
```bash
pip install -r requirements.txt
```
- If needed
```bash 
python -m pip install -r requirements.txt
```
- Then restart the application.

---






