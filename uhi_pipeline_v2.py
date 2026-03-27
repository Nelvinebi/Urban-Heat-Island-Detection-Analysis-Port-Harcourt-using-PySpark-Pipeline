# ============================================================
# Urban Heat Island Detection & Analysis — Port Harcourt
# PySpark Pipeline — WITH GHSL Built-up Integration
# ============================================================

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, avg, round as spark_round, month, year,
    when, lit, to_date, count
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

lst_raw  = spark.read.csv("data/MOD11A2-061-Statistics.csv",  header=True, inferSchema=True)
ndvi_raw = spark.read.csv("data/MOD13A2-061-Statistics.csv",  header=True, inferSchema=True)

# Check if GHSL CSV exists (run ghsl_converter.py first to generate it)
ghsl_available = os.path.exists("data/ghsl_portharcourt.csv")
if ghsl_available:
    ghsl_raw = spark.read.csv("data/ghsl_portharcourt.csv", header=True, inferSchema=True)
    print("✅ GHSL built-up data loaded")
else:
    print("⚠️  GHSL CSV not found — run ghsl_converter.py first")
    print("   Continuing with NDVI-based urban classification...")

print(f"✅ Raw data loaded — LST: {lst_raw.count()} rows | NDVI: {ndvi_raw.count()} rows")


# ============================================================
# STEP 3: CLEAN & TRANSFORM LST
# ============================================================

lst_clean = lst_raw.select(
    col("Dataset").alias("band"),
    to_date(col("Date")).alias("date"),
    col("Mean").cast(FloatType()).alias("lst_kelvin"),
    col("Minimum").cast(FloatType()).alias("lst_min_kelvin"),
    col("Maximum").cast(FloatType()).alias("lst_max_kelvin"),
    col("Standard Deviation").cast(FloatType()).alias("lst_std")
).dropna()

lst_clean = lst_clean \
    .withColumn("lst_celsius",     spark_round(col("lst_kelvin")     - lit(273.15), 2)) \
    .withColumn("lst_min_celsius", spark_round(col("lst_min_kelvin") - lit(273.15), 2)) \
    .withColumn("lst_max_celsius", spark_round(col("lst_max_kelvin") - lit(273.15), 2))

lst_day = lst_clean.filter(col("band") == "LST_Day_1km").select(
    col("date"),
    col("lst_celsius").alias("lst_day_celsius"),
    col("lst_min_celsius").alias("lst_day_min"),
    col("lst_max_celsius").alias("lst_day_max"),
    col("lst_std").alias("lst_day_std")
)

lst_night = lst_clean.filter(col("band") == "LST_Night_1km").select(
    col("date"),
    col("lst_celsius").alias("lst_night_celsius")
)

print("✅ LST cleaned — converted to Celsius")


# ============================================================
# STEP 4: CLEAN NDVI
# ============================================================

ndvi_clean = ndvi_raw.select(
    to_date(col("Date")).alias("date"),
    col("Mean").cast(FloatType()).alias("ndvi_mean"),
    col("Minimum").cast(FloatType()).alias("ndvi_min"),
    col("Maximum").cast(FloatType()).alias("ndvi_max")
).dropna()

print("✅ NDVI cleaned")


# ============================================================
# STEP 5: GHSL — Urban Structure Summary
# ============================================================

if ghsl_available:
    ghsl_summary = ghsl_raw.groupBy("urban_class").agg(
        count("*").alias("pixel_count"),
        spark_round(avg("built_up"), 2).alias("avg_built_up_m2")
    ).orderBy("avg_built_up_m2", ascending=False)

    print("\n🏙️  GHSL URBAN STRUCTURE — Port Harcourt:")
    ghsl_summary.show(truncate=False)

    # Calculate urban coverage percentage
    total_pixels  = ghsl_raw.count()
    urban_pixels  = ghsl_raw.filter(col("is_urban") == 1).count()
    urban_pct     = round((urban_pixels / total_pixels) * 100, 2)

    print(f"   Total pixels     : {total_pixels}")
    print(f"   Urban pixels     : {urban_pixels}")
    print(f"   Urban coverage   : {urban_pct}%")


# ============================================================
# STEP 6: MERGE LST + NDVI (Monthly)
# ============================================================

lst_day    = lst_day.withColumn("year",  year("date")).withColumn("month", month("date"))
lst_night  = lst_night.withColumn("year", year("date")).withColumn("month", month("date"))
ndvi_clean = ndvi_clean.withColumn("year", year("date")).withColumn("month", month("date"))

lst_monthly = lst_day.groupBy("year", "month").agg(
    spark_round(avg("lst_day_celsius"), 2).alias("avg_lst_day"),
    spark_round(avg("lst_day_min"),     2).alias("avg_lst_day_min"),
    spark_round(avg("lst_day_max"),     2).alias("avg_lst_day_max")
)

lst_night_monthly = lst_night.groupBy("year", "month").agg(
    spark_round(avg("lst_night_celsius"), 2).alias("avg_lst_night")
)

ndvi_monthly = ndvi_clean.groupBy("year", "month").agg(
    spark_round(avg("ndvi_mean"), 4).alias("avg_ndvi"),
    spark_round(avg("ndvi_min"),  4).alias("avg_ndvi_min"),
    spark_round(avg("ndvi_max"),  4).alias("avg_ndvi_max")
)

df = lst_monthly \
    .join(lst_night_monthly, ["year", "month"], "left") \
    .join(ndvi_monthly,      ["year", "month"], "left") \
    .orderBy("year", "month")

