'Set of internal functions involving FRENDY related to the uncertainty quantification workflow'
'Not intended to be called directly when using the workflow'

'Functions related to generating unperturbed ACE files'

def formatENDFEvaluation(endf_Path):
    """
    Formats the raw ENDF evaluation into a .dat format needed for use by FRENDY

    Parameters:
        endf_Path (str): Path to the endf evaluation that will be used to create an unperturbed ACE file

    Results:
        endf_file_dat (str): Path to the .dat formatted endf evaluation
    """

    'Import modules'

    import shutil

    'Create a .dat file to use for the ACE file generation'

    endf_file_original = endf_Path

    endf_file_intermediate = endf_file_original[:-5]

    endf_file_dat = str(endf_file_intermediate) + '.dat'

    shutil.copy2(endf_file_original, endf_file_dat)

    return endf_file_dat

def writeUpgradeLines(energy_grid):

    """
    Writes optional lines to include within the unperturbed ACE file generation input file
    to add more energy grid points.

    Parameters: 
        energy_grid (list or nd_array): Energy bounds that will be used to perform perturbations for either the direct
        perturbation or random sampling methodologies.

    Results:
        upgrade_lines (list): List of text lines that can be added to the unperturbed ACE file generation
        input file to add additional energy grid points
    """

    upgrade_lines = []

    'Generates a list of the extra energy bounds to add to the input file'

    upgrade_energy_bounds = []

    for ii in range(0, len(energy_grid)):

        if (energy_grid[ii] < 99.99):

            if ii == 0:

                upgrade_energy_bounds.append(energy_grid[ii] + (1E-6))

            elif ii == (len(energy_grid) - 1):

                upgrade_energy_bounds.append(energy_grid[ii] - (1E-6))

            else:

                upgrade_energy_bounds.append(energy_grid[ii] - (1E-6))

                upgrade_energy_bounds.append(energy_grid[ii] + (1E-6))
        
        elif (energy_grid[ii] >= 99.99) and (energy_grid[ii] < 99990):

            if ii == 0:

                upgrade_energy_bounds.append(energy_grid[ii] + 0.1)

            elif ii == (len(energy_grid) - 1):

                upgrade_energy_bounds.append(energy_grid[ii] - 0.1)

            else:

                upgrade_energy_bounds.append(energy_grid[ii] - 0.1)

                upgrade_energy_bounds.append(energy_grid[ii] + 0.1)

        else:

            if ii == 0:

                upgrade_energy_bounds.append(energy_grid[ii] + 1000)

            elif ii == (len(energy_grid) - 1):

                upgrade_energy_bounds.append(energy_grid[ii] - 1000)

            else:

                upgrade_energy_bounds.append(energy_grid[ii] - 1000)

                upgrade_energy_bounds.append(energy_grid[ii] + 1000)

    'Lines that specify the additional energy grid points to add in the ACE file generation'
            
    for jj in range(0, len(upgrade_energy_bounds)):

        if jj == 0:
            
            upgraded_bound_line = '    add_grid_data    (' + str(upgrade_energy_bounds[jj]) + '\n'

            upgrade_lines.append(upgraded_bound_line)
        
        elif jj == (len(upgrade_energy_bounds) - 1):

            upgraded_bound_line = '        ' + str(upgrade_energy_bounds[jj]) + ')\n'

            upgrade_lines.append(upgraded_bound_line)

        else:

            upgraded_bound_line = '        ' + str(upgrade_energy_bounds[jj]) + '\n'

            upgrade_lines.append(upgraded_bound_line)

    return upgrade_lines

