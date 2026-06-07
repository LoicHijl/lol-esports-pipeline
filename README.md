# LoL esports pipeline

A data engineering project that ingests, processes and visualizes League of Legends Esports data from the Fandom Wiki API to analyze pick-ban priorities and team/player performances.ayer performance.

---

## 1. Project Overview

This project builds and automated end-to-end data pipeline to extract semi-structured competetive match data from the Leaguepedia/Fandom Wiki API. The goal is to transform this raw, nested data into clean, analytical models that can be used to highlight drafting priorities (pick/ban rates, meta shifts, counterpick rates) and team/player performance metrics (early game performance, resource efficiency, lead conversion efficiency). By utilizing modern data engineering tools and practices, this project demonstrates how to handle complex API strucutres and deliver clean datasets to an interactive dashboard.

---

## 2. Architecture & Data Flow

                  [ Fandom Wiki API ]
                           │
                           ▼  (Python Script / PySpark)
               ┌───────────────────────┐
               │   AWS S3 (Bronze)     │ <─── Free Tier / Local Simulation
               └───────────────────────┘
                           │
                           ▼  (Apache Spark / PySpark)
               ┌───────────────────────┐
               │   AWS S3 (Silver)     │ <─── Local Delta / Parquet files
               └───────────────────────┘
                           │
                           ▼  (DuckDB / PostgreSQL)
               ┌───────────────────────┐
               │    Data Warehouse     │ <─── Locally hosted
               └───────────────────────┘
                           │
                           ▼  (dbt Core)
               ┌───────────────────────┐
               │    Gold Layer / Data  │ <─── Fact & Dimension Tables
               │       Modeling        │
               └───────────────────────┘
                           │
                           ▼  (Streamlit)
               ┌───────────────────────┐
               │ Interactive Dashboard │ <─── Localhost / Streamlit Community Cloud
               └───────────────────────┘

---

### Architectural Notes & Cost Optimization
* **Local Simulation & Free Alternatives:** Because this started as a solo project, the goal was to keep costs relatively low. As such it uses only free tools and local simulations instead of a full cloud service. Possibilities to upgrade the project exists at a later stage. 
Currently the plan is to use AWS S3, which can be simulated locally. DuckDB will be utilized as a zero-cost, serverless, in-process analytical database.

* **Deployment Path:** The architecture will be intentionally decoupled. This allows for easy migration of the PySpark transformation scripts into AWS EMR or AWS Glue. Local Parquet files can also easily be pointed to an actual cloud AWS S3 bucket, and DuckDB can be swapped for a paid alternative like Amazon Redshift or Snowflake with minimal modifications.

---

## 3. Tech Stack & Justification

| Technology | Role in Project | Justification |
| :--- | :--- | :--- |
| **Python** | Main programming language; Data ingestion | Handles requests to the Fandom Wiki API, endpoint pagination, and intial data extraction tasks |
| **Apache Spark (PySpark)** | Heavy Compute & Processing | Chosen to efficiently flatten the JSON formats returned by the esports wiki, enforce strict schemas and drop duplicates |
| **Local Parquet Files** | Object Storage | ToDo |
| **DuckDB** | Data warehouse backend | ToDo |
| **dbt Core** | SQL Transformation | ToDo |
| **Streamlit** | Visualization UI | ToDo|


---

## 4. Data Pipeline Design

This project is currently a WIP; This section will be added later.

---

## 5. Data Quality, Testing & Governance

This project is currently a WIP; This section will be added later.

---

## 6. Dashboard Insights & Metrics

This project is currently a WIP; This section will be added later.

---

## 7. How to Setup and Run Locally (100% Free)

This project is currently a WIP; This section will be added later.