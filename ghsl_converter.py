# ============================================================
# GHSL Built-up Data — GeoTIFF to CSV Converter
# For Urban Heat Island Project — Port Harcourt
# ============================================================
# Run this BEFORE the main uhi_pipeline.py
# Output: data/ghsl_portharcourt.csv
# ============================================================

import rasterio
import rasterio.mask
import numpy as np
import pandas as pd
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.crs import CRS
import os

# -------------------------------------------------------
# CONFIG — update file path if needed
# -------------------------------------------------------
INPUT_TIF  = "data/GHS_BUILT_S_E2030_GLOBE_R2023A_54009_100_V1_0_R9_C19.tif"
OUTPUT_CSV = "data/ghsl_portharcourt.csv"

# Port Harcourt bounding box (WGS84 degrees)
PH_BOUNDS = {
    "min_lon": 6.90,
    "max_lon": 7.10,
    "min_lat": 4.70,
    "max_lat": 4.95
}

# -------------------------------------------------------
# STEP 1: INSTALL DEPENDENCY (run once in terminal)
# pip install rasterio numpy pandas
# -------------------------------------------------------

# -------------------------------------------------------
# STEP 2: REPROJECT FROM MOLLWEIDE TO WGS84
# GHSL native CRS is ESRI:54009 (Mollweide / Equal Area)
# We need EPSG:4326 (lat/lon) for PySpark joining
# -------------------------------------------------------

print("📂 Opening GHSL file...")

with rasterio.open(INPUT_TIF) as src:
    print(f"   Original CRS     : {src.crs}")
    print(f"   Original shape   : {src.shape}")
    print(f"   Original bounds  : {src.bounds}")
    print(f"   Resolution       : {src.res}")

    dst_crs = CRS.from_epsg(4326)

    # Calculate transform for reprojection
    transform, width, height = calculate_default_transform(
        src.crs, dst_crs,
        src.width, src.height,
        *src.bounds
    )

    kwargs = src.meta.copy()
    kwargs.update({
        "crs"      : dst_crs,
        "transform": transform,
        "width"    : width,
        "height"   : height,
        "nodata"   : src.nodata
    })

    # Reproject to WGS84 in memory
    reprojected = np.empty((height, width), dtype=np.float32)

    reproject(
        source      = rasterio.band(src, 1),
        destination = reprojected,
        src_transform = src.transform,
        src_crs       = src.crs,
        dst_transform = transform,
        dst_crs       = dst_crs,
        resampling    = Resampling.nearest
    )

print("✅ Reprojected to WGS84 (EPSG:4326)")

# -------------------------------------------------------
# STEP 3: CROP TO PORT HARCOURT BOUNDING BOX
# -------------------------------------------------------

print("✂️  Cropping to Port Harcourt...")

rows_all, cols_all = np.indices(reprojected.shape)

# Convert row/col indices to lat/lon
lons, lats = rasterio.transform.xy(
    transform,
    rows_all.flatten(),
    cols_all.flatten()
)

lons = np.array(lons)
lats = np.array(lats)
vals = reprojected.flatten()

# Filter to Port Harcourt bounding box
mask = (
    (lons >= PH_BOUNDS["min_lon"]) &
    (lons <= PH_BOUNDS["max_lon"]) &
    (lats >= PH_BOUNDS["min_lat"]) &
    (lats <= PH_BOUNDS["max_lat"])
)

lons_ph = lons[mask]
lats_ph = lats[mask]
vals_ph = vals[mask]

print(f"   Pixels in Port Harcourt area: {len(vals_ph)}")

# -------------------------------------------------------
# STEP 4: REMOVE NODATA VALUES
# -------------------------------------------------------

nodata_val = kwargs.get("nodata", -1)
valid_mask = (vals_ph != nodata_val) & (~np.isnan(vals_ph))

lons_ph = lons_ph[valid_mask]
lats_ph = lats_ph[valid_mask]
vals_ph = vals_ph[valid_mask]

print(f"   Valid pixels after nodata removal: {len(vals_ph)}")

# -------------------------------------------------------
# STEP 5: CREATE DATAFRAME + CLASSIFY URBAN/RURAL
# -------------------------------------------------------

df = pd.DataFrame({
    "lon"     : np.round(lons_ph, 6),
    "lat"     : np.round(lats_ph, 6),
    "built_up": np.round(vals_ph, 2)
})

# Classify urban vs rural based on built-up value
# GHSL values represent built-up surface in m²
# 0       = no built-up (rural/vegetation)
# 1-500   = low built-up (suburban)
# 500+    = high built-up (urban)

df["urban_class"] = pd.cut(
    df["built_up"],
    bins=[-1, 0, 500, 2500, float("inf")],
    labels=["Rural", "Suburban", "Urban", "High Urban"]
)

df["is_urban"] = (df["built_up"] > 0).astype(int)

print("\n📊 Urban classification breakdown:")
print(df["urban_class"].value_counts())

# -------------------------------------------------------
# STEP 6: SAVE TO CSV
# -------------------------------------------------------

os.makedirs("data", exist_ok=True)
df.to_csv(OUTPUT_CSV, index=False)

print(f"\n✅ Saved to: {OUTPUT_CSV}")
print(f"   Rows: {len(df)}")
print(f"\nSample output:")
print(df.head(10).to_string())
print("\n🎉 GHSL conversion complete! Now re-run uhi_pipeline.py")
