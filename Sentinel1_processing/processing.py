"""SNAP filtering and geometric operations."""

from esa_snappy import HashMap, GPF, jpy

HashMap = jpy.get_type('java.util.HashMap')
GPF = jpy.get_type('org.esa.snap.core.gpf.GPF')


def apply_speckle_filter(source):
    """Apply Lee Sigma speckle filter."""
    print('\tApplying speckle filtering...')
    parameters = HashMap()
    parameters.put('filter', 'Lee Sigma')
    parameters.put('windowSize', '7x7')
    parameters.put('sigmaStr', '0.9')
    parameters.put('targetWindowSizeStr', '3x3')
    parameters.put('numLooksStr', '1')
    return GPF.createProduct('Speckle-Filter', parameters, source)


def terrain_correct(source, pixel_spacing=10.0):
    """Apply terrain correction."""
    print('\tApplying terrain correction...')
    parameters = HashMap()
    parameters.put('demName', 'SRTM 1Sec HGT')
    parameters.put('demResamplingMethod', 'BILINEAR_INTERPOLATION')
    parameters.put('imgResamplingMethod', 'BILINEAR_INTERPOLATION')
    parameters.put('mapProjection', 'WGS84(DD)')
    parameters.put('pixelSpacingInMeter', float(pixel_spacing))
    parameters.put('saveProjectedLocalIncidenceAngle', False)
    parameters.put('saveSelectedSourceBand', True)
    parameters.put('nodataValueAtSea', True)
    return GPF.createProduct('Terrain-Correction', parameters, source)


def subset_product(source, wkt):
    """Subset product to ROI."""
    print('\tSubsetting...')
    parameters = HashMap()
    parameters.put('geoRegion', wkt)
    parameters.put('copyMetadata', True)
    return GPF.createProduct('Subset', parameters, source)


def convert_to_db(source):
    """Convert linear to dB."""
    print('\tConverting to dB...')
    parameters = HashMap()
    return GPF.createProduct('LinearToFromdB', parameters, source)
