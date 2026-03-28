'Set of functions related to the workflow that make use of FRENDY'

def GenerateUnperturbedNeutronACEFile(frendy_Path, 
                                      endf_Path, 
                                      temperature, 
                                      nuclide, 
                                      upgrade_Flag = False, 
                                      energy_grid = [], 
                                      cleanup_Flag = True):
    """ 
    Generates unperturbed neutron cross section ACE files for use in the workflow.

    Parameters:
        frendy_Path (str): Full path to the directory created by FRENDY during the installation process
            End of path should be '.../frendy_YYYYMMDD' where 'YYYYMMDD' corresponds to the date related to the version of FRENDY installed

        endf_Path (str): Full path to the ENDF evaluation for the nuclide of interest
            End of path should be '.../n-ZZZ_Y_AAA.endf' where ZZZ represents the three-digit Z number of the nuclide, Y the alphabetical name of the nuclide's element, and AAA the mass number of the nuclide
            If having difficulties, inputting as a raw string may assist

        temperature (int): Temperature at which to generate ACE file at
            Only one temperature can be specified per ACE file; creating multi-temperature libraries requires multiple ACE files for each nuclide at each temperature

        nuclide (str): Name of the nuclide whose ENDF evaluation will be used to generate an ACE file

        upgrade_Flag (Bool): Flag used to determine whether the ACE file will have additional energy grid points added to increase chances of successful data perturbations
            Default: False

        energy_grid (list or nd_array): Values of the energy grid used to determine perturbation bounds
            Should be the same as those corresponding to the retrieval of covariance data
            Default: Empty list ([])

        cleanup_Flag (Bool): Flag used to determine if automatic file cleanup will occur after completing the ACE file generation
            Deletes all intermediate files leaving the final ACE file as the only new file created.
            Default: True

    Results:
        output_file_path (str): Path to the unperturbed ACE file that was generated
    """

    'Import modules and internal functions'

    import os
    from FRENDYInternalFunctions import (formatENDFEvaluation,
                                         createUnperturbedACEGenerationInput)

    'Format the endf file into a .dat format'

    endf_file_dat = formatENDFEvaluation(endf_Path = endf_Path)

    'Write the input file for the ACE file generation'

    ace_file_gen_input_filename = createUnperturbedACEGenerationInput(frendy_Path = frendy_Path, 
                                                                      nuclide = nuclide, 
                                                                      endf_file_dat = endf_file_dat, 
                                                                      temperature = temperature, 
                                                                      upgrade_Flag = upgrade_Flag,
                                                                      energy_grid = energy_grid) 

    'Specifies the executable directory and the ACE file generation command'

    executable_directory = frendy_Path + '/frendy/main'

    run_command = './frendy.exe ' + str(ace_file_gen_input_filename)

    'Save the starting directory so that it can be returned to after FRENDY runs'

    starting_directory = os.getcwd()

    'Set the current directory to that of the FRENDY executable, and run the ACE file generation command'

    os.chdir(executable_directory)

    os.system(str(run_command))

    'Return to the starting directory after FRENDY runs'

    os.chdir(starting_directory)

    'First portion of the optional intermediate file cleanup'

    if cleanup_Flag:

        os.remove(endf_file_dat)

        os.remove(ace_file_gen_input_filename)

    'Specify output ACE file''s name for printing later, and perform any remaining file cleanup if need be'

    if upgrade_Flag: 

        output_file_path = executable_directory + '/' + str(nuclide) + '_upgrade.ace'

        if cleanup_Flag:

            os.remove(executable_directory + '/' +str(nuclide) + '_upgrade.ace.ace.dir')

            print('Intermediate Files Removed')

    else:

        output_file_path = executable_directory + '/' + str(nuclide) + '.ace'

        if cleanup_Flag:

            os.remove(executable_directory + '/' + str(nuclide) + '.ace.ace.dir')

            print('Intermediate Files Removed')

    'Check if the ACE file was successfully generated, and output the corresponding path'
    'Otherwise, give an error message'

    if os.path.exists(output_file_path):
        print('\n')
        print("ACE file successfully generated. The path to it is: " + str(output_file_path))
    else:
        print('\n')
        print("ACE file couldn''t generate; consult terminal output for assistance")

    return output_file_path


