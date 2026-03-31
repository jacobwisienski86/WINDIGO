def count_directories(perturbed_ACE_folder_path):
    """
    Count the number of directories within the perturbed ACE files folder
    of interest.

    Parameters:
        perturbed_ACE_folder_path (str): Path to the directory where the
        folders containing the perturbed ACE files are located.

    Results:
        directory_number (int): Number of directories within the folder
        containing the perturbed ACE files. Doesn't include a directory
        containing the perturbation inputs.
    """

    'Import needed modules'

    import os

    'Set a starting value for the directory number'

    directory_number = 0

    (
        "Count the number of directories within the folder containing the "
        "perturbed ACE files. Doesn't include directories containing inputs "
        "used to create ACE files."
    )

    for checked_directory in os.scandir(perturbed_ACE_folder_path):
    
        if 'input' in checked_directory.path.lower():
            continue
        if checked_directory.is_dir():
            directory_number += 1

    return directory_number


def create_numbers(directory_number):
    """
    Create a list of four-digit numbers corresponding to the folders
    containing each of the perturbed ACE files.

    Parameters:
        directory_number (int): Number of directories each containing a
        perturbed ACE file.

    Results:
        four_digit_numbers (list): List of four-digit numbers corresponding
        to the folders containing the perturbed ACE files.
    """

    'Set an initial empty list to add the numbers to'

    four_digit_numbers = []

    'Add the four digit numbers to the list'

    for ii in range(0, directory_number):
        number = str(ii + 1).zfill(4)
        four_digit_numbers.append(number)

    return four_digit_numbers


def create_unperturbed_library(
    neutron_sublibrary_path,
    unperturbed_nuclide_list,
    thermal_scatter_sublibrary_path,
    unperturbed_TSL_list
):
    """
    Creates a template data library containing the unperturbed neutron xs data.
    Assumes the unperturbed data is formatted in accordance with the .h5
    formatting used by premade OpenMC data libraries (e.g. H1.h5, U235.h5).

    Parameters:
        neutron_sublibrary_path (str): Path to the directory where the
        .h5-formatted unperturbed cross section data is located.

        unperturbed_nuclide_list (list): List of strings containing the names
        of nuclides whose neutron xs data won't be perturbed within the model.

        unperturbed_TSL_list (list): List containing strings with the names of
        each thermal scattering library to use within the model of interest.

        thermal_scatter_sublibrary_path (str): Path to the directory where the
        unperturbed .h5-formatted cross section data is stored.

    Results:
        unperturbed_library (openmc.data.DataLibrary): Data library containing
        all necessary xs data to run the model except for the perturbed xs data.
    """

    'Import needed modules'

    import os
    import openmc

    'Initial the data library'

    unperturbed_library = openmc.data.DataLibrary()

    'Register each unperturbed xs file with the data library'

    for nuclide in unperturbed_nuclide_list:
        for file in os.listdir(neutron_sublibrary_path):
            if nuclide in file and file.endswith(".h5"):
                xs_filename = neutron_sublibrary_path + '/' + file
                unperturbed_library.register_file(xs_filename)

    for thermal_scatter in unperturbed_TSL_list:
        for file in os.listdir(thermal_scatter_sublibrary_path):
            if thermal_scatter in file and file.endswith(".h5"):
                tsl_filename = thermal_scatter_sublibrary_path + '/' + file
                unperturbed_library.register_file(tsl_filename)

    return unperturbed_library


def create_model_folders(
    directory_number,
    perturbed_nuclide,
    model_name,
    perturbation_type
):
    """
    Create folders to store the perturbed cross_sections.xml files.

    Parameters:
        directory_number (int): Number of directories containing perturbed
        ACE files.

        perturbed_nuclide (str): Name of the nuclide whose cross section data
        is being perturbed.

        model_name (str): Model name under investigation.

        perturbation_type (str): Type of perturbation performed for the xs data.

    Results:
        perturbed_model_top_directory_name (str): Name of the directory where
        the folders containing the perturbed cross_sections.xml files are
        located.

        perturbed_model_folder_list (list): List with paths to each folder
        containing the perturbed cross_sections.xml files.
    """

    'Import needed modules'

    import os
    import shutil

    'Set the name of the directory where the folders will be located'

    perturbed_model_top_directory_name = (
        model_name + '_' + str(perturbed_nuclide) + '_' +
        str(perturbation_type) + 'PerturbedModels'
    )

    'Remove the perturbed model directory if it already exists'

    if os.path.exists(perturbed_model_top_directory_name):
        shutil.rmtree(perturbed_model_top_directory_name)

    'Create the directory to store the folders'

    os.mkdir(perturbed_model_top_directory_name)

    'Create a blank list that will store the folder paths'

    perturbed_model_folder_list = []

    (
        "Iterate over the number of directories, create folders to store the "
        "cross_sections.xml files, and add their paths to the list."
    )

    for number in range(0, directory_number):
        perturbed_model_folder_name = f'Model_{number + 1}_Folder'
        folder_path = (
            perturbed_model_top_directory_name + '/' +
            perturbed_model_folder_name
        )
        os.mkdir(folder_path)
        perturbed_model_folder_list.append(folder_path)

    return perturbed_model_top_directory_name, perturbed_model_folder_list


def create_perturbed_xml(
    unperturbed_library,
    perturbed_ACE_folder_path,
    four_digit_numbers,
    perturbed_model_folder_list
):
    """
    Create the cross_sections.xml files with the perturbed xs data that can be
    used to run the models.

    Parameters:
        unperturbed_library (openmc.data.DataLibrary): Data library containing
        the unperturbed neutron xs data.

        perturbed_ACE_folder_path (str): Path to the directory where the
        perturbed ACE files are located.

        four_digit_numbers (list): List of numbers corresponding to the folders
        containing the perturbed ACE files.

        perturbed_model_folder_list (list): List containing the names of the
        folders where the perturbed cross_sections.xml files will be stored.
    """

    'Import needed modules'

    import os
    import openmc
    from pathlib import Path
    import copy

    'Retrieve the starting directory'

    starting_directory = os.getcwd()

    'Iterate over each of the perturbed model folders'

    for ii in range(0, len(perturbed_model_folder_list)):

        'Set the current directory to the perturbed model folder'

        os.chdir(perturbed_model_folder_list[ii])

        'Grab the name of the folder containing a perturbed ACE file'

        perturbed_data_folder = (
            perturbed_ACE_folder_path + '/' + str(four_digit_numbers[ii])
        )

        'Retrieve the perturbed ACE file in the folder'

        for file in os.listdir(perturbed_data_folder):
            if ('xsdir' not in file) and ('h5' not in file) and ('.ace' in file):
                perturbed_ACE_file_path = perturbed_data_folder + '/' + file
            else:
                continue

        'Set a perturbed xs library using the unperturbed library as a template'

        perturbed_xs_library = copy.deepcopy(unperturbed_library)

        'Convert perturbed ACE file to .h5 format'

        perturbed_data = openmc.data.IncidentNeutron.from_ace(
            Path(perturbed_ACE_file_path)
        )

        h5_filename = perturbed_ACE_file_path + '.h5'

        'Delete .h5 file if one already exists'

        if os.path.exists(h5_filename):
            os.remove(h5_filename)

        perturbed_data.export_to_hdf5(h5_filename)

        'Register ACE file in xs_library'

        perturbed_xs_library.register_file(h5_filename)

        'Export library as cross_sections.xml file'

        perturbed_xs_library.export_to_xml('cross_sections.xml')

        os.chdir(starting_directory)
