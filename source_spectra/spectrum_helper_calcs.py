import numpy as np

def find_index_of_max(var_array):
    idx = np.argmax(var_array, axis=0)
    return idx

def find_index_of_nearest(var_array, value):
    idx = (np.abs(var_array-value)).argmin()
    return idx

def find_FWHM_indices(var_array):
    '''
    Assumes var_array is normalized. 
    '''
    idx_peak = find_index_of_max(var_array)
    idx_low = find_index_of_nearest(var_array[0:idx_peak], 0.5)
    idx_high = idx_peak + find_index_of_nearest(var_array[idx_peak:-1], 0.5)
    return (idx_low, idx_high)

def calc_FWHM_nm(wavelengths_and_spectrum_values):
    indices = find_FWHM_indices(wavelengths_and_spectrum_values[:,1])
    return wavelengths_and_spectrum_values[indices[1], 0] - wavelengths_and_spectrum_values[indices[0], 0]