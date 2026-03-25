"Set of functions related to the workflow that make use of FRENDY"

def GenerateUnperturbedNeutronACEFile(frendy_Path, endf_Path, temperature, nuclide, upgrade_Flag = False, energy_Grid = [], cleanup_Flag = True):
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

        upgrade_Flag (Boolean): Flag used to determine whether the ACE file will have additional energy grid points added to increase chances of successful data perturbations
            Default: False

        energy_Grid (list or nd_array): Values of the energy grid used to determine perturbation bounds.
            Should be the same as those corresponding to the retrieval of covariance data
            Default: Empty list ([])

        cleanup_Flag (Boolean): Flag used to determine if automatic file cleanup will occur after completing the ACE file generation.
            Deletes all intermediate files leaving the final ACE file as the only new file created.
            Default: True

    """
    'Import necessary modules'

    import os
    import shutil

    'Create a .dat file to use for the ACE file generation'

    endf_file_original = endf_Path

    endf_file_intermediate = endf_file_original[:-5]

    endf_file_dat = str(endf_file_intermediate) + '.dat'

    shutil.copy2(endf_file_original, endf_file_dat)

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

        'Generates a list of the extra energy bounds to add to the input file'

        upgrade_energy_bounds = []

        for ii in range(0, len(energy_Grid)):

            if (energy_Grid[ii] < 99.99):

                if ii == 0:

                    upgrade_energy_bounds.append(energy_Grid[ii] + (1E-6))

                elif ii == (len(energy_Grid) - 1):

                    upgrade_energy_bounds.append(energy_Grid[ii] - (1E-6))

                else:

                    upgrade_energy_bounds.append(energy_Grid[ii] - (1E-6))

                    upgrade_energy_bounds.append(energy_Grid[ii] + (1E-6))
            
            elif (energy_Grid[ii] >= 99.99) and (energy_Grid[ii] < 99990):

                if ii == 0:

                    upgrade_energy_bounds.append(energy_Grid[ii] + 0.1)

                elif ii == (len(energy_Grid) - 1):

                    upgrade_energy_bounds.append(energy_Grid[ii] - 0.1)

                else:

                    upgrade_energy_bounds.append(energy_Grid[ii] - 0.1)

                    upgrade_energy_bounds.append(energy_Grid[ii] + 0.1)

            else:

                if ii == 0:

                    upgrade_energy_bounds.append(energy_Grid[ii] + 1000)

                elif ii == (len(energy_Grid) - 1):

                    upgrade_energy_bounds.append(energy_Grid[ii] - 1000)

                else:

                    upgrade_energy_bounds.append(energy_Grid[ii] - 1000)

                    upgrade_energy_bounds.append(energy_Grid[ii] + 1000)

        'Lines that specify the additional energy grid points to add in the ACE file generation'
                
        for jj in range(0, len(upgrade_energy_bounds)):

            if jj == 0:
                
                upgraded_bound_line = '    add_grid_data    (' + str(upgrade_energy_bounds[jj]) + '\n'

                ace_file_lines.append(upgraded_bound_line)
            
            elif jj == (len(upgrade_energy_bounds) - 1):

                upgraded_bound_line = '        ' + str(upgrade_energy_bounds[jj]) + ')\n'

                ace_file_lines.append(upgraded_bound_line)

            else:

                upgraded_bound_line = '        ' + str(upgrade_energy_bounds[jj]) + '\n'

                ace_file_lines.append(upgraded_bound_line)

    
    'Write the ace file generation input'

    with open(ace_file_gen_input_filename, 'w') as file:

        file.writelines(ace_file_lines)

        file.close()

    print('The path to the ace file generation input is: ' + str(ace_file_gen_input_filename) + '\n')

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

def GenerateDirectPerturbationACEFiles(frendy_Path, unperturbed_ACE_file_path, energy_Grid_MeV, mt_Numbers, nuclide, perturbation_coefficient, cleanup_Flag = True):
    
    """
    
    Need to write

    """

    'Import necessary modules'

    import os 
    import shutil
    import sys

    'Store the initial directory to return to after creating the ACE files'

    starting_directory = os.getcwd()

    'Set the current directory to that of FRENDY'

    os.chdir(frendy_Path)

    'Create a folder to store the directly perturbation ACE files'

    perturbed_ace_folder_path = frendy_Path + '/' + str(nuclide) + '_DirectPerturbationACEFiles_ReactionMT'

    for mt in mt_Numbers:
        
        perturbed_ace_folder_path += '_'
        perturbed_ace_folder_path += str(mt)

    os.makedirs(perturbed_ace_folder_path)

    'Set the current directory to that of the folder for ease in file generation, execution, and cleanup'

    os.chdir(perturbed_ace_folder_path)

    'Create a folder to store the perturbation input files'

    perturbation_input_folder_name = str(nuclide) + '_DirectPerturbationInputs_ReactionMT'

    for mt in mt_Numbers:
        
        perturbation_input_folder_name += '_'
        perturbation_input_folder_name += str(mt)

    os.mkdir(perturbation_input_folder_name)

    'Write the input files into the folder, and create a list of the input files that is needed by FRENDY'

    perturbation_list_filename = 'perturbation_list_' + str(nuclide) + '_MT' 

    for mt in mt_Numbers:

        perturbation_list_filename += '_'
        perturbation_list_filename += str(mt)

    perturbation_list_filename += 'Direct.inp'

    perturbation_list_lines = []

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

        'Set a failure mode in case multiple MT numbers are used'
        if len(mt_Numbers) > 1:
            sys.exit('Code is currently only configured for single MT number perturbations. Additional multi-MT functionality will be added later')
        else:
            with open(perturbation_input_file_name, 'w') as file:
                file.write(str(mt) + '     ' + str(energy_grid[ii]) + '     ' + str(energy_grid[ii+1]) + '     ' + str(perturbation_coefficient))
                file.close()
            
    with open(perturbation_list_filename, 'w') as file:
        file.writelines(perturbation_list_lines)
        file.close()

    'Generate the input file to perform the direct perturbations'
    'Some of the lines help to produce an output log that may be useful for debugging; make sure cleanup_Flag is set to False so to ensure it isn''t deleted'

    create_ace_files_input_filename = 'run_create_perturbed_ace_file.csh'

    input_file_lines = []

    first_line = '#!/bin/csh\n'
    input_file_lines.append(first_line)

    first_space = '\n'
    input_file_lines.append(first_space)

    executable_line = 'set EXE     = ' + str(frendy_Path) + '/tools/perturbation_ace_file/perturbation_ace_file.exe'
    input_file_lines.append(executable_line)

    second_space = '\n'
    input_file_lines.append(second_space)

    perturbation_list_line = 'set INP     = ' + str(perturbation_list_filename)
    input_file_lines.append(perturbation_list_line)

    third_space = '\n'
    input_file_lines.append(third_space)

    unperturbed_ace_file_line = 'set ACE     = ' + str(unperturbed_ACE_file_path)
    input_file_lines.append(unperturbed_ace_file_line)

    fourth_space = '\n'
    input_file_lines.append(fourth_space)

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
    
    'Run the file generation command'

    file_generation_command = 'csh ./run_create_perturbed_ace_file.csh'

    os.system(file_generation_command)

    'Check if all of the files were created successfully based on the folder numbers they should be in'

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

def GenerateRandomSamplingACEFiles(frendy_Path, relative_covariance_matrix_path, unperturbed_ACE_file_path, energy_Grid_MeV, mt_Numbers, nuclide, seed = 1234567, sample_size = 100, cleanup_Flag = False):
    """

    Write later

    """

    'Import modules'

    import os 
    import shutil

    'Grab the starting directory to return to as need be'

    starting_directory = os.getcwd()

    'Retrieve the directory for the random sampling'

    random_sampling_tool_directory = frendy_Path + '/tools/make_perturbation_factor'

    executable_directory = random_sampling_tool_directory + '/make_perturbation_factor.exe'

    os.chdir(random_sampling_tool_directory)

    'Set up the execution file'

    execution_filename = 'run_make_perturbation_factor.csh'

    executable_lines = []

    first_line = '#!/bin/csh\n'

    executable_lines.append(first_line)

    first_space = '\n'

    executable_lines.append(first_space)

    executor_line = 'set EXE     = ' + str(executable_directory) + '\n'

    executable_lines.append(executor_line)

    second_space = '\n'

    executable_lines.append(second_space)

    input_line = 'set INP        = ' + str(random_sampling_tool_directory) + '/sample_copy.inp'  

    executable_lines.append(input_line)

    third_space = '\n'

    executable_lines.append(third_space)

    fourth_space = '\n'

    executable_lines.append(fourth_space)

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

    for zz in range(0, len(energy_Grid_MeV)):

        if zz == 0:

            energy_line = '<energy_grid>          (' + str(energy_Grid_MeV[zz]) + '\n'

            sample_lines.append(energy_line)

        elif zz == len(energy_Grid_MeV) - 1:

            energy_line = '                       ' + str(energy_Grid_MeV[zz]) + ')\n'  

            sample_lines.append(energy_line)

        else:

            energy_line = '                       ' + str(energy_Grid_MeV[zz]) + '\n'

            sample_lines.append(energy_line)
    
    sample_lines.append(linespace)

    nuclide_line = '<nuclide>             (' + str(nuclide) + ')\n'

    sample_lines.append(nuclide_line)

    sample_lines.append(linespace)

    reaction_line = '<reaction>            (' + str(mt_Numbers) +')\n'

    sample_lines.append(reaction_line)

    sample_lines.append(linespace)

    with open(sample_filename, 'w') as file:
        file.writelines(sample_lines)
        file.close()

    'Execute the creation of the randomly sampled perturbation coefficients'

    perturbation_factor_command = 'csh ./' + str(execution_filename)

    os.system(perturbation_factor_command)

    'Check if the perturbation factors were made successfully'

    if os.path.exists(random_sampling_tool_directory + '/' +str(nuclide)):
        print('Perturbation factors created successfully')
    else:
        print('Perturbation factors not created successfully')

    'Remove extra files if chosen'

    if cleanup_Flag:
        os.remove(sample_filename)
        os.remove(execution_filename)
    
    'Move the perturbation factor inputs to the root FRENDY directory, and change their name'

    original_inputs_directory = random_sampling_tool_directory + '/' +str(nuclide)

    new_inputs_directory = frendy_Path

    shutil.move(original_inputs_directory, new_inputs_directory)

    new_inputs_directory_name =  str(nuclide) + '_RandomSamplingInputs_ReactionMT_' + str(mt_Numbers) + '_Inputs'

    shutil.move(frendy_Path + '/' + str(nuclide),  frendy_Path + '/' + new_inputs_directory_name)

    'Move to the root FRENDY directory'

    os.chdir(frendy_Path)

    'Create the random sampling perturbations list'

    perturbation_list_filename = 'perturbation_list_' + str(nuclide) + '_MT_' + str(mt_Numbers) + '.inp'

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

    'Create a new directory to store the ACE files, and move the needed files there'

    ace_files_directory = frendy_Path + '/' + str(nuclide) + '_RandomSamplingACEFiles_ReactionMT_'  + str(mt_Numbers)

    os.mkdir(ace_files_directory)

    shutil.move(frendy_Path + '/' + perturbation_list_filename, ace_files_directory + '/' + perturbation_list_filename)
    shutil.move(frendy_Path + '/' + new_inputs_directory_name, ace_files_directory + '/' + new_inputs_directory_name)

    os.chdir(ace_files_directory)

    'Generate the execution file'

    create_ace_files_input_filename = 'run_create_perturbed_ace_file.csh'

    input_file_lines = []

    first_line = '#!/bin/csh\n'
    input_file_lines.append(first_line)

    first_space = '\n'
    input_file_lines.append(first_space)

    executable_line = 'set EXE     = ' + str(frendy_Path) + '/tools/perturbation_ace_file/perturbation_ace_file.exe'
    input_file_lines.append(executable_line)

    second_space = '\n'
    input_file_lines.append(second_space)

    perturbation_list_line = 'set INP     = ' + str(ace_files_directory) + '/' + 'perturbation_list_' + str(nuclide) + '_MT_' + str(mt_Numbers) + '.inp'
    input_file_lines.append(perturbation_list_line)

    third_space = '\n'
    input_file_lines.append(third_space)

    unperturbed_ace_file_line = 'set ACE     = ' + str(unperturbed_ACE_file_path)
    input_file_lines.append(unperturbed_ace_file_line)

    fourth_space = '\n'
    input_file_lines.append(fourth_space)

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

    'Run the command to generate the ACE files'

    random_sampling_file_command = 'csh ./' + str(create_ace_files_input_filename)

    os.system(random_sampling_file_command)

    'Check if all of the files were created successfully based on the folder numbers they should be in'

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

    'Optional File Cleanup Section'

    if cleanup_Flag:
        os.remove(perturbation_list_filename)
        shutil.rmtree(new_inputs_directory_name)
        os.remove(create_ace_files_input_filename)
        os.remove(perturbed_ace_folder_path + '/results.log')

        print('Intermediate Files Removed')

    'Return to the starting directory'

    os.chdir(starting_directory)

    if file_failure_flag == False:
        print('ACE files not generated successfully; check outputs for more information')
    else:
        print('All ACE files generated successfully and are located in: ' + str(ace_files_directory))

