# 🌆 Urban Heat Island Detection & Analysis — Port Harcourt

A scalable big data pipeline for detecting and analyzing Urban Heat Island (UHI) effects in Port Harcourt, Nigeria, using Apache PySpark and real satellite datasets.

---

## 📌 Project Overview

Urban Heat Islands (UHIs) occur when cities are significantly warmer than surrounding rural areas due to human activities and land cover changes. This project:

- Processes multi-source satellite data using **Apache PySpark**
- Computes UHI intensity across Port Harcourt (2019–2024)
- Analyzes seasonal and yearly temperature trends
- Correlates temperature with vegetation (NDVI) and built-up area (GHSL)
- Detects the hottest months and urban heat hotspots
- Visualizes all findings in an interactive HTML dashboard

---

## 🗂️ Project Structure

```
UHI_PortHarcourt/
│
├── data/
│   ├── MOD11A2-061-Statistics.csv        # MODIS Land Surface Temperature
│   ├── MOD13A2-061-Statistics.csv        # MODIS NDVI Vegetation Index
│   ├── GHS_BUILT_S_E2030_...tif          # GHSL Built-up Surface (GeoTIFF)
│   └── ghsl_portharcourt.csv             # GHSL converted to CSV (auto-generated)
│
├── ghsl_converter.py                     # Converts GHSL GeoTIFF → CSV
├── uhi_pipeline_v2.py                    # Main PySpark UHI pipeline
├── requirements.txt                      # Python dependencies
│
├── output/
│   ├── uhi_monthly_analysis.csv          # Full monthly dataset
│   ├── uhi_seasonal_summary.csv          # Temps by season
│   ├── uhi_yearly_trend.csv              # Temps by year (2020–2024)
│   ├── uhi_zone_summary.csv              # Temps by vegetation zone
│   ├── uhi_hotspots.csv                  # Top 10 hottest months
│   └── ghsl_urban_structure.csv          # Urban coverage breakdown
│
└── uhi_dashboard.html                    # Interactive visualization dashboard
```

---

## 📊 Datasets Used

| Dataset | Source | Purpose |
|---|---|---|
| MODIS MOD11A2 (LST) | NASA Earthdata / AppEEARS | Land Surface Temperature (day & night) |
| MODIS MOD13A2 (NDVI) | NASA Earthdata / AppEEARS | Vegetation Index |
| GHSL R2023A Built-up | EU Joint Research Centre | Urban/rural classification |

- **Study Area:** Port Harcourt, Nigeria (Lat: 4.70–4.95, Lon: 6.90–7.10)
- **Time Period:** 2019–2024
- **Projection:** WGS84 (EPSG:4326)

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.9+
- Java 17 (required for PySpark)
- Anaconda (recommended)

### Install Java 17
Download from: https://adoptium.net/temurin/releases/
Select: JDK 17 LTS → Windows → x64 → .msi

Set environment variable (run as Administrator):
```bash
setx JAVA_HOME "C:\Program Files\Eclipse Adoptium\jdk-17.0.xx-hotspot" /M
```

### Install Python Dependencies
```bash
pip install -r requirements.txt
```

---

## 🚀 Running the Pipeline

### Step 1: Convert GHSL GeoTIFF to CSV
```bash
python ghsl_converter.py
```
This only needs to be run once. It converts the GHSL `.tif` file into a CSV that PySpark can process.

### Step 2: Run the Main UHI Pipeline
```bash
python uhi_pipeline_v2.py
```
Results will be saved to the `output/` folder.

### Step 3: View the Dashboard
Open `uhi_dashboard.html` in any web browser.

---

## 🔑 Key Results

| Metric | Value |
|---|---|
| UHI Index | −1.05°C (inverse UHI pattern) |
| Urban Coverage | 56.97% of study area |
| Peak Temperature | 31.18°C (April 2020) |
| Hottest Season | Early Rains — Mar–May (28.66°C) |
| Coolest Season | Peak Rains — Jun–Aug (26.17°C) |
| Temperature Trend | −2.52°C decline (2019 → 2024) |
| NDVI Trend | −25.9% vegetation decline (2019 → 2024) |

---

## 🧠 Key Findings

1. **Inverse UHI Pattern:** Urban zones (26.91°C) are slightly cooler than vegetated areas (27.96°C), likely due to Port Harcourt's coastal location and high humidity moderating urban heat.

2. **Cooling Trend:** Average daytime temperature declined from 29.57°C (2019) to 27.05°C (2024), a 2.52°C drop over the study period.

3. **Seasonal Heat Peaks:** The hottest period is Early Rains (March–May), when pre-rain atmospheric buildup intensifies surface temperatures before cloud cover and rainfall moderate them.

4. **2020 Heat Cluster:** Four of the top 10 hottest months occurred in 2020 (Feb, Mar, Apr, May), making it the most thermally intense year despite not having the highest annual average.

5. **Vegetation Loss:** NDVI declined 25.9% from 2019 to 2024, indicating ongoing urbanisation and land-use change in Port Harcourt.

6. **High Urbanisation:** 56.97% of the study area is built-up, with 18,156 pixels classified as High Urban (avg built-up surface: 4,281 m²).

---

## 🛠️ Pipeline Architecture

```
Raw Data (CSV/GeoTIFF)
        ↓
  PySpark Ingestion
        ↓
  Data Cleaning & Kelvin → Celsius Conversion
        ↓
  Monthly Aggregation (LST + NDVI join)
        ↓
  Urban Zone Classification (NDVI thresholds + GHSL)
        ↓
  UHI Index Computation (Urban − Vegetated)
        ↓
  Seasonal & Yearly Analysis
        ↓
  Hotspot Detection (Top 10 months)
        ↓
  CSV Export + HTML Dashboard
```

---

## 📦 Technologies Used

- **Apache PySpark** — distributed data processing
- **Pandas** — data export
- **Rasterio** — GeoTIFF processing and reprojection
- **NumPy** — array operations
- **Chart.js** — dashboard visualizations
- **NASA AppEEARS** — satellite data extraction
- **GHSL Portal** — urban land cover data

---

## 📄 License

This project is for educational and portfolio purposes.

---

## 👤 Author

Built as part of a Data Engineering + Geospatial Analytics portfolio project.
Study Area: Port Harcourt, Rivers State, Nigeria.
