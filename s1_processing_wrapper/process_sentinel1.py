import sys
import argparse
import subprocess
from typing import Any

from Sentinel1_processing.product_loader import load_product_from_path, validate_roi_intersection
from Sentinel1_processing.preprocessing import apply_orbit_file, remove_thermal_noise, calibrate_product
from Sentinel1_processing.processing import apply_speckle_filter, terrain_correct, subset_product, convert_to_db
from esa_snappy import ProductIO

product_path = "/path/to/your/sentinel1_product.zip"
wkt_roi = "POLYGON((-98.06 19.5, -97.5 19.5, -97.5 19.28, -98.06 19.28, -98.06 19.5))"
output_path = "processed_result.tif"

def process(product_path: Any, output_path: Any):
    # Load and validate product
    product = load_product_from_path(product_path)

    if validate_roi_intersection(product, wkt_roi):
        print("✅ Product intersects with ROI - proceeding with processing")
    else:
        print("❌ No intersection - stopping")

    # Preprocessing steps
    orbit_corrected = apply_orbit_file(product)
    noise_removed = remove_thermal_noise(orbit_corrected)
    calibrated = calibrate_product(noise_removed, polarization='DV')

    # Processing steps
    filtered = apply_speckle_filter(calibrated)
    terrain_corrected = terrain_correct(filtered, pixel_spacing=100.0)
    subset_result = subset_product(terrain_corrected, wkt_roi)
    final_product = convert_to_db(subset_result)

    # Save result
    ProductIO.writeProduct(final_product, output_path, 'GeoTIFF-BigTIFF')
    print(f"Processing complete: {output_path}")

    # Clean up memory
    product.dispose()
    print("Memory released")


if __name__ == "__main__":
    parse = argparse.ArgumentParser(description="Runs sentinel S1 sar processing to generate a terrain correction")
    parse.add_argument("--product_path", help="Input file to use", required=True)
    parse.add_argument("--product_path", help="Input file to use", required=True)
    parse.add_argument("--output_file", help="Output file to write", required=True)
    # parse.add_argument("--outsize", help="Reduction size", required=True)
    args = parse.parse_args()
    # env_check()
    exit_code, output = process(args.product_path, args.output_file) # type: ignore
    if exit_code != 0:
        print(f"sentinel s1 failed with a non-zero exit code: {exit_code}")
        exit(exit_code)