def createUnperturbedACEGenerationInput(frendy_Path, 
                                        nuclide, 
                                        endf_file_dat, 
                                        temperature, 
                                        upgrade_Flag = False, 
                                        energy_grid = []):

    """
    Writes the input file used to generate the unperturbed ACE files

    Parameters:
        frendy_Path (str): Full path to the directory created by FRENDY during the installation process
        End of path should be '.../frendy_YYYYMMDD' where 'YYYYMMDD' corresponds to the date related to the version of FRENDY installed

    Results:
        ace_file_gen_input_filename (str): Path to the file that is ran to generate the unperturbed ACE file
    """

    'Generate the input file to be run by FRENDY'

    ace_file_gen_input_filename = str(frendy_Path) + '/frendy/main/' + str(nuclide) + '_acegenerator'

    'Modify input file name based on if upgrades are specified'

    if upgrade_Flag:
        ace_file_gen_input_filename += '_upgrade.dat'
    else:
        ace_file_gen_input_filename += '_normal.dat'

    ace_file_lines = []

    'Line specifying ACE file generation mode'

    file_gen_type_line = 'ace_file_generation_fast_mode\n'

    ace_file_lines.append(file_gen_type_line)

    'Line specifying where to find the nuclear data used to create the file'

    nucl_data_file_line = '    nucl_file_name    ' + str(endf_file_dat) + '\n'

    ace_file_lines.append(nucl_data_file_line)

    'Line specifying the temperature to generate ACE file at'

    temp_line = '    temp    ' + str(temperature) + '\n'

    ace_file_lines.append(temp_line)

    'Line specifying outputted ACE file''s name'

    if upgrade_Flag: 
        ace_file_output_name_line = '    ace_file_name    ' + str(nuclide) + '_upgrade.ace\n'
    else:
        ace_file_output_name_line = '    ace_file_name    ' + str(nuclide) + '.ace\n'

    ace_file_lines.append(ace_file_output_name_line)

    'Section that performs the energy grid upgrade'

    if upgrade_Flag:
        upgrade_lines = writeUpgradeLines(energy_grid = energy_grid)
        ace_file_lines.append(upgrade_lines)

    'Write the ace file generation input'

    with open(ace_file_gen_input_filename, 'w') as file:

        file.writelines(ace_file_lines)

        file.close()

    print('The path to the ace file generation input is: ' + str(ace_file_gen_input_filename) + '\n')

    return ace_file_gen_input_filename

'Functions related to generating direct perturbation ACE files'

def createDirectPerturbationInputs(nuclide, 
                                   mt_Number, 
                                   energy_grid,
                                   perturbation_coefficient):
    """
    Creates a folder to store the direct perturbation inputs, generates the inputs, and writes the names of the inputs to a list

    Parameters:
        nuclide (str): Name of the nuclide whose ACE file will be perturbed

        mt_Number (int): MT number of the reaction to be perturbed

        energy_grid (list or nd_array): List of the energy bounds over which to perform perturbations [MeV]

        perturbation_coefficient (float): Coefficient to multiple the cross section data over the energy intervals of interest by
        ex. 1.1 for a positive perturbation of 10%, or 0.80 for a negative perturbation of 20%

    Results:
        perturbation_list_lines (list): List of lines containing the names of each of the direct perturbation
        input files

        perturbation_input_folder_name (str): Directory where the direct perturbation input files are located

    """

    'Import needed modules'

    import os

    'Create a folder to store the perturbation input files'

    perturbation_input_folder_name = str(nuclide) + '_DirectPerturbationInputs_ReactionMT'
        
    perturbation_input_folder_name += '_'
    perturbation_input_folder_name += str(mt_Number)

    os.mkdir(perturbation_input_folder_name)

    'Create a blank list to store the names of direct perturbation inputs'

    perturbation_list_lines = []

    'Generate the direct perturbation inputs, and store their names in a list'

    for ii in range(0, len(energy_grid)-1):
        if ii < 9:
            perturbation_input_file_name = perturbation_input_folder_name + '/' + str(nuclide) + f"_000{ii+1}"

            input_file_line = perturbation_input_file_name + '\n'

            perturbation_list_lines.append(input_file_line)
        
        elif (ii>=9) and (ii<=98):
            perturbation_input_file_name = perturbation_input_folder_name + '/' + str(nuclide) + f"_00{ii+1}" 

            input_file_line = perturbation_input_file_name + '\n'

            perturbation_list_lines.append(input_file_line)

        else:
            perturbation_input_file_name = perturbation_input_folder_name + '/' + str(nuclide) + f"_0{ii+1}"

            input_file_line = perturbation_input_file_name + '\n'

            perturbation_list_lines.append(input_file_line)

        with open(perturbation_input_file_name, 'w') as file:
            file.write(str(mt_Number) + '     ' + str(energy_grid[ii]) + '     ' + str(energy_grid[ii+1]) + '     ' + str(perturbation_coefficient))
            file.close()

    return perturbation_list_lines, perturbation_input_folder_name

