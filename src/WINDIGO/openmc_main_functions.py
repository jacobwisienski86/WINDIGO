# Functions related to functionality with OpenMC for WINDIGO

from .openmc_internal_functions import (
    count_directories,
    create_numbers,
    create_unperturbed_library,
    create_model_folders,
    create_perturbed_xml,
)


def build_perturbed_cross_sections_libraries(
    unperturbed_nuclide_list,
    neutron_sublibrary_path,
    perturbed_ACE_folder_path,
    unperturbed_TSL_list = [],
    thermal_scatter_sublibrary_path = '',
    perturbed_nuclide='',
    model_name='',
    perturbation_type=''
):
    """
    Create a directory with numbered folders, each containing a
    cross_sections.xml file created using perturbed cross section data.

    Parameters
    ----------
    unperturbed_nuclide_list : list of str
        Names of nuclides whose cross section data is unperturbed.

    neutron_sublibrary_path : str
        Path to directory containing unperturbed neutron .h5 files.

    perturbed_ACE_folder_path : str
        Path to directory containing folders with perturbed ACE files.

    unperturbed_TSL_list : list of str, optional
        Names of thermal scattering libraries to include.

    thermal_scatter_sublibrary_path : str, optional
        Path to directory containing unperturbed thermal scattering .h5 files.

    perturbed_nuclide : str, optional
        Name of the nuclide being perturbed. Used only for naming folders.

    model_name : str, optional
        Name of the model under investigation. Used only for naming folders.

    perturbation_type : str, optional
        Type of perturbation (e.g., direct, random). Used only for naming
        folders.

    Returns
    -------
    str
        Path to the directory containing all perturbed cross_sections.xml files.
    """
    # Count directories containing perturbed ACE files
    directory_number = count_directories(
        perturbed_ACE_folder_path=perturbed_ACE_folder_path
    )

    # Create four-digit folder identifiers
    four_digit_numbers = create_numbers(directory_number=directory_number)

    # Create unperturbed base library
    unperturbed_library = create_unperturbed_library(
        neutron_sublibrary_path=neutron_sublibrary_path,
        unperturbed_nuclide_list=unperturbed_nuclide_list,
        unperturbed_TSL_list=unperturbed_TSL_list,
        thermal_scatter_sublibrary_path=thermal_scatter_sublibrary_path
    )

    # Create folders for perturbed cross_sections.xml files
    (
        perturbed_model_top_directory_name,
        perturbed_model_folder_list
    ) = create_model_folders(
        directory_number=directory_number,
        perturbed_nuclide=perturbed_nuclide,
        model_name=model_name,
        perturbation_type=perturbation_type
    )

    # Generate perturbed cross_sections.xml files
    create_perturbed_xml(
        unperturbed_library=unperturbed_library,
        perturbed_ACE_folder_path=perturbed_ACE_folder_path,
        four_digit_numbers=four_digit_numbers,
        perturbed_model_folder_list=perturbed_model_folder_list
    )

    print(
        "All perturbed cross_sections.xml files created. The folders "
        "containing them are located in: "
        f"{perturbed_model_top_directory_name}"
    )

    return perturbed_model_top_directory_name