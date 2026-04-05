# 🌆 Urban Heat Island Detection & Analysis — Port Harcourt, Nigeria

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Apache Spark](https://img.shields.io/badge/Apache%20PySpark-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![Folium](https://img.shields.io/badge/Folium-77B829?style=for-the-badge&logo=folium&logoColor=white)
![NASA](https://img.shields.io/badge/NASA%20MODIS-0B3D91?style=for-the-badge&logo=nasa&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen?style=for-the-badge)
![Stars](https://img.shields.io/github/stars/Nelvinebi/Urban-Heat-Island-Detection-Analysis-Port-Harcourt-using-PySpark-Pipeline?style=for-the-badge&color=yellow)

> A scalable **Apache PySpark big data pipeline** that processes 6 years of real NASA satellite imagery (MODIS LST + NDVI + GHSL) to detect, quantify, and analyse **Urban Heat Island effects across Port Harcourt, Nigeria (2019–2024)** revealing an inverse UHI pattern driven by coastal moderation, a 2.52°C daytime cooling trend, and a 25.9% vegetation loss hidden beneath the surface.

</div>


<div align="center">

[![Live Dashboard](https://img.shields.io/badge/🚀%20Click%20for%20Live%20Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://7an7zrltefttuauc5cqwec.streamlit.app/)

</div>

---

## 📌 Problem

Port Harcourt, Nigeria's industrial heartland and oil capital, is undergoing rapid urbanisation driven by petrochemical expansion, population growth (~1.9M), and infrastructural development. Urban Heat Islands where built-up surfaces absorb and re-radiate heat, raising temperatures relative to surrounding rural areas are a well-documented consequence of unchecked urban growth in tropical coastal cities.

Yet quantifying UHI dynamics in data-sparse West African cities remains a challenge: ground-based weather networks are sparse, long-term temperature records are incomplete, and processing multi-source satellite imagery at scale demands distributed computing infrastructure beyond typical research budgets.

There is a critical need for a **reproducible, scalable, open-source pipeline** that integrates real NASA satellite data, processes it with distributed computing, and delivers actionable insights on thermal dynamics, vegetation loss, and seasonal heat patterns tailored to Port Harcourt's unique coastal-tropical context.

---

## 🎯 Objective

- Ingest and process **real MODIS satellite data** (LST 8-day composites + NDVI 16-day composites) using **Apache PySpark**
- Convert raw NASA AppEEARS statistics to analysis-ready Celsius temperature and vegetation index datasets
- Merge multi-source satellite streams (LST Day, LST Night, NDVI) into a **unified monthly dataset**
- Classify the study area into urban heat zones using **NDVI thresholds** and **GHSL built-up surface data**
- Compute the **UHI Index** (Urban Vegetated temperature difference)
- Conduct **seasonal analysis** across four climatological periods: Dry Season, Early Rains, Peak Rains, Late Rains
- Detect **temporal trends** in surface temperature, vegetation cover, and diurnal temperature range (2019–2024)
- Identify **heat hotspots** the top 10 hottest months over the study period
- Export all results to CSV and deliver an **interactive Streamlit dashboard** with Plotly charts and Folium map

---

## 🗂️ Dataset

All data is sourced from **real satellite observations** no synthetic data is used in this project.

### Satellite Data Sources

| Dataset | Source | Resolution | Purpose |
|---------|--------|------------|---------|
| `MOD11A2` v061 (LST) | NASA Earthdata / AppEEARS | 1 km, 8-day composite | Land Surface Temperature (Day & Night, °C) |
| `MOD13A2` v061 (NDVI) | NASA Earthdata / AppEEARS | 1 km, 16-day composite | Vegetation Index (greenness proxy) |
| `GHS_BUILT_S_E2030` R2023A | EU Joint Research Centre / GHSL Portal | 100 m → reprojected 1 km | Urban/rural built-up surface classification |

### Study Area

| Parameter | Value |
|-----------|-------|
| City | Port Harcourt, Rivers State, Nigeria |
| Bounding Box | Lat: 4.70°–4.95°N · Lon: 6.90°–7.10°E |
| Study Area | ~550 km² |
| Projection | WGS84 (EPSG:4326) |
| Time Period | January 2019 – December 2024 (6 years) |
| Total Records | 72 monthly composite records (post-aggregation) |

### GHSL Urban Structure (Port Harcourt, 60,500 pixels total)

| Urban Class | Pixel Count | % of Study Area | Avg Built-up Surface |
|-------------|-------------|-----------------|----------------------|
| High Urban | 18,156 | 30.0% | 4,281 m² |
| Urban | 8,756 | 14.5% | 1,442 m² |
| Suburban | 7,556 | 12.5% | 161 m² |
| Rural | 26,031 | 43.0% | 0 m² |
| **Total Urban** | **34,468** | **56.97%** | — |

---

## 🛠️ Tools & Technologies

- **Language:** Python 3.9+
- **Distributed Computing:** Apache PySpark 3.5 — SparkSession, DataFrames, distributed SQL aggregations
- **Geospatial Processing:** Rasterio — GeoTIFF reprojection, pixel extraction, CRS transformation
- **Data Processing:** Pandas, NumPy
- **Visualisation:** Plotly (interactive charts), Folium (interactive map), Matplotlib/Seaborn (static charts)
- **Dashboard:** Streamlit — multi-tab interactive web dashboard
- **Satellite Data Access:** NASA AppEEARS API (MODIS), EU GHSL Portal
- **UHI Classification:** NDVI threshold-based zone classification + GHSL built-up surface integration
- **Prerequisites:** Java 17 (Eclipse Temurin JDK — required for PySpark)

---

## ⚙️ Methodology / Project Workflow

1. **Spark Session Initialisation:** Launch PySpark SparkSession with optimised shuffle partitions (`spark.sql.shuffle.partitions=8`) for local execution
2. **Raw Data Ingestion:** Load MODIS LST statistics CSV (MOD11A2) and NDVI statistics CSV (MOD13A2) from NASA AppEEARS; conditionally load GHSL built-up CSV if generated
3. **LST Cleaning & Unit Conversion:** Select band, date, mean/min/max/std columns; cast to FloatType; drop nulls; convert all Kelvin values to Celsius (subtract 273.15); split into separate Day (LST_Day_1km) and Night (LST_Night_1km) DataFrames
4. **NDVI Cleaning:** Select date, mean/min/max columns; cast to FloatType; drop nulls to produce clean 16-day vegetation index records
5. **GHSL Urban Structure Analysis:** If GHSL CSV available aggregate pixel counts and average built-up surface by urban class; compute overall urban coverage percentage (56.97%)
6. **Monthly Aggregation & Join:** Add year/month columns to all DataFrames; group LST Day, LST Night, and NDVI records by year+month using `avg()`; join three monthly DataFrames on year+month keys using left joins
7. **Urban Zone Classification:** Classify each monthly record into heat zones using NDVI thresholds: `< 0.2` → High Urban · `0.2–0.4` → Urban-Suburban · `0.4–0.6` → Vegetated · `> 0.6` → Dense Vegetation; append GHSL urban coverage as a context column
8. **UHI Index Computation:** Filter urban records (High Urban + Urban-Suburban) and vegetated records (Vegetated + Dense Vegetation); compute mean LST Day for each group; UHI Index = Urban avg Vegetated avg
9. **Seasonal Analysis:** Classify months into four Niger Delta climatological seasons; aggregate avg day temp, night temp, and NDVI per season
10. **Yearly Trend Analysis:** Group by year; compute annual averages for day temperature, night temperature, and NDVI to reveal multi-year trends
11. **Hotspot Detection:** Rank all monthly records by descending daytime LST; extract top 10 hottest months with zone and NDVI context
12. **Export & Dashboard:** Convert Spark DataFrames to Pandas; export 5–6 CSV files to `output/`; serve interactive Streamlit dashboard with 5 tabs Overview, Temporal, Spatial, Hotspots, Map

---

## 📊 Key Features

- ✅ **Real NASA satellite data** — 6 years (2019–2024) of MODIS MOD11A2 LST and MOD13A2 NDVI at 1 km resolution, sourced from NASA AppEEARS
- ✅ **Scalable PySpark pipeline** — fully distributed processing using SparkSession DataFrames, joins, aggregations, and window operations — ready to scale to larger spatial extents
- ✅ **Multi-source data fusion** — MODIS LST (8-day) + NDVI (16-day) + GHSL built-up (GeoTIFF) merged into a unified monthly analytical dataset
- ✅ **NDVI-based urban zone classification** — four heat zones (High Urban → Urban-Suburban → Vegetated → Dense Vegetation) using NDVI thresholds, validated against GHSL urban structure
- ✅ **UHI Index computation** — quantified inverse UHI of −1.05°C (urban cooler than vegetated), attributed to Port Harcourt's coastal humidity and oceanic moderation
- ✅ **Four-season climatological analysis** — Early Rains (Mar–May), Dry Season (Dec–Feb), Late Rains (Sep–Nov), Peak Rains (Jun–Aug) — revealing pre-rain heat buildup as the dominant thermal driver
- ✅ **Diurnal Temperature Range (DTR) tracking** — day-night spread narrowed from 7.9°C (2019) to 4.4°C (2024), signalling increased nocturnal heat retention
- ✅ **10 publication-ready visualisations** — zone comparison, yearly trend, seasonal patterns, hotspot ranking, NDVI decline, urban coverage donut, pipeline architecture, temperature-vegetation scatter, DTR trend, monthly heat calendar
- ✅ **Interactive Streamlit dashboard** — 5-tab web app with Plotly charts, Folium map with neighbourhood markers, and embedded KPI metrics
- ✅ **Full CSV export** — 6 analysis outputs (monthly, seasonal, yearly, zone, hotspot, GHSL urban structure) for downstream use

---

## 📸 Visualisations

### 🔹 UHI Zone Comparison — Inverse UHI Pattern
> Urban-Suburban areas (26.9°C day) are cooler than Vegetated zones (28.0°C day), confirming a −1.05°C inverse UHI driven by Port Harcourt's coastal location and high atmospheric humidity

![UHI Zone Comparison](https://github.com/Nelvinebi/Urban-Heat-Island-Detection-Analysis-Port-Harcourt-using-PySpark-Pipeline/blob/main/visualization/01_uhi_zone_comparison.png)

---

### 🔹 Yearly Temperature Trend — The Cooling-Vegetation Paradox
> Daytime temperature declined 2.52°C (29.57°C → 27.05°C) from 2019 to 2024, even as NDVI dropped 25.9% — suggesting increased cloud cover and coastal dynamics outweigh surface vegetation effects

![Yearly Temperature Trend](https://github.com/Nelvinebi/Urban-Heat-Island-Detection-Analysis-Port-Harcourt-using-PySpark-Pipeline/blob/main/visualization/02_yearly_temperature_trend.png)

---

### 🔹 Seasonal Temperature Patterns
> Early Rains (Mar–May) is the hottest season at 28.66°C — pre-rain atmospheric heat buildup peaks before cloud cover and precipitation moderate surface temperatures through Peak Rains (Jun–Aug, 26.17°C)

![Seasonal Temperature](https://github.com/Nelvinebi/Urban-Heat-Island-Detection-Analysis-Port-Harcourt-using-PySpark-Pipeline/blob/main/visualization/03_seasonal_temperature.png)

---

### 🔹 Top 10 Hottest Months — 2020 Heat Cluster
> April 2020 is the all-time peak at 31.18°C. Four of the top 10 hottest months occurred in 2020, making it the most thermally intense year; three months (Apr/Mar 2020, Apr 2021) exceeded the 30°C threshold

![Hotspots 2020 Cluster](https://github.com/Nelvinebi/Urban-Heat-Island-Detection-Analysis-Port-Harcourt-using-PySpark-Pipeline/blob/main/visualization/04_hotspots_2020_cluster.png)

---

### 🔹 Vegetation Decline (NDVI) — 2019–2024
> NDVI fell from 0.5635 (2019) to 0.4174 (2024), a 25.9% reduction in vegetation cover — clear evidence of ongoing urbanisation and land-use conversion despite the paradoxical cooling in surface temperatures

![NDVI Decline Trend](https://github.com/Nelvinebi/Urban-Heat-Island-Detection-Analysis-Port-Harcourt-using-PySpark-Pipeline/blob/main/visualization/05_ndvi_decline_trend.png)

---

### 🔹 Urban Land Classification — GHSL Donut Chart
> 56.97% of the study area (34,468 pixels) is built-up; High Urban alone accounts for 30.0% (18,156 pixels) with an average built-up surface of 4,281 m² per pixel, confirming Port Harcourt's dense urban footprint

![Urban Coverage Donut](https://github.com/Nelvinebi/Urban-Heat-Island-Detection-Analysis-Port-Harcourt-using-PySpark-Pipeline/blob/main/visualization/06_urban_coverage_donut.png)

---

### 🔹 PySpark UHI Pipeline Architecture
> End-to-end data flow from raw NASA CSV/GeoTIFF inputs through PySpark ingestion, Kelvin→Celsius conversion, monthly aggregation, NDVI-based zone classification, UHI index computation, and CSV export + Streamlit dashboard

![Pipeline Architecture](https://github.com/Nelvinebi/Urban-Heat-Island-Detection-Analysis-Port-Harcourt-using-PySpark-Pipeline/blob/main/visualization/07_pipeline_architecture.png)

---

### 🔹 Temperature vs Vegetation Scatter — Inverse Correlation
> Scatter plot of monthly NDVI vs daytime LST coloured by zone classification; the positive trend line (slope: 5.2) confirms that vegetated areas are warmer — the hallmark of Port Harcourt's coastal inverse UHI. Peak: 31.2°C (April 2020)

![Temperature vs NDVI Scatter](https://github.com/Nelvinebi/Urban-Heat-Island-Detection-Analysis-Port-Harcourt-using-PySpark-Pipeline/blob/main/visualization/08_temp_ndvi_scatter.png)

---

### 🔹 Diurnal Temperature Range (DTR) Trend
> Day-night temperature spread narrowed from 7.9°C (2019) to 4.4°C (2024) — a 44% compression of the diurnal range, indicating increasing nocturnal heat retention consistent with urban surface densification and reduced radiative cooling

![Day Night Spread](https://github.com/Nelvinebi/Urban-Heat-Island-Detection-Analysis-Port-Harcourt-using-PySpark-Pipeline/blob/main/visualization/09_day_night_spread.png)

---

### 🔹 Monthly Temperature Heat Calendar (2019–2024)
> Full 72-month heatmap showing LST Day by year and month; darker red = hotter. April consistently hot across years; July–August consistently coolest. The 2022 July anomaly (23.5°C) stands out as a notable cooling event

![Heat Calendar](https://github.com/Nelvinebi/Urban-Heat-Island-Detection-Analysis-Port-Harcourt-using-PySpark-Pipeline/blob/main/visualization/10_heat_calendar.png)

> 📌 *All visualisations are saved at high resolution in the `/visualization/` folder.*

---

## 📈 Results & Insights

### Key Metrics Summary

| Metric | Value | Context |
|--------|-------|---------|
| UHI Index | **−1.05°C** | Inverse UHI — urban cooler than vegetated |
| Urban Coverage (GHSL) | **56.97%** | 34,468 of 60,500 pixels are built-up |
| Peak Temperature | **31.18°C** | April 2020 — all-time study-period high |
| Avg Daytime Temp (2019–2024) | **27.66°C** | 6-year mean across all zones |
| Daytime Temp Trend | **−2.52°C** | 29.57°C (2019) → 27.05°C (2024) |
| Hottest Season | **28.66°C** | Early Rains (Mar–May) |
| Coolest Season | **26.17°C** | Peak Rains (Jun–Aug) |
| NDVI Trend | **−25.9%** | 0.5635 (2019) → 0.4174 (2024) |
| DTR Trend | **−3.5°C** | 7.9°C (2019) → 4.4°C (2024) |

### Seasonal Analysis

| Season | Avg Day Temp (°C) | Avg Night Temp (°C) | Avg NDVI |
|--------|-------------------|---------------------|----------|
| Early Rains (Mar–May) | **28.66** | 22.75 | 0.4662 |
| Dry Season (Dec–Feb) | 27.78 | 22.38 | 0.4179 |
| Late Rains (Sep–Nov) | 27.42 | 21.92 | 0.4071 |
| Peak Rains (Jun–Aug) | **26.17** | 21.22 | 0.3597 |

### Temperature by Vegetation Zone

| Zone | Avg Day Temp (°C) | Avg Night Temp (°C) | Avg NDVI |
|------|-------------------|---------------------|----------|
| Vegetated | **27.97** | 22.49 | 0.4735 |
| Dense Vegetation | 27.49 | 23.14 | 0.6330 |
| Urban-Suburban | **26.91** | 21.49 | 0.3250 |

### Yearly Trend

| Year | Avg Day Temp (°C) | Avg Night Temp (°C) | Avg NDVI |
|------|-------------------|---------------------|----------|
| 2019 | 29.57 | 21.70 | 0.5635 |
| 2020 | 27.95 | 21.88 | 0.4230 |
| 2021 | 27.60 | 21.93 | 0.4057 |
| 2022 | 27.35 | 21.36 | 0.3613 |
| 2023 | 27.44 | 22.60 | 0.4441 |
| 2024 | 27.05 | 22.63 | 0.4174 |

### Key Insights

- 🔍 **Inverse UHI confirmed:** Urban zones (26.91°C) are 1.06°C cooler than Vegetated areas (27.97°C) — atypical of most tropical megacities, attributed to Port Harcourt's Atlantic coastal position, high relative humidity, and sea-breeze moderation of urban heat
- 🔍 **The cooling-vegetation paradox:** Daytime temperature fell 2.52°C from 2019 to 2024 despite NDVI declining 25.9% — increased Atlantic cloud cover and oceanic cooling likely outweigh the warming effect of vegetation loss in this coastal environment
- 🔍 **2020 heat cluster:** Four of the top 10 hottest months occurred in 2020 (Feb, Mar, Apr, May), with three breaching 30°C; likely linked to a suppressed wet season onset and reduced cloud shielding that year
- 🔍 **Pre-rain heat buildup dominates:** Early Rains (Mar–May) at 28.66°C is consistently the hottest season — as humidity rises but rainfall has yet to begin, sensible heat flux peaks before clouds and precipitation moderate temperatures through the June–August peak rainy season
- 🔍 **DTR compression signals urban heat retention:** The day-night temperature gap narrowed from 7.9°C to 4.4°C over six years — as built-up surfaces and impervious cover increase, nocturnal radiative cooling slows, narrowing the diurnal range even as daytime temperatures trend downward
- 🔍 **56.97% urban coverage:** Over half the study area is classified as built-up by GHSL, with 30.0% in the High Urban class (avg 4,281 m² built-up surface per pixel) — confirming Port Harcourt as one of Nigeria's most intensely urbanised coastal cities
- 🔍 **NDVI trough in 2022 (0.3613):** Vegetation hit its lowest recorded value in 2022, coinciding with October 2022 appearing in the top 10 hottest months and the lowest annual average night temperature (21.36°C) — suggesting a particularly stressed dry-vegetation year

---

## 🚀 Live Dashboard

📊 **[View the Interactive Streamlit Dashboard →](https://7an7zrltefttuauc5cqwec.streamlit.app/)**

The dashboard features 5 interactive tabs:
- **Overview** — KPI cards (UHI index, peak temp, urban coverage, NDVI trend) + zone comparison + urban donut
- **Temporal** — Yearly trend with dual-axis NDVI overlay + seasonal comparison charts
- **Spatial** — Hotspot rankings + temperature-NDVI scatter coloured by zone
- **Hotspots** — Top 10 hottest months table + 2020 heat cluster analysis
- **Map** — Interactive Folium map of Port Harcourt with neighbourhood temperature markers

---

## 📁 Repository Structure

```
📦 Urban-Heat-Island-Detection-Analysis-Port-Harcourt-using-PySpark-Pipeline/
│
├── 📂 data/
│   ├── MOD11A2-061-Statistics.csv          # MODIS Land Surface Temperature (8-day, NASA AppEEARS)
│   ├── MOD13A2-061-Statistics.csv          # MODIS NDVI Vegetation Index (16-day, NASA AppEEARS)
│   ├── GHS_BUILT_S_E2030_...tif            # GHSL Built-up Surface GeoTIFF (EU JRC R2023A)
│   └── ghsl_portharcourt.csv               # GHSL converted to CSV (auto-generated by ghsl_converter.py)
│
├── 📂 output/
│   ├── uhi_monthly_analysis.csv            # Full monthly LST + NDVI + zone dataset
│   ├── uhi_seasonal_summary.csv            # Avg temps and NDVI by season
│   ├── uhi_yearly_trend.csv                # Annual averages (2019–2024)
│   ├── uhi_zone_summary.csv                # Avg temps and NDVI by vegetation zone
│   ├── uhi_hotspots.csv                    # Top 10 hottest months ranked
│   └── ghsl_urban_structure.csv            # Urban coverage breakdown by class
│
├── 📂 visualization/
│   ├── 01_uhi_zone_comparison.png          # Temperature by vegetation zone — inverse UHI
│   ├── 02_yearly_temperature_trend.png     # Yearly temp decline vs NDVI loss paradox
│   ├── 03_seasonal_temperature.png         # Seasonal temperature patterns (4 seasons)
│   ├── 04_hotspots_2020_cluster.png        # Top 10 hottest months, 2020 heat cluster
│   ├── 05_ndvi_decline_trend.png           # NDVI decline 0.5635 → 0.4174 (2019–2024)
│   ├── 06_urban_coverage_donut.png         # GHSL urban land classification donut chart
│   ├── 07_pipeline_architecture.png        # PySpark UHI pipeline architecture flowchart
│   ├── 08_temp_ndvi_scatter.png            # Temperature vs NDVI scatter by zone
│   ├── 09_day_night_spread.png             # Diurnal temperature range (DTR) trend
│   └── 10_heat_calendar.png               # Monthly temperature heat calendar (2019–2024)
│
├── uhi_pipeline.py                         # Main PySpark UHI analysis pipeline
├── uhi_pipeline_v2.py                      # Extended pipeline with full GHSL integration
├── ghsl_converter.py                       # Converts GHSL GeoTIFF → CSV for PySpark ingestion
├── streamlit_app.py                        # Interactive Streamlit dashboard (5 tabs)
├── requirements.txt                        # Python dependencies
└── README.md
```

---

## ▶️ How to Run

### Prerequisites

```bash
# Python 3.9+
# Java 17 (required for PySpark) — download from: https://adoptium.net/temurin/releases/
# Set JAVA_HOME environment variable (Windows — run as Administrator):
setx JAVA_HOME "C:\Program Files\Eclipse Adoptium\jdk-17.0.xx-hotspot" /M
```

```bash
# 1. Clone the repository
git clone https://github.com/Nelvinebi/Urban-Heat-Island-Detection-Analysis-Port-Harcourt-using-PySpark-Pipeline.git
cd Urban-Heat-Island-Detection-Analysis-Port-Harcourt-using-PySpark-Pipeline

# 2. Install dependencies
pip install -r requirements.txt

# 3. Convert GHSL GeoTIFF to CSV (run once only)
python ghsl_converter.py

# 4. Run the main UHI PySpark pipeline
python uhi_pipeline.py

# 5. Launch the interactive Streamlit dashboard
streamlit run streamlit_app.py
```

**What the pipeline produces automatically:**

| Output | Location |
|--------|----------|
| Full monthly LST + NDVI + zone dataset | `output/uhi_monthly_analysis.csv` |
| Seasonal temperature summary | `output/uhi_seasonal_summary.csv` |
| Yearly trend (2019–2024) | `output/uhi_yearly_trend.csv` |
| Temperature by vegetation zone | `output/uhi_zone_summary.csv` |
| Top 10 hottest months | `output/uhi_hotspots.csv` |
| GHSL urban structure breakdown | `output/ghsl_urban_structure.csv` |

### Dependencies

```
streamlit>=1.28.0
pandas>=2.2.0
pyspark>=3.5.0
numpy>=1.24.0
folium>=0.14.0
streamlit-folium>=0.15.0
rasterio>=1.3.9
plotly>=5.0.0
altair>=5.0.0
```

---

## ⚠️ Limitations & Future Work

**Current Limitations:**
- MODIS LST at **1 km resolution** captures city-level patterns but misses intra-urban micro-scale heat variation (e.g., individual streets, rooftops, green spaces)
- The study uses **area-averaged AppEEARS statistics** rather than pixel-level spatial grids, limiting the ability to produce full choropleth temperature maps
- **NDVI-based zone classification** is a proxy for urbanisation — true land-use categories (industrial, residential, commercial) require additional ground-truth or higher-resolution data
- **No atmospheric correction verification** — MODIS LST products from AppEEARS are preprocessed but emissivity assumptions for Port Harcourt's mixed coastal land cover may introduce systematic bias
- The GHSL dataset reflects **2030 projected built-up** surface (R2023A), not annual snapshots — temporal dynamics of urban expansion within 2019–2024 are not fully captured

**Future Improvements:**
- 🛰️ Integrate **Landsat 8/9 OLI-TIRS** (30 m resolution) to capture sub-kilometre LST variation and map heat at neighbourhood level
- 🌐 Deploy a **full PySpark cluster** (AWS EMR or Google Dataproc) to extend the pipeline to all Niger Delta cities simultaneously
- 📍 Add **point-level weather station validation** to ground-truth MODIS LST retrievals against in-situ temperature records from NIMET stations
- 📉 Implement **time-series decomposition** (STL or Prophet) to separate long-term warming/cooling trends from seasonal and inter-annual variability
- 🌱 Incorporate **Sentinel-2 NDVI** (10 m resolution) for higher-fidelity vegetation mapping and cross-validation with MODIS NDVI
- 🏙️ Extend to **urban morphology metrics** — building density, sky-view factor, impervious surface fraction — to model UHI intensity from physical first principles
- 🤖 Apply **deep learning** (U-Net / CNN) to segment LST hotspots spatially and predict future heat stress zones under urbanisation scenarios

---

## 👤 Author

**Name:** Agbozu Ebingiye Nelvin

🌍 Environmental Data Scientist | GIS & Remote Sensing | Big Data Engineering | Climate Analytics
📍 Port Harcourt, Rivers State, Nigeria

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/agbozu-ebi/)
[![GitHub](https://img.shields.io/badge/GitHub-Nelvinebi-181717?style=flat-square&logo=github)](https://github.com/Nelvinebi)
[![Email](https://img.shields.io/badge/Email-nelvinebingiye%40gmail.com-D14836?style=flat-square&logo=gmail)](mailto:nelvinebingiye@gmail.com)
[![Streamlit Apps](https://img.shields.io/badge/Streamlit%20Apps-FF4B4B?style=flat-square&logo=streamlit)](https://share.streamlit.io/user/nelvinebi)

---

## 📄 License

This project is licensed under the **MIT License** — free to use, adapt, and build upon for research, education, and environmental analytics.
See the [LICENSE](LICENSE) file for full details.

---

## 🙌 Acknowledgements

- **NASA Earthdata / AppEEARS** — for providing open access to MODIS MOD11A2 (LST) and MOD13A2 (NDVI) satellite statistics
- **EU Joint Research Centre (JRC)** — for the Global Human Settlement Layer (GHSL R2023A) built-up surface dataset
- **Apache Spark** community — for the distributed computing framework powering the scalable pipeline
- **Streamlit** — for enabling rapid interactive dashboard development and free cloud deployment
- Research on Port Harcourt's UHI dynamics informed by published work from **Rivers State University Department of Urban and Regional Planning**

---

<div align="center">

⭐ **If this project helped you, please consider starring the repo!**

*Part of a broader portfolio of Environmental Data Science and Big Data Engineering projects focused on the Niger Delta and West African climate systems.*

🔗 [View All Projects](https://github.com/Nelvinebi?tab=repositories) · [Connect on LinkedIn](https://www.linkedin.com/in/agbozu-ebi/) · [Live Dashboard](https://7an7zrltefttuauc5cqwec.streamlit.app/)

</div>