def createDirectPerturbationList(nuclide, 
                                 mt_Number,
                                 perturbation_list_lines):
    """ 
    Creates a file with a list of the direct perturbation input files

    Parameters:
        nuclide (str): Name of the nuclide whose ACE file is being perturbed

        mt_Number (int): MT number of the reaction being perturbed

        perturbation_list_lines (list): List of lines specifying the names of the direct perturbation input files

    Results:
        perturbation_list_filename (str): Name of the file containing the list of direct perturbation input files
    """

    perturbation_list_filename = 'perturbation_list_' + str(nuclide) + '_MT' 

    perturbation_list_filename += '_'
    perturbation_list_filename += str(mt_Number)

    perturbation_list_filename += 'Direct.inp'

    with open(perturbation_list_filename, 'w') as file:
        file.writelines(perturbation_list_lines)
        file.close()
    
    return perturbation_list_filename

def createDirectPerturbationCommandFile(frendy_Path, 
                                        perturbation_list_filename, 
                                        unperturbed_ACE_file_path):
    """  
    Creates a .csh file with the commands and inputs to create the direct perturbation ACE files
    
    Parameters:
        frendy_Path (str): Full path to the directory created by FRENDY during the installation process
        End of path should be '.../frendy_YYYYMMDD' where 'YYYYMMDD' corresponds to the date related to the version of FRENDY installed

        perturbation_list_filename (str): Name of the file containing the list of direct perturbation input files

        unperturbed_ACE_file_path (str): Path to the unperturbed ACE file for the nuclide of interest
    
    Results:
        create_ace_files_input_filename (str): Path to the file containing the commands used to generated the direct perturbation ACE files
    """

    'Generate the input file to perform the direct perturbations'
    'Some of the lines help to produce an output log that may be useful for debugging; make sure cleanup_Flag is set to False so to ensure it isn''t deleted'

    create_ace_files_input_filename = 'run_create_perturbed_ace_file.csh'

    input_file_lines = []

    space_line ='\n'

    first_line = '#!/bin/csh\n'
    input_file_lines.append(first_line)
    input_file_lines.append(space_line)

    executable_line = 'set EXE     = ' + str(frendy_Path) + '/tools/perturbation_ace_file/perturbation_ace_file.exe'
    input_file_lines.append(executable_line)
    input_file_lines.append(space_line)

    perturbation_list_line = 'set INP     = ' + str(perturbation_list_filename)
    input_file_lines.append(perturbation_list_line)
    input_file_lines.append(space_line)

    unperturbed_ace_file_line = 'set ACE     = ' + str(unperturbed_ACE_file_path)
    input_file_lines.append(unperturbed_ace_file_line)
    input_file_lines.append(space_line)

    output_log_line1 = 'set LOG = results.log\n'
    input_file_lines.append(output_log_line1)

    output_log_line2 = 'echo "${EXE}  ${ACE}  ${INP}"      > ${LOG}\n'
    input_file_lines.append(output_log_line2)

    output_log_line3 = 'echo ""                           >> ${LOG}\n'
    input_file_lines.append(output_log_line3)

    running_command_line = '${EXE}  ${ACE}  ${INP} >> ${LOG}\n'
    input_file_lines.append(running_command_line)

    with open(create_ace_files_input_filename, 'w') as file:
        file.writelines(input_file_lines)
        file.close()

    return create_ace_files_input_filename 

def directPerturbationFolderCheck(perturbed_ace_folder_path,
                                  energy_grid):
    """
    Checks that all direct perturbation ACE files were created by checking if their expected folders exist

    Parameters:
        perturbed_ace_folder_path (str): Path to the directory where the direct perturbation ACE files are stored

        energy_grid (list or nd_array): Energy bounds where the perturbations will be performed 

    Results:
        file_failure_flag (Bool): Flag used to indicate if all ACE files were generated properly
    """

    'Import needed modules'

    import os

    file_failure_flag = False

    for ii in range(0, len(energy_grid)-1):
        if ii < 9:
            folder_to_check = perturbed_ace_folder_path + f"/000{ii+1}"

        elif (ii>=9) and (ii<=98):
            folder_to_check = perturbed_ace_folder_path + f"/00{ii+1}"

        else:
            folder_to_check = perturbed_ace_folder_path + f"/0{ii+1}"
        
        if os.path.exists(folder_to_check):
            continue
        else:
            file_failure_flag = True
            break

        return file_failure_flag 