print(f"✅ Merged dataset: {df.count()} monthly records")


# ============================================================
# STEP 7: CLASSIFY ZONES
# Using GHSL urban % if available, else NDVI thresholds
# ============================================================

df = df.withColumn("zone",
    when(col("avg_ndvi") < 0.2,  "High Urban")
    .when(col("avg_ndvi") < 0.4, "Urban-Suburban")
    .when(col("avg_ndvi") < 0.6, "Vegetated")
    .otherwise("Dense Vegetation")
)

# Add GHSL urban context column if available
if ghsl_available:
    df = df.withColumn("ghsl_urban_pct", lit(urban_pct))
    print(f"✅ Zones classified (GHSL urban coverage: {urban_pct}%)")
else:
    print("✅ Zones classified using NDVI thresholds")


# ============================================================
# STEP 8: COMPUTE UHI INDEX
# ============================================================

urban_avg = df.filter(col("zone").isin("High Urban", "Urban-Suburban")) \
              .agg(avg("avg_lst_day").alias("urban_temp"))
rural_avg = df.filter(col("zone").isin("Vegetated", "Dense Vegetation")) \
              .agg(avg("avg_lst_day").alias("rural_temp"))

u = urban_avg.collect()[0]["urban_temp"]
r = rural_avg.collect()[0]["rural_temp"]

if u and r:
    uhi = round(u - r, 2)
    print(f"\n🌡️  UHI INDEX RESULT:")
    print(f"   Urban avg temp    : {round(u, 2)}°C")
    print(f"   Vegetated avg temp: {round(r, 2)}°C")
    print(f"   UHI Index         : {uhi}°C")
    if ghsl_available:
        print(f"   Built-up coverage : {urban_pct}%")


# ============================================================
# STEP 9: SEASONAL ANALYSIS
# ============================================================

seasonal = df.withColumn("season",
    when(col("month").isin(12, 1, 2),  "Dry Season (Dec-Feb)")
    .when(col("month").isin(3, 4, 5),  "Early Rains (Mar-May)")
    .when(col("month").isin(6, 7, 8),  "Peak Rains (Jun-Aug)")
    .otherwise("Late Rains (Sep-Nov)")
)

seasonal_summary = seasonal.groupBy("season").agg(
    spark_round(avg("avg_lst_day"),   2).alias("avg_day_temp_C"),
    spark_round(avg("avg_lst_night"), 2).alias("avg_night_temp_C"),
    spark_round(avg("avg_ndvi"),      4).alias("avg_ndvi")
).orderBy("avg_day_temp_C", ascending=False)

print("\n📊 SEASONAL ANALYSIS:")
seasonal_summary.show(truncate=False)


# ============================================================
# STEP 10: YEARLY TREND
# ============================================================

yearly = df.groupBy("year").agg(
    spark_round(avg("avg_lst_day"),   2).alias("avg_day_temp_C"),
    spark_round(avg("avg_lst_night"), 2).alias("avg_night_temp_C"),
    spark_round(avg("avg_ndvi"),      4).alias("avg_ndvi")
).orderBy("year")

print("📈 YEARLY TEMPERATURE TREND:")
yearly.show(truncate=False)


# ============================================================
# STEP 11: ZONE SUMMARY
# ============================================================

zone_summary = df.groupBy("zone").agg(
    spark_round(avg("avg_lst_day"),   2).alias("avg_day_temp_C"),
    spark_round(avg("avg_lst_night"), 2).alias("avg_night_temp_C"),
    spark_round(avg("avg_ndvi"),      4).alias("avg_ndvi")
).orderBy("avg_day_temp_C", ascending=False)

print("🌿 TEMPERATURE BY VEGETATION ZONE:")
zone_summary.show(truncate=False)


# ============================================================
# STEP 12: TOP 10 HOTTEST MONTHS
# ============================================================

hotspots = df.select("year", "month", "avg_lst_day", "avg_ndvi", "zone") \
             .orderBy(col("avg_lst_day").desc()).limit(10)

print("🔥 TOP 10 HOTTEST MONTHS:")
hotspots.show(truncate=False)


# ============================================================
# STEP 13: EXPORT ALL RESULTS (using pandas — Windows safe)
# ============================================================

os.makedirs("output", exist_ok=True)

# Convert Spark DataFrames to pandas and save as single CSV files
df.toPandas().to_csv("output/uhi_monthly_analysis.csv", index=False)
print("✅ Saved: output/uhi_monthly_analysis.csv")

seasonal_summary.toPandas().to_csv("output/uhi_seasonal_summary.csv", index=False)
print("✅ Saved: output/uhi_seasonal_summary.csv")

yearly.toPandas().to_csv("output/uhi_yearly_trend.csv", index=False)
print("✅ Saved: output/uhi_yearly_trend.csv")

zone_summary.toPandas().to_csv("output/uhi_zone_summary.csv", index=False)
print("✅ Saved: output/uhi_zone_summary.csv")

hotspots.toPandas().to_csv("output/uhi_hotspots.csv", index=False)
print("✅ Saved: output/uhi_hotspots.csv")

if ghsl_available:
    ghsl_summary.toPandas().to_csv("output/ghsl_urban_structure.csv", index=False)
    print("✅ Saved: output/ghsl_urban_structure.csv")

print("\n✅ All results exported to output/")
print("🎉 UHI Pipeline Complete!")

spark.stop()
