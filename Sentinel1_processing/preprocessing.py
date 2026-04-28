"""SNAP preprocessing operations."""
from esa_snappy import HashMap, GPF, jpy

HashMap = jpy.get_type('java.util.HashMap')
GPF = jpy.get_type('org.esa.snap.core.gpf.GPF')


def apply_orbit_file(source):
    """Apply precise orbit file."""
    print('\tApplying orbit file...')
    parameters = HashMap()
    parameters.put('orbitType', 'Sentinel Precise (Auto Download)')
    parameters.put('polyDegree', '3')
    parameters.put('continueOnFail', False)
    return GPF.createProduct('Apply-Orbit-File', parameters, source)


def remove_thermal_noise(source):
    """Remove thermal noise."""
    print('\tRemoving thermal noise...')
    parameters = HashMap()
    parameters.put('removeThermalNoise', True)
    parameters.put('selectedPolarisations', 'VV,VH')
    return GPF.createProduct('ThermalNoiseRemoval', parameters, source)


def calibrate_product(source, polarization):
    """Calibrate to sigma0."""
    print('\tCalibrating...')
    parameters = HashMap()
    parameters.put('outputImageInComplex', False)
    parameters.put('outputBetaBand', False)
    parameters.put('outputGammaBand', False)
    parameters.put('outputSigmaBand', True)
    parameters.put('outputImageScaleInDb', False)
    
    # Polarization mapping
    pol_mapping = {
        'DH': ('Intensity_HH,Intensity_HV', 'HH,HV'),
        'DV': ('Intensity_VH,Intensity_VV', 'VH,VV'),
        'SH': ('Intensity_HH', 'HH'),
        'HH': ('Intensity_HH', 'HH'),
        'SV': ('Intensity_VV', 'VV'),
        'VV': ('Intensity_VV', 'VV')
    }
    
    if polarization in pol_mapping:
        source_bands, selected_pols = pol_mapping[polarization]
        parameters.put('sourceBands', source_bands)
        parameters.put('selectedPolarisations', selected_pols)
    
    return GPF.createProduct("Calibration", parameters, source)