'Functions related to generated random sampling ACE files'

def createRandomSamplingToolExecutionFile(executable_directory,
                                          random_sampling_tool_directory):

    """
    Creates the file needed to execute the random sampling tool

    Parameters:
        executable_directory (str): Path to the random sampling tool executable

        random_sampling_tool_directory (str): Directory where the random sampling tool executable within

    Results:
        execution_filename (str): Path to the file with the commands for running the random sampling tool executable

    """

    'Set up the execution file'

    execution_filename = 'run_make_perturbation_factor.csh'

    executable_lines = []

    first_line = '#!/bin/csh\n'

    linespace = '\n'

    executable_lines.append(first_line)
    executable_lines.append(linespace)

    executor_line = 'set EXE     = ' + str(executable_directory) + '\n'

    executable_lines.append(executor_line)
    executable_lines.append(linespace)

    input_line = 'set INP        = ' + str(random_sampling_tool_directory) + '/sample_copy.inp'  

    executable_lines.append(input_line)
    executable_lines.append(linespace)
    executable_lines.append(linespace)

    log_line1 = 'set LOG = result.log\n'

    executable_lines.append(log_line1)

    log_line2 = 'echo "${EXE}  ${INP}"      > ${LOG}\n'

    executable_lines.append(log_line2)

    log_line3 = 'echo ""                   >> ${LOG}\n'

    executable_lines.append(log_line3)

    execution_line = '${EXE}  ${INP} >> ${LOG}\n'

    executable_lines.append(execution_line)

    with open(execution_filename, 'w') as file:
        file.writelines(executable_lines)
        file.close()

    return execution_filename

def createRandomSamplingToolInputs(sample_size,
                                   seed,                                  
                                   relative_covariance_matrix_path,
                                   energy_grid,
                                   nuclide,
                                   mt_Number):
    """
    Creates the input file to be used with the random sampling tool

    Parameters:
        sample_size (int): Number of random sampling ACE file inputs to be created

        seed (int): Random seed for the perturbation coefficient random sampling tool

        relative_covariance_matrix_path (str): Path to the .csv file with the relative covariance data

        energy_grid (list or nd_array): Energy bounds for where the perturbations will be applied

        nuclide (str): Name of the nuclide of investigation

        mt_Number (int): MT number for the reaction of interest

    Results:
        sample_filename (str): Path to the file specifying the inputs for the random sampling tool
    """

    'Create the random sampling input file'

    sample_filename = 'sample_copy.inp'

    sample_lines = []

    sample_size_line = '<sample_size>         ' +str(sample_size) + '\n'

    sample_lines.append(sample_size_line)

    linespace = '\n'

    sample_lines.append(linespace)

    seed_line = '<seed>                ' + str(seed) + '\n'

    sample_lines.append(seed_line)

    sample_lines.append(linespace)

    covariance_matrix_line = '<relative_covariance> ' + str(relative_covariance_matrix_path) + '\n'

    sample_lines.append(covariance_matrix_line)

    sample_lines.append(linespace)

    for zz in range(0, len(energy_grid)):

        if zz == 0:

            energy_line = '<energy_grid>          (' + str(energy_grid[zz]) + '\n'

            sample_lines.append(energy_line)

        elif zz == len(energy_grid) - 1:

            energy_line = '                       ' + str(energy_grid[zz]) + ')\n'  

            sample_lines.append(energy_line)

        else:

            energy_line = '                       ' + str(energy_grid[zz]) + '\n'

            sample_lines.append(energy_line)
    
    sample_lines.append(linespace)

    nuclide_line = '<nuclide>             (' + str(nuclide) + ')\n'

    sample_lines.append(nuclide_line)

    sample_lines.append(linespace)

    reaction_line = '<reaction>            (' + str(mt_Number) +')\n'

    sample_lines.append(reaction_line)

    sample_lines.append(linespace)

    with open(sample_filename, 'w') as file:
        file.writelines(sample_lines)
        file.close()

    return sample_filename

