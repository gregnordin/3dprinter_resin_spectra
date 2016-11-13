import numpy as np
import matplotlib.pyplot as plt
import os

def makename(datadirectory,filename):
    return os.path.join(datadirectory,filename)

def get_list_of_materials(datadirectory):
    results = []
    for r in os.listdir(datadirectory):
        if r.startswith('dark'):
            pass
        elif r.startswith('.'):
            pass
        else:
            results.append(r)
    return results

def read_and_calc_ave_spectral_data(datadirectory, filenames, start_index, end_index):
    """
    Read data from files in input list and return array with columns for wavelength, ave, std
    """
    num_pnts_in_spectrum, num_data_files = (end_index-start_index), len(filenames)
    data_all = np.zeros(shape=(num_pnts_in_spectrum, num_data_files))
    for i, f in enumerate(filenames):
        print(i, f)
        temp_data = np.loadtxt(makename(datadirectory, f), delimiter=' ')
        data_all[:,i] = temp_data[1,start_index:end_index]
        if i is 0:
            wavelengths = temp_data[0,start_index:end_index]
    ave = np.mean(data_all, axis=1)
    std = np.std(data_all, axis=1)
    return np.array([wavelengths, ave, std]).T

def get_list_of_processed_dark_data_files(datadirectory):
    list_of_dark_data = []
    for f in os.listdir(datadirectory):
        if f.startswith('dark'):
            list_of_dark_data.append(f)
    return list_of_dark_data

def get_list_of_dark_data(datadirectory):
    list_of_directories = []
    for d in os.listdir(datadirectory):
        if os.path.isdir(makename(datadirectory,d)):
            if d.startswith('dark'):
                list_of_directories.append(d)
    return list_of_directories

def process_dark_data(dark_data_directory_path, start_index, end_index):
    '''
    Calculate average dark data for data files in specified directory.
    
    Arguments:
        dark_data_directory_path - full relative path to dark data directory
        start_index, end_index - range of data to use
    '''
    print(dark_data_directory_path)
    files = get_list_of_all_data_file_names(dark_data_directory_path)
    print(files)
    return read_and_calc_ave_spectral_data(dark_data_directory_path, files, start_index, end_index)

def process_and_save_dark_data(raw_data_directory, dark_data_directory, processed_data_directory, 
                               params_for_dark_data):
    '''
    Calculate average dark data for data files in specified directory and save to csv file.
    
    Arguments:
        raw_data_directory - relative path to raw data directory
        dark_data_directory - name of dark data directory in raw_data_directory
        params_for_dark_data - dict with start_index, end_index (both mandatory), and any other desired parameters
            start_index, end_index - range of data to use
    '''
    print(makename(raw_data_directory,dark_data_directory))
    result = process_dark_data(makename(raw_data_directory,dark_data_directory), 
                               params_for_dark_data['start_index'], 
                               params_for_dark_data['end_index'])
    temp_name = makename(processed_data_directory, dark_data_directory+'.csv')
    np.savetxt(temp_name, result, delimiter=',', header=str(params_for_dark_data))
    return temp_name

def get_processed_data_from_file(path_to_file):
    '''
    Retrieve processed spectrum data from specified file which can optionally have
    one comment line as the first line in the file.
    
    Arguments:
        path_to_file - relative path (including name) to processed data file
    
    Returns:
        header string - None if there is no header string
        numpy array with data. Columns are wavelength, spectrum, and (optionally) standard deviation
    '''
    # Read header lines
    header = []
    with open(path_to_file) as f:
        line = f.readline()
        li=line.strip()
        if li.startswith('#'):
            header = li[2:]
        else:
            header = None
    # Read the rest of the file
    data = np.loadtxt(path_to_file, delimiter=',', dtype=float)
    return header, data


def get_list_of_all_data_file_names(datadirectory):
    """
    Return list of all data files (.txt) in specified directory
    """
    print('get_list_of_all_data_file_names', datadirectory)
    list_of_files = []
    for file in os.listdir(datadirectory):
        if file.endswith('txt'):
            list_of_files.append(file)
    return list_of_files

def sort_resin_noresin_file_names(names):
    '''
    Sort filenames into two lists: resin and no resin cases
    '''
    resin = []
    noresin = []
    for n in names:
        if n.startswith("meas_"):
            resin.append(n)
        else:
            noresin.append(n)
    return resin, noresin

def process_data_to_get_absorbance(datadirectory, dark_data, start_index, end_index):
    # Prepare file names
    files = get_list_of_all_data_file_names(datadirectory)
    resin_files, noresin_files = sort_resin_noresin_file_names(files)
    # Calculate dark-corrected resin data
    resin = read_and_calc_ave_spectral_data(datadirectory, resin_files, start_index, end_index)
    resin[:,1] -= dark_data[:,1]  # subtract dark data
    # Calculate dark-corrected noresin data
    noresin = read_and_calc_ave_spectral_data(datadirectory, noresin_files, start_index, end_index)
    noresin[:,1] -= dark_data[:,1]  # subtract dark data
    # Calculate absorbance
    data = np.zeros(shape=(resin.shape[0], 2))
    data[:,0] = resin[:,0] # Copy wavelengths
    data[:,1] = -np.log10(resin[:,1]/noresin[:,1])
    return data

def write_processed_data_to_file(filename_with_path, data, comment_line=''):
    '''
    Write data to csv file optional comment line as first line
    '''
    np.savetxt(filename_with_path, data, delimiter=',', header=comment_line)

    