def GenerateDirectPerturbationACEFiles(frendy_Path, 
                                       unperturbed_ACE_file_path, 
                                       energy_grid, 
                                       mt_Number, 
                                       nuclide, 
                                       perturbation_coefficient, 
                                       cleanup_Flag = True):
    
    """
    Generates direct perturbation ACE files

    Parameters:

        frendy_Path (str): Full path to the directory created by FRENDY during the installation process
        End of path should be '.../frendy_YYYYMMDD' where 'YYYYMMDD' corresponds to the date related to the version of FRENDY installed

        unperturbed_ACE_file_path (str): Path to the unperturbed ACE file containing the cross section data for the nuclide of investigation

        energy_grid (list or nd_array): List of the energy bounds over which to perform perturbations [MeV]

        mt_Number (int): MT number of the reaction to be perturbed

        nuclide (str): Name of the nuclide whose ACE file will be perturbed

        perturbation_coefficient (float): Coefficient to multiple the cross section data over the energy intervals of interest by
        ex. 1.1 for a positive perturbation of 10%, or 0.80 for a negative perturbation of 20%

        cleanup_Flag (Bool): Flag used to determine is intermediate files will be deleted after all ACE files are created.
        Default value: True

    Results:
        perturbed_ace_folder_path (str): Directory where the direct perturbation ACE files are located
    """

    'Import necessary modules and functions'

    import os 
    import shutil
    from FRENDYInternalFunctions import (createDirectPerturbationInputs, 
                                         createDirectPerturbationList, 
                                         createDirectPerturbationCommandFile,
                                         directPerturbationFolderCheck)

    'Store the initial directory to return to after creating the ACE files'

    starting_directory = os.getcwd()

    'Set the current directory to that of FRENDY'

    os.chdir(frendy_Path)

    'Create a folder to store the directly perturbation ACE files'

    perturbed_ace_folder_path = frendy_Path + '/' + str(nuclide) + '_DirectPerturbationACEFiles_ReactionMT'
        
    perturbed_ace_folder_path += '_'
    perturbed_ace_folder_path += str(mt_Number)

    os.makedirs(perturbed_ace_folder_path)

    'Set the current directory to that of the folder for ease in file generation, execution, and cleanup'

    os.chdir(perturbed_ace_folder_path)

    'Create the direct perturbation input files'

    perturbation_list_lines, perturbation_input_folder_name = createDirectPerturbationInputs(nuclide = nuclide,
                                                                                             mt_Number = mt_Number,
                                                                                             energy_grid = energy_grid,
                                                                                             perturbation_coefficient = perturbation_coefficient)

    'Create a list of the direct perturbation input files'

    perturbation_list_filename = createDirectPerturbationList(nuclide = nuclide,
                                                              mt_Number = mt_Number,
                                                              perturbation_list_lines = perturbation_list_lines)

    'Create the execution file for the direct perturbations'

    create_ace_files_input_filename = createDirectPerturbationCommandFile(frendy_Path = frendy_Path,
                                                                          perturbation_list_filename = perturbation_list_filename,
                                                                          unperturbed_ACE_file_path = unperturbed_ACE_file_path)
    
    'Run the file generation command'

    file_generation_command = 'csh ./run_create_perturbed_ace_file.csh'

    os.system(file_generation_command)

    'Check if all of the files were created successfully based on the folder numbers they should be in'

    file_failure_flag = directPerturbationFolderCheck(perturbed_ace_folder_path = perturbed_ace_folder_path,
                                                      energy_grid = energy_grid)

    'Optional File Cleanup Section'

    if cleanup_Flag:
        os.remove(perturbation_list_filename)
        shutil.rmtree(perturbation_input_folder_name)
        os.remove(create_ace_files_input_filename)
        os.remove(perturbed_ace_folder_path + '/results.log')

        print('Intermediate Files Removed')

    'Return to the starting directory'

    os.chdir(starting_directory)

    'Display output message'
    
    if file_failure_flag:
        print("One or more ACE files failed to generate; consult outputs for details")
    else:
        print("All ACE files have successfully generated; they are located in: " + str(perturbed_ace_folder_path))
        return perturbed_ace_folder_path 

