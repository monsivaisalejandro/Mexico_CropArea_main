"""Product loading and validation utilities."""

from esa_snappy import ProductIO, PixelPos
from shapely.wkt import loads as load_wkt
from shapely.geometry import Polygon


def load_product_from_path(product_path):
    """Load Sentinel-1 product from file path."""
    product = ProductIO.readProduct(product_path)
    if not product:
        raise ValueError(f"Could not read product from: {product_path}")
    
    print(f"Product loaded: {product.getName()}")
    print(f"Dimensions: {product.getSceneRasterWidth()} x {product.getSceneRasterHeight()}")
    return product


def get_product_bounds(product):
    """Extract geographic bounds from product."""
    w = product.getSceneRasterWidth()
    h = product.getSceneRasterHeight()
    gc = product.getSceneGeoCoding()
    
    if gc is None:
        return None

    coords = []
    for x, y in [(0, 0), (w, 0), (w, h), (0, h)]:
        pix_pos = PixelPos(float(x), float(y))
        geo_pos = gc.getGeoPos(pix_pos, None)
        coords.append((geo_pos.getLon(), geo_pos.getLat()))
    
    return coords


def validate_roi_intersection(product, wkt_roi):
    """Validate if WKT ROI intersects with product bounds."""
    print("Validating geographic bounds...")
    
    product_coords = get_product_bounds(product)
    if not product_coords:
        print("❌ Product has no geocoding information.")
        return False

    try:
        product_poly = Polygon(product_coords)
        roi_poly = load_wkt(wkt_roi)
        
        if product_poly.intersects(roi_poly):
            intersection_area = product_poly.intersection(roi_poly).area
            coverage = (intersection_area / roi_poly.area) * 100
            print(f"✅ Intersection detected. Product covers {coverage:.2f}% of ROI.")
            return True
        else:
            print("⚠️ ROI is completely outside this product.")
            return False
            
    except Exception as e:
        print(f"❌ Error validating ROI: {e}")
        return False
