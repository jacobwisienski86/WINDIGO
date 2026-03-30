# Functions related to functionality with OpenMC for WENDIGO

def build_perturbed_cross_sections_libraries(
    unperturbed_nuclide_list,
    neutron_sublibrary_path,
    unperturbed_TSL_list,
    thermal_scatter_sublibrary_path,
    perturbed_ACE_folder_path,
    perturbed_nuclide='',
    model_name='',
    perturbation_type=''
):
    """
    Creates a directory with numbered folders, each containing a
    cross_sections.xml file created using perturbed cross section data.

    Parameters:
        unperturbed_nuclide_list (list): List containing a list of strings with
        the names of the nuclides within the model of interest whose cross
        section data isn't being perturbed.

        neutron_sublibrary_path (str): Path to the directory where the
        unperturbed .h5-formatted cross section data is stored.

        unperturbed_TSL_list (list): List containing a list of strings with the
        names of each of the thermal scattering libraries to use within the
        model of interest. For example, when analyzing BeO this may be
        ['c_Be_in_BeO', 'c_O_in_BeO'].

        thermal_scatter_sublibrary_path (str): Path to the directory where the
        unperturbed .h5-formatted cross section data is stored. May be the same
        as neutron_sublibrary_path depending on where cross section data was
        downloaded from.

        perturbed_ACE_folder_path (str): Path to the directory where the folders
        containing the perturbed ACE files are located.

        perturbed_nuclide (str): Optional name of the nuclide whose cross
        section data is being perturbed. Only used to create more descriptive
        names for the directory containing the folders with the perturbed
        cross_sections.xml files. Default value: ''.

        model_name (str): Optional name of the model under investigation. Only
        used to create more descriptive names for the directory containing the
        folders with the perturbed cross_sections.xml files. Default value: ''.

        perturbation_type (str): Optional input to state if the models are using
        direct perturbation or random sampling ACE files. Only used to create
        more descriptive names for the directory containing the folders with the
        perturbed cross_sections.xml files. Default value: ''.

    Returns:
        perturbed_model_top_directory (str): Path to the directory containing
        the folders with the perturbed cross_sections.xml files.
    """

    'Import needed functions'

    from OpenMCInternalFunctions import (
        count_directories,
        create_numbers,
        create_unperturbed_library,
        create_model_folders,
        create_perturbed_xml
    )
    from pathlib import Path

    'Count the number of directories within the perturbed ACE file folder'

    directory_number = count_directories(
        perturbed_ACE_folder_path=perturbed_ACE_folder_path
    )

    'Creates a list of four digit numbers for folder creation'

    four_digit_numbers = create_numbers(directory_number=directory_number)

    'Iterate through each unperturbed nuclide to create a base library'

    unperturbed_library = create_unperturbed_library(
        neutron_sublibrary_path=neutron_sublibrary_path,
        unperturbed_nuclide_list=unperturbed_nuclide_list,
        unperturbed_TSL_list=unperturbed_TSL_list,
        thermal_scatter_sublibrary_path=thermal_scatter_sublibrary_path
    )

    'Generate folders to store each perturbed cross_sections.xml file'

    (
        perturbed_model_top_directory_name,
        perturbed_model_folder_list
    ) = create_model_folders(
        directory_number=directory_number,
        perturbed_nuclide=perturbed_nuclide,
        model_name=model_name,
        perturbation_type=perturbation_type
    )

    'Create the cross_sections.xml files using the perturbed ACE files'

    create_perturbed_xml(
        unperturbed_library=unperturbed_library,
        perturbed_ACE_folder_path=perturbed_ACE_folder_path,
        four_digit_numbers=four_digit_numbers,
        perturbed_model_folder_list=perturbed_model_folder_list
    )

    print(
        'All perturbed cross_sections.xml files created. The folders '
        'containing them are located in: '
        + str(perturbed_model_top_directory_name)
    )

    return perturbed_model_top_directory_name
