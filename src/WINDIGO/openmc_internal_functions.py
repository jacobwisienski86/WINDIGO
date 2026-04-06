import os
import openmc
from pathlib import Path
import copy
import shutil


def count_directories(perturbed_ACE_folder_path):
    """
    Count the number of directories within the perturbed ACE files folder.

    Parameters
    ----------
    perturbed_ACE_folder_path : str
        Path to the directory where the folders containing the perturbed
        ACE files are located.

    Returns
    -------
    int
        Number of directories within the folder containing the perturbed
        ACE files. Directories containing perturbation inputs are excluded.
    """
    directory_number = 0

    for checked_directory in os.scandir(perturbed_ACE_folder_path):
        if 'input' in checked_directory.path.lower():
            continue
        if checked_directory.is_dir():
            directory_number += 1

    return directory_number


def create_numbers(directory_number):
    """
    Create a list of four-digit numbers corresponding to folders containing
    perturbed ACE files.

    Parameters
    ----------
    directory_number : int
        Number of directories, each containing a perturbed ACE file.

    Returns
    -------
    list of str
        Four-digit folder identifiers.
    """
    four_digit_numbers = []

    for ii in range(directory_number):
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
    Create a template data library containing unperturbed neutron cross
    section data.

    Parameters
    ----------
    neutron_sublibrary_path : str
        Path to directory containing unperturbed neutron .h5 files.

    unperturbed_nuclide_list : list of str
        Names of nuclides whose neutron cross sections are unperturbed.

    thermal_scatter_sublibrary_path : str
        Path to directory containing unperturbed thermal scattering .h5 files.

    unperturbed_TSL_list : list of str
        Names of thermal scattering libraries to include.

    Returns
    -------
    openmc.data.DataLibrary
        Data library containing all unperturbed cross section data.
    """
    unperturbed_library = openmc.data.DataLibrary()

    # Register neutron cross section files
    for nuclide in unperturbed_nuclide_list:
        for file in os.listdir(neutron_sublibrary_path):
            if nuclide in file and file.endswith(".h5"):
                xs_filename = f"{neutron_sublibrary_path}/{file}"
                unperturbed_library.register_file(xs_filename)

    #Check if thermal scattering data will be included in the model of interest
    if (thermal_scatter_sublibrary_path != '') and (unperturbed_TSL_list != []):
        # Register thermal scattering files
        for thermal_scatter in unperturbed_TSL_list:
            for file in os.listdir(thermal_scatter_sublibrary_path):
                if thermal_scatter in file and file.endswith(".h5"):
                    tsl_filename = f"{thermal_scatter_sublibrary_path}/{file}"
                    unperturbed_library.register_file(tsl_filename)
    else:
        print('No thermal scattering data will be included.')

    return unperturbed_library


def create_model_folders(
    directory_number,
    perturbed_nuclide,
    model_name,
    perturbation_type
):
    """
    Create folders to store perturbed cross_sections.xml files.

    Parameters
    ----------
    directory_number : int
        Number of directories containing perturbed ACE files.

    perturbed_nuclide : str
        Nuclide whose cross section data is being perturbed.

    model_name : str
        Name of the model under investigation.

    perturbation_type : str
        Type of perturbation performed.

    Returns
    -------
    perturbed_model_top_directory_name : str
        Name of the directory containing all perturbed model folders.

    perturbed_model_folder_list : list of str
        Paths to each folder containing a perturbed cross_sections.xml file.
    """
    perturbed_model_top_directory_name = (
        f"{model_name}_{perturbed_nuclide}_{perturbation_type}"
        "PerturbedModels"
    )

    # Remove existing directory if present
    if os.path.exists(perturbed_model_top_directory_name):
        shutil.rmtree(perturbed_model_top_directory_name)

    # Create top-level directory
    os.mkdir(perturbed_model_top_directory_name)

    perturbed_model_folder_list = []

    # Create subdirectories
    for number in range(directory_number):
        folder_name = f"Model_{number + 1}_Folder"
        folder_path = f"{perturbed_model_top_directory_name}/{folder_name}"
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
    Create cross_sections.xml files using perturbed ACE data.

    Parameters
    ----------
    unperturbed_library : openmc.data.DataLibrary
        Library containing unperturbed neutron cross section data.

    perturbed_ACE_folder_path : str
        Path to directory containing perturbed ACE files.

    four_digit_numbers : list of str
        Folder identifiers for perturbed ACE files.

    perturbed_model_folder_list : list of str
        Paths to folders where cross_sections.xml files will be stored.
    """
    starting_directory = os.getcwd()

    for ii in range(len(perturbed_model_folder_list)):
        os.chdir(perturbed_model_folder_list[ii])

        perturbed_data_folder = (
            f"{perturbed_ACE_folder_path}/{four_digit_numbers[ii]}"
        )

        # Identify ACE file
        for file in os.listdir(perturbed_data_folder):
            if (
                'xsdir' not in file
                and 'h5' not in file
                and 'ace' in file
            ):
                perturbed_ACE_file_path = f"{perturbed_data_folder}/{file}"
                break

        # Deep copy base library
        perturbed_xs_library = copy.deepcopy(unperturbed_library)

        # Convert ACE → HDF5
        perturbed_data = openmc.data.IncidentNeutron.from_ace(
            Path(perturbed_ACE_file_path)
        )

        h5_filename = f"{perturbed_ACE_file_path}.h5"

        # Remove existing .h5 file if present
        if os.path.exists(h5_filename):
            os.remove(h5_filename)

        perturbed_data.export_to_hdf5(h5_filename)

        # Register new HDF5 file
        perturbed_xs_library.register_file(h5_filename)

        # Export cross_sections.xml
        perturbed_xs_library.export_to_xml("cross_sections.xml")

        os.chdir(starting_directory)