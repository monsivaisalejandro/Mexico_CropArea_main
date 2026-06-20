import sys
import argparse
import subprocess
from typing import Any

from Sentinel1_processing.product_loader import load_product_from_path, validate_roi_intersection
from Sentinel1_processing.preprocessing import apply_orbit_file, remove_thermal_noise, calibrate_product
from Sentinel1_processing.processing import apply_speckle_filter, terrain_correct, subset_product, convert_to_db
from esa_snappy import ProductIO

def process(product_path: str, wkt_roi: str, output_path: str):
    try:
        # Load and validate product
        print(f"Loading product from {product_path}")
        product = load_product_from_path(product_path)

        if validate_roi_intersection(product, wkt_roi):
            print("✅ Product intersects with ROI - proceeding with processing")
        else:
            print("❌ No intersection - stopping")
            product.dispose()
            return 1

        # Preprocessing steps
        print("Applying orbit file...")
        orbit_corrected = apply_orbit_file(product)
        print("Removing thermal noise...")
        noise_removed = remove_thermal_noise(orbit_corrected)
        print("Calibrating product...")
        calibrated = calibrate_product(noise_removed, polarization='DV')

        # Processing steps
        print("Applying speckle filter...")
        filtered = apply_speckle_filter(calibrated)
        print("Applying terrain correction...")
        terrain_corrected = terrain_correct(filtered, pixel_spacing=100.0)

        # Resolve subset ROI WKT
        try:
            import geombox
            print("Extracting subset WKT from geombox...")
            resolved_roi_wkt = geombox.get_geometry(wkt_roi, target_crs="EPSG:4326").wkt
        except ImportError:
            resolved_roi_wkt = wkt_roi

        print("Subsetting product...")
        subset_result = subset_product(terrain_corrected, resolved_roi_wkt)
        print("Converting to dB...")
        final_product = convert_to_db(subset_result)

        # Save result
        print(f"Writing output to {output_path}")
        ProductIO.writeProduct(final_product, output_path, 'GeoTIFF-BigTIFF')
        print(f"Processing complete: {output_path}")

        # Clean up memory
        product.dispose()
        print("Memory released")
        return 0
    except Exception as e:
        print(f"Error during processing: {e}")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Runs sentinel S1 sar processing to generate a terrain correction")
    parser.add_argument("--product_path", help="Input file to use", required=True)
    parser.add_argument("--wkt_roi", help="WKT ROI to subset", required=True)
    parser.add_argument("--output_file", help="Output file to write", required=True)

    args = parser.parse_args()

    exit_code = process(args.product_path, args.wkt_roi, args.output_file)
    if exit_code != 0:
        print(f"sentinel s1 failed with exit code: {exit_code}")
    sys.exit(exit_code)