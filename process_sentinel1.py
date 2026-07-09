"""Main Sentinel-1 processing pipeline."""

import sys
import traceback
from esa_snappy import ProductIO

from Sentinel1_processing.product_loader import load_product_from_path, validate_roi_intersection
from Sentinel1_processing.preprocessing import apply_orbit_file, remove_thermal_noise, calibrate_product
from Sentinel1_processing.processing import apply_speckle_filter, terrain_correct, subset_product, convert_to_db


def process_sentinel1_product(product_path, wkt_roi, output_path, pixel_spacing=100.0):
    """
    Complete Sentinel-1 processing pipeline.
    
    Args:
        product_path: Path to Sentinel-1 product
        wkt_roi: WKT string defining region of interest
        output_path: Output file path
        pixel_spacing: Output pixel spacing in meters
    """
    product = None
    
    try:
        # Load and validate product
        product = load_product_from_path(product_path)
        
        if not validate_roi_intersection(product, wkt_roi):
            print("Skipping processing - no ROI intersection")
            return False
        
        print(f"Processing: {product.getName()}")
        
        # Preprocessing chain
        orbit_corrected = apply_orbit_file(product)
        noise_removed = remove_thermal_noise(orbit_corrected)
        calibrated = calibrate_product(noise_removed, polarization='DV')
        filtered = apply_speckle_filter(calibrated)
        
        # Geometric processing
        terrain_corrected = terrain_correct(filtered, pixel_spacing)
        
        # Resolve subset ROI WKT
        try:
            import geombox
            print("Extracting subset WKT from geombox...")
            resolved_roi_wkt = geombox.get_geometry(wkt_roi, target_crs="EPSG:4326").wkt
        except ImportError:
            resolved_roi_wkt = wkt_roi

        subset_result = subset_product(terrain_corrected, resolved_roi_wkt)
        final_product = convert_to_db(subset_result)
        
        # Save result
        print(f"Saving to: {output_path}")
        ProductIO.writeProduct(final_product, output_path, 'GeoTIFF-BigTIFF')
        
        return True
        
    except Exception as e:
        print(f"Processing error: {e}")
        traceback.print_exc()
        return False
        
    finally:
        if product:
            product.dispose()
            print("Memory released")


def main():
    if len(sys.argv) < 4:
        print("Usage: python process_sentinel1.py <product_path> <wkt_roi> <output_path>")
        sys.exit(1)
    
    product_path = sys.argv[1]
    wkt_roi = sys.argv[2]
    output_path = sys.argv[3]
    
    success = process_sentinel1_product(product_path, wkt_roi, output_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
