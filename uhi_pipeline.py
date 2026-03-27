# ============================================================
# Urban Heat Island Detection & Analysis — Port Harcourt
# PySpark Pipeline
# ============================================================

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, avg, round as spark_round, month, year,
    when, lit, to_date, abs as spark_abs
)
from pyspark.sql.types import FloatType
import os

# ============================================================
# STEP 1: START SPARK SESSION
# ============================================================

spark = SparkSession.builder \
    .appName("UHI_PortHarcourt") \
    .config("spark.sql.shuffle.partitions", "8") \
    .getOrCreate()

spark.sparkContext.setLogLevel("ERROR")
print("✅ Spark session started")


# ============================================================
# STEP 2: LOAD RAW DATA
# ============================================================

# --- 2a. Load LST (Land Surface Temperature) ---
lst_raw = spark.read.csv(
    "data/MOD11A2-061-Statistics.csv",
    header=True,
    inferSchema=True
)

# --- 2b. Load NDVI (Vegetation Index) ---
ndvi_raw = spark.read.csv(
    "data/MOD13A2-061-Statistics.csv",
    header=True,
    inferSchema=True
)

print("✅ Raw data loaded")
print(f"   LST records  : {lst_raw.count()}")
print(f"   NDVI records : {ndvi_raw.count()}")


# ============================================================
# STEP 3: CLEAN & TRANSFORM LST DATA
# ============================================================

# Select only the columns we need and rename them clearly
lst_clean = lst_raw.select(
    col("Dataset").alias("band"),
    to_date(col("Date")).alias("date"),
    col("Mean").cast(FloatType()).alias("lst_kelvin"),
    col("Minimum").cast(FloatType()).alias("lst_min_kelvin"),
    col("Maximum").cast(FloatType()).alias("lst_max_kelvin"),
    col("Standard Deviation").cast(FloatType()).alias("lst_std")
).dropna()

# Convert Kelvin to Celsius
# MODIS LST values from AppEEARS are already scaled (not raw integers)
lst_clean = lst_clean \
    .withColumn("lst_celsius",
        spark_round(col("lst_kelvin") - lit(273.15), 2)) \
    .withColumn("lst_min_celsius",
        spark_round(col("lst_min_kelvin") - lit(273.15), 2)) \
    .withColumn("lst_max_celsius",
        spark_round(col("lst_max_kelvin") - lit(273.15), 2))

# Split into Day and Night
lst_day = lst_clean.filter(col("band") == "LST_Day_1km") \
    .select(
        col("date"),
        col("lst_celsius").alias("lst_day_celsius"),
        col("lst_min_celsius").alias("lst_day_min"),
        col("lst_max_celsius").alias("lst_day_max"),
        col("lst_std").alias("lst_day_std")
    )

lst_night = lst_clean.filter(col("band") == "LST_Night_1km") \
    .select(
        col("date"),
        col("lst_celsius").alias("lst_night_celsius"),
        col("lst_std").alias("lst_night_std")
    )

print("✅ LST cleaned and converted to Celsius")


# ============================================================
# STEP 4: CLEAN & TRANSFORM NDVI DATA
# ============================================================

ndvi_clean = ndvi_raw.select(
    to_date(col("Date")).alias("date"),
    col("Mean").cast(FloatType()).alias("ndvi_mean"),
    col("Minimum").cast(FloatType()).alias("ndvi_min"),
    col("Maximum").cast(FloatType()).alias("ndvi_max"),
    col("Standard Deviation").cast(FloatType()).alias("ndvi_std")
).dropna()

print("✅ NDVI cleaned")


# ============================================================
# STEP 5: MERGE LST + NDVI
# NOTE: LST = 8-day composite, NDVI = 16-day composite
# We join on the nearest available date using year + month
# ============================================================

# Add year and month for joining
lst_day   = lst_day.withColumn("year", year("date")).withColumn("month", month("date"))
lst_night = lst_night.withColumn("year", year("date")).withColumn("month", month("date"))
ndvi_clean = ndvi_clean.withColumn("year", year("date")).withColumn("month", month("date"))

# Aggregate LST to monthly averages (for clean joining with NDVI)
lst_monthly = lst_day.groupBy("year", "month").agg(
    spark_round(avg("lst_day_celsius"), 2).alias("avg_lst_day"),
    spark_round(avg("lst_day_min"), 2).alias("avg_lst_day_min"),
    spark_round(avg("lst_day_max"), 2).alias("avg_lst_day_max")
)

lst_night_monthly = lst_night.groupBy("year", "month").agg(
    spark_round(avg("lst_night_celsius"), 2).alias("avg_lst_night")
)

ndvi_monthly = ndvi_clean.groupBy("year", "month").agg(
    spark_round(avg("ndvi_mean"), 4).alias("avg_ndvi"),
    spark_round(avg("ndvi_min"), 4).alias("avg_ndvi_min"),
    spark_round(avg("ndvi_max"), 4).alias("avg_ndvi_max")
)

# Join everything on year + month
df = lst_monthly \
    .join(lst_night_monthly, ["year", "month"], "left") \
    .join(ndvi_monthly, ["year", "month"], "left") \
    .orderBy("year", "month")