def generateRandomSamplingFactors(execution_filename,
                                  random_sampling_tool_directory,
                                  nuclide,
                                  sample_filename,
                                  cleanup_Flag):

    """
    Execute the creation of the randomly sampled perturbation coefficients

    Parameters:
        execution_filename (str): Name of the file that is ran to execute creating the random sampling ACE files

        random_sampling_tool_directory (str): Directory where the random sampling executable is located

        nuclide (str): Name of the nuclide of interest

        sample_filename (str): Path to the file acting as the input for the random sampling tool    

        cleanup_Flag (Bool): Flag to indicate if intermediate files from the ACE file creation process will be removed.    
    """

    'Import needed modules'

    import os

    perturbation_factor_command = 'csh ./' + str(execution_filename)

    os.system(perturbation_factor_command)

    'Check if the perturbation factors were made successfully'

    if os.path.exists(random_sampling_tool_directory + '/' +str(nuclide)):
        print('Perturbation factors created successfully')
    else:
        print('Perturbation factors not created successfully')

    'Remove extra files if chosen to do so'

    if cleanup_Flag:
        os.remove(sample_filename)
        os.remove(execution_filename)

def moveRandomSamplingFiles(random_sampling_tool_directory,
                            nuclide,
                            frendy_Path,
                            mt_Number):
    """
    Moves the random sampling files from the tools directory to a new directory for better management

    Parameters:
        random_sampling_tool_directory (str): Directory where the random sampling tool executable is located

        nuclide (str): Name of the nuclide of investigation

        frendy_Path (str): Full path to the directory created by FRENDY during the installation process
        End of path should be '.../frendy_YYYYMMDD' where 'YYYYMMDD' corresponds to the date related to the version of FRENDY installed

        mt_Number (int): MT number of the reaction of interest

    Results:
        new_inputs_directory_name (str): Directory where the random sampling inputs are stored
    """

    'Import needed modules'

    import shutil
    
    'Move the perturbation factor inputs to the root FRENDY directory, and change their name'

    original_inputs_directory = random_sampling_tool_directory + '/' +str(nuclide)

    new_inputs_directory = frendy_Path

    shutil.move(original_inputs_directory, new_inputs_directory)

    new_inputs_directory_name =  str(nuclide) + '_RandomSamplingInputs_ReactionMT_' + str(mt_Number) + '_Inputs'

    shutil.move(frendy_Path + '/' + str(nuclide),  frendy_Path + '/' + new_inputs_directory_name)

    return new_inputs_directory_name

def createRandomSamplingPertList(nuclide,
                                 mt_Number,
                                 new_inputs_directory_name,
                                 sample_size):
    """
    Create the random sampling perturbations list

    Parameters:
        nuclide (str): Name of the nuclide of interest

        mt_Number (int): MT number of the reaction of interest

        new_inputs_directory_name (str): Directory where the random sampling inputs are located

        sample_size (int): Number of random sampling input files generated

    Results:
        perturbation_list_filename (str): Path to the file with the list of random sampling inputs
    """

    perturbation_list_filename = 'perturbation_list_' + str(nuclide) + '_MT_' + str(mt_Number) + '.inp'

    perturbation_list_lines = []

    for ii in range(0, sample_size):
        if ii < 9:
            perturbation_input_line = new_inputs_directory_name + '/' + str(nuclide) + f"_000{ii+1}\n"
            perturbation_list_lines.append(perturbation_input_line)

        elif (ii>=9) and (ii<=98):
            perturbation_input_line = new_inputs_directory_name + '/' + str(nuclide) + f"_00{ii+1}\n"
            perturbation_list_lines.append(perturbation_input_line)

        else:
            perturbation_input_line = new_inputs_directory_name + '/' + str(nuclide) + f"_0{ii+1}\n"
            perturbation_list_lines.append(perturbation_input_line)
    
    with open(perturbation_list_filename, 'w') as file:
        file.writelines(perturbation_list_lines)
        file.close()

    return perturbation_list_filename

