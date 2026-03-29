'Functions related to functionality with OpenMC for WENDIGO'

def buildPerturbedCrossSectionsLibraries(unperturbed_nuclide_list, 
                                         neutron_sublibrary_path, 
                                         perturbed_ACE_folder_path,
                                         perturbed_nuclide = '', 
                                         model_name = ''):

    """
    Creates a directory with numbered folders, each containing a cross_sections.xml file created using perturbed cross section data

    Parameters:
        unperturbed_nuclide_list (list): List containing a list of strings with the names of the nuclides within the model of interest whose cross section data isn't being perturbed

        neutron_sublibrary_path (str): Path to the directory where the unperturbed .h5-formatted cross section data is stored

        perturbed_ACE_folder_path (str): Path to the directory where the folders containing the perturbed ACE files are located

        perturbed_nuclide (str): Optional name of the nuclide whose cross section data is being perturbed
        Only used to create more descriptive names for the directory containing the folders with the perturbed cross_sections.xml files
        Default value: Empty string ('')

        model_name (str): Optional name of the model under investigation
        Only used to create more descriptive names for the directory containing the folders with the perturbed cross_sections.xml files
        Default value: Empty string ('')

    Returns:
        perturbed_model_top_directory (str): Path to the directory containing the folders with the perturbed cross_sections.xml files
    """

    'Import needed functions'

    from OpenMCInternalFunctions import (countDirectories,
                                         createNumbers,
                                         createUnperturbedLibrary,
                                         createModelFolders,
                                         createPerturbedXML)

    'Count the number of directories within the perturbed ACE file folder'

    directory_number = countDirectories(perturbed_ACE_folder_path = perturbed_ACE_folder_path)

    'Creates a list of four digit numbers that can be used for creating folders containing the perturbed cross_section.xml files'

    four_digit_numbers = createNumbers(directory_number = directory_number)

    'Iterate through each unperturbed nuclide to create a base library that the perturbed files can be added onto'

    unperturbed_library = createUnperturbedLibrary(neutron_sublibrary_path = neutron_sublibrary_path,
                                                   unperturbed_nuclide_list = unperturbed_nuclide_list)

    'Generate folders to store each perturbed cross_sections.xml file in'

    perturbed_model_top_directory_name, perturbed_model_folder_list = createModelFolders(directory_number = directory_number,
                                                                                         perturbed_nuclide = perturbed_nuclide,
                                                                                         model_name = model_name)

    'Create the cross_sections.xml files using the perturbed ACE files'

    createPerturbedXML(unperturbed_library = unperturbed_library,
                       perturbed_ACE_folder_path = perturbed_ACE_folder_path,
                       four_digit_numbers = four_digit_numbers,
                       perturbed_model_folder_list = perturbed_model_folder_list)


    print('All perturbed cross_sections.xml files created. The folders containing them are located in: ' +str(perturbed_model_top_directory_name))

    return perturbed_model_top_directory_name

buildPerturbedCrossSectionsLibraries(unperturbed_nuclide_list = (['H2', 'H3', 'Li6', 'C12', 'U238']),
                                     neutron_sublibrary_path = r'/mnt/c/Users/jacob/endfb80/endfb-viii.0-hdf5/neutron',
                                     perturbed_ACE_folder_path = r'/mnt/c/Users/jacob/frendy_20241030/H1_DirectPerturbationACEFiles_ReactionMT_2',
                                     perturbed_nuclide = 'H1',
                                     model_name = 'Fusion')




                     
    
        




        