def GenerateRandomSamplingACEFiles(frendy_Path, 
                                   relative_covariance_matrix_path, 
                                   unperturbed_ACE_file_path, 
                                   energy_grid, 
                                   mt_Number, 
                                   nuclide, 
                                   seed = 1234567, 
                                   sample_size = 100, 
                                   cleanup_Flag = True):
    """
    Generates ACE files perturbed using randomly sampled perturbation coefficients

    Parameters:
        frendy_Path (str): Full path to the directory created by FRENDY during the installation process
        End of path should be '.../frendy_YYYYMMDD' where 'YYYYMMDD' corresponds to the date related to the version of FRENDY installed
    
        relative_covariance_matrix_path (str): Path to a .csv file with the relative covariance matrix data for the nuclide and reaction of interest.
        Must have been created using the same partitioning as in energy_grid

        unperturbed_ACE_file_path (str): Path to the unperturbed ACE file for the nuclide of interest

        energy_grid (list or nd_array): List of the energy bounds defining the energy ranges of perturbations [in MeV]

        mt_Number (int): MT number for the reaction of interest

        nuclide (str): Name of the nuclide of investigation
        Must be given without hyphens (e.g. H1 instead of H-1)

        seed (int): Seed for the random sampling algorithm used by FRENDY to generate the perturbation coefficients
        Default value: 1234567

        sample_size (int): Number of random sampling input files to create
        Default value: 100

        cleanup_Flag (Bool): Flag to determine if intermediate files will be deleted following the ACE file creation
        Default value: True

    Results:
        ace_files_directory (str): Directory where the random sampling ACE files are located
    """

    'Import modules'

    import os 
    import shutil
    from FRENDYInternalFunctions import (createRandomSamplingToolExecutionFile,
                                         createRandomSamplingToolInputs,
                                         generateRandomSamplingFactors,
                                         moveRandomSamplingFiles,
                                         createRandomSamplingPertList,
                                         createRandomSamplingACEDirectory,
                                         createRandomSamplingACEExecutionFile,
                                         randomSamplingFolderCheck)

    'Grab the starting directory to return to as need be'

    starting_directory = os.getcwd()

    'Retrieve the directory for the random sampling'

    random_sampling_tool_directory = frendy_Path + '/tools/make_perturbation_factor'

    executable_directory = random_sampling_tool_directory + '/make_perturbation_factor.exe'

    os.chdir(random_sampling_tool_directory)

    'Create the file used to execute the commands for generating the random sampling perturbation coefficients'

    execution_filename = createRandomSamplingToolExecutionFile(executable_directory = executable_directory,
                                                               random_sampling_tool_directory = random_sampling_tool_directory)

    'Create random sampling tool inputs'

    sample_filename = createRandomSamplingToolInputs(sample_size = sample_size,
                                                     seed = seed,
                                                     relative_covariance_matrix_path = relative_covariance_matrix_path,
                                                     energy_grid = energy_grid,
                                                     nuclide = nuclide,
                                                     mt_Number = mt_Number)

    'Generate the randomly sampled perturbation factors'

    generateRandomSamplingFactors(execution_filename = execution_filename,
                                  random_sampling_tool_directory = random_sampling_tool_directory,
                                  nuclide = nuclide,
                                  sample_filename = sample_filename,
                                  cleanup_Flag = cleanup_Flag)
    
    'Move the randomly sampled perturbation factors to the main FRENDY directory, and rename the associated folder'

    new_inputs_directory_name = moveRandomSamplingFiles(random_sampling_tool_directory = random_sampling_tool_directory,
                                                        nuclide = nuclide,
                                                        frendy_Path = frendy_Path,
                                                        mt_Number = mt_Number)

    'Move to the root FRENDY directory'

    os.chdir(frendy_Path)

    'Generate a file with a list of the random sampling inputs'

    perturbation_list_filename = createRandomSamplingPertList(nuclide = nuclide,
                                                              mt_Number = mt_Number,
                                                              new_inputs_directory_name = new_inputs_directory_name,
                                                              sample_size = sample_size)

    'Create a directory to store the random sampling ACE files, and move the inputs and perturbation list into it'

    ace_files_directory = createRandomSamplingACEDirectory(frendy_Path = frendy_Path,
                                                           nuclide = nuclide,
                                                           mt_Number = mt_Number,
                                                           perturbation_list_filename = perturbation_list_filename,
                                                           new_inputs_directory_name = new_inputs_directory_name)

    'Set the current directory to that where the randomly sampled ACE files will be stored'

    os.chdir(ace_files_directory)

    'Create the file with the commands to create the ACE files'

    create_ace_files_input_filename = createRandomSamplingACEExecutionFile(frendy_Path = frendy_Path,
                                                                           ace_files_directory = ace_files_directory,
                                                                           nuclide = nuclide, 
                                                                           mt_Number = mt_Number,
                                                                           unperturbed_ACE_file_path = unperturbed_ACE_file_path)

    'Run the command to generate the ACE files'

    random_sampling_file_command = 'csh ./' + str(create_ace_files_input_filename)

    os.system(random_sampling_file_command)

    'Check if all of the ACE files were created properly'

    file_failure_flag = randomSamplingFolderCheck(sample_size = sample_size,
                                                  ace_files_directory = ace_files_directory)


    'Optional File Cleanup Section'

    if cleanup_Flag:
        os.remove(perturbation_list_filename)
        shutil.rmtree(new_inputs_directory_name)
        os.remove(create_ace_files_input_filename)
        os.remove('results.log')

        print('Intermediate Files Removed')

    'Return to the starting directory'

    os.chdir(starting_directory)

    'Display outputs depending on completion status'

    if file_failure_flag == False:
        print('ACE files not generated successfully; check outputs for more information')
    else:
        print('All ACE files generated successfully and are located in: ' + str(ace_files_directory))
        return ace_files_directory