def createRandomSamplingACEDirectory(frendy_Path,
                                     nuclide,
                                     mt_Number,
                                     perturbation_list_filename,
                                     new_inputs_directory_name):
    """
    Create a new directory to store the ACE files, and move the needed files there

    Parameters:
        frendy_Path (str): Full path to the directory created by FRENDY during the installation process
        End of path should be '.../frendy_YYYYMMDD' where 'YYYYMMDD' corresponds to the date related to the version of FRENDY installed

        nuclide (str): Name of the nuclide being investigated

        mt_Number (int): MT number of the reaction of interest

        perturbation_list_filename (str): Path to the file with the list of random sampling inputs

        new_inputs_directory_name (str): Directory where the random sampling inputs are located
    """

    'Import needed modules'

    import os 
    import shutil

    ace_files_directory = frendy_Path + '/' + str(nuclide) + '_RandomSamplingACEFiles_ReactionMT_'  + str(mt_Number)

    os.mkdir(ace_files_directory)

    shutil.move(frendy_Path + '/' + perturbation_list_filename, ace_files_directory + '/' + perturbation_list_filename)
    shutil.move(frendy_Path + '/' + new_inputs_directory_name, ace_files_directory + '/' + new_inputs_directory_name)

    return ace_files_directory

def createRandomSamplingACEExecutionFile(frendy_Path,
                                         ace_files_directory,
                                         nuclide,
                                         mt_Number,
                                         unperturbed_ACE_file_path):
    """
    Generate the execution file for creating the random sampling ACE files

    Parameters:
        frendy_Path (str): Full path to the directory created by FRENDY during the installation process
        End of path should be '.../frendy_YYYYMMDD' where 'YYYYMMDD' corresponds to the date related to the version of FRENDY installed

        ace_files_directory (str): Directory where the random sampling ACE files will be created

        nuclide (str): Name of the nuclide under investigation

        mt_Number (int): MT number of the reaction of interest

        unperturbed_ACE_file_path (str): Path to the unperturbed ACE file for the nuclide of interest

    Results:
        create_ace_files_input_filename (str): Path to the file ran to initiate generating the random sampling ACE files
    """

    create_ace_files_input_filename = 'run_create_perturbed_ace_file.csh'

    input_file_lines = []

    first_line = '#!/bin/csh\n'

    linespace = '\n'

    input_file_lines.append(first_line)
    input_file_lines.append(linespace)

    executable_line = 'set EXE     = ' + str(frendy_Path) + '/tools/perturbation_ace_file/perturbation_ace_file.exe'
    input_file_lines.append(executable_line)
    input_file_lines.append(linespace)

    perturbation_list_line = 'set INP     = ' + str(ace_files_directory) + '/' + 'perturbation_list_' + str(nuclide) + '_MT_' + str(mt_Number) + '.inp'
    input_file_lines.append(perturbation_list_line)
    input_file_lines.append(linespace)

    unperturbed_ace_file_line = 'set ACE     = ' + str(unperturbed_ACE_file_path)
    input_file_lines.append(unperturbed_ace_file_line)
    input_file_lines.append(linespace)

    output_log_line1 = 'set LOG = results.log\n'
    input_file_lines.append(output_log_line1)

    output_log_line2 = 'echo "${EXE}  ${ACE}  ${INP}"      > ${LOG}\n'
    input_file_lines.append(output_log_line2)

    output_log_line3 = 'echo ""                           >> ${LOG}\n'
    input_file_lines.append(output_log_line3)

    running_command_line = '${EXE}  ${ACE}  ${INP} >> ${LOG}\n'
    input_file_lines.append(running_command_line)

    with open(create_ace_files_input_filename, 'w') as file:
        file.writelines(input_file_lines)
        file.close()

    return create_ace_files_input_filename

def randomSamplingFolderCheck(sample_size,
                              ace_files_directory):
    """
    Check if all of the files were created successfully based on the folder numbers they should be in

    Parameters:
        sample_size (int): Number of samples used in the ACE file generation

        ace_files_directory (str): Directory where the random sampling ACE files are located

    Results:
        file_failure_flag (Bool): Flag used to indicate if all of the ACE files were properly created
    """

    'Import needed modules'

    import os

    file_failure_flag = False

    for ii in range(0, sample_size):
        if ii < 9:
            folder_to_check = str(ace_files_directory) + f"000{ii+1}"

        elif (ii>=9) and (ii<=98):
            folder_to_check = str(ace_files_directory) + f"00{ii+1}"

        else:
            folder_to_check = str(ace_files_directory) + f"0{ii+1}"
        
        if os.path.exists(folder_to_check):
            continue
        else:
            file_failure_flag = True
            break

    return file_failure_flag