print("✅ LST + NDVI merged into monthly dataset")
print(f"   Combined records: {df.count()}")


# ============================================================
# STEP 6: CLASSIFY URBAN HEAT ZONES USING NDVI
# ============================================================
# NDVI thresholds for urban classification:
# < 0.2  → High Urban (concrete, roads)
# 0.2–0.4 → Urban-Suburban mix
# 0.4–0.6 → Vegetated / Suburban
# > 0.6  → Dense Vegetation / Rural

df = df.withColumn("zone",
    when(col("avg_ndvi") < 0.2,  "High Urban")
    .when(col("avg_ndvi") < 0.4, "Urban-Suburban")
    .when(col("avg_ndvi") < 0.6, "Vegetated")
    .otherwise("Dense Vegetation")
)

print("✅ Urban heat zones classified")


# ============================================================
# STEP 7: COMPUTE UHI INDEX
# ============================================================
# UHI = avg temperature of urban zones - avg temperature of vegetated zones

urban_avg = df.filter(
    col("zone").isin("High Urban", "Urban-Suburban")
).agg(avg("avg_lst_day").alias("urban_temp"))

rural_avg = df.filter(
    col("zone").isin("Vegetated", "Dense Vegetation")
).agg(avg("avg_lst_day").alias("rural_temp"))

urban_temp_val = urban_avg.collect()[0]["urban_temp"]
rural_temp_val = rural_avg.collect()[0]["rural_temp"]

if urban_temp_val and rural_temp_val:
    uhi_index = round(urban_temp_val - rural_temp_val, 2)
    print(f"\n🌡️  UHI RESULT:")
    print(f"   Urban avg temp    : {round(urban_temp_val, 2)}°C")
    print(f"   Vegetated avg temp: {round(rural_temp_val, 2)}°C")
    print(f"   UHI Index         : {uhi_index}°C")
else:
    print("⚠️  Not enough zone variety to compute UHI directly — see seasonal analysis below")


# ============================================================
# STEP 8: SEASONAL UHI ANALYSIS
# ============================================================

seasonal = df.withColumn("season",
    when(col("month").isin(12, 1, 2),  "Dry Season (Dec-Feb)")
    .when(col("month").isin(3, 4, 5),  "Early Rains (Mar-May)")
    .when(col("month").isin(6, 7, 8),  "Peak Rains (Jun-Aug)")
    .otherwise("Late Rains (Sep-Nov)")
)

seasonal_summary = seasonal.groupBy("season").agg(
    spark_round(avg("avg_lst_day"), 2).alias("avg_day_temp_C"),
    spark_round(avg("avg_lst_night"), 2).alias("avg_night_temp_C"),
    spark_round(avg("avg_ndvi"), 4).alias("avg_ndvi")
).orderBy("season")

print("\n📊 SEASONAL ANALYSIS:")
seasonal_summary.show(truncate=False)


# ============================================================
# STEP 9: YEARLY TREND ANALYSIS
# ============================================================

yearly = df.groupBy("year").agg(
    spark_round(avg("avg_lst_day"), 2).alias("avg_day_temp_C"),
    spark_round(avg("avg_lst_night"), 2).alias("avg_night_temp_C"),
    spark_round(avg("avg_ndvi"), 4).alias("avg_ndvi")
).orderBy("year")

print("📈 YEARLY TEMPERATURE TREND:")
yearly.show(truncate=False)


# ============================================================
# STEP 10: CORRELATION — TEMPERATURE vs NDVI
# ============================================================

# Simple heat zone breakdown
zone_summary = df.groupBy("zone").agg(
    spark_round(avg("avg_lst_day"), 2).alias("avg_day_temp_C"),
    spark_round(avg("avg_lst_night"), 2).alias("avg_night_temp_C"),
    spark_round(avg("avg_ndvi"), 4).alias("avg_ndvi")
).orderBy("avg_day_temp_C", ascending=False)

print("🌿 TEMPERATURE BY VEGETATION ZONE:")
zone_summary.show(truncate=False)


# ============================================================
# STEP 11: HOTSPOT DETECTION — Top 10 Hottest Months
# ============================================================

hotspots = df.select(
    "year", "month", "avg_lst_day", "avg_ndvi", "zone"
).orderBy(col("avg_lst_day").desc()).limit(10)

print("🔥 TOP 10 HOTTEST MONTHS (Hotspots):")
hotspots.show(truncate=False)


# ============================================================
# STEP 12: EXPORT RESULTS TO CSV
# ============================================================

os.makedirs("output", exist_ok=True)

# Main combined dataset
df.coalesce(1).write.mode("overwrite").csv(
    "output/uhi_monthly_analysis", header=True
)

# Seasonal summary
seasonal_summary.coalesce(1).write.mode("overwrite").csv(
    "output/uhi_seasonal_summary", header=True
)

# Yearly trend
yearly.coalesce(1).write.mode("overwrite").csv(
    "output/uhi_yearly_trend", header=True
)

# Zone summary
zone_summary.coalesce(1).write.mode("overwrite").csv(
    "output/uhi_zone_summary", header=True
)

print("\n✅ All results exported to output/ folder")
print("\n🎉 UHI Pipeline Complete!")

spark.stop()
