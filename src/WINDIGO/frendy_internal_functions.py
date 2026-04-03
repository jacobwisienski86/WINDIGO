# Set of internal functions involving FRENDY related to the uncertainty
# quantification workflow. Not intended to be called directly when using
# the workflow.

# Functions related to generating unperturbed ACE files

import shutil
import os

def format_endf_evaluation(endf_Path):
    """
    Formats the raw ENDF evaluation into a .dat format needed for use by FRENDY.

    Parameters:
        endf_Path (str): Path to the ENDF evaluation used to create an
        unperturbed ACE file.

    Results:
        endf_file_dat (str): Path to the .dat formatted ENDF evaluation.
    """

    'Create a .dat file to use for the ACE file generation'

    endf_file_original = endf_Path
    endf_file_intermediate = endf_file_original[:-5]
    endf_file_dat = str(endf_file_intermediate) + '.dat'

    shutil.copy2(endf_file_original, endf_file_dat)

    return endf_file_dat


def write_upgrade_lines(energy_grid):
    """
    Writes optional lines to include within the unperturbed ACE file generation
    input file to add more energy grid points.

    Parameters:
        energy_grid (list or ndarray): Energy bounds used for perturbations.

    Results:
        upgrade_lines (list): Lines to add additional energy grid points.
    """

    upgrade_lines = []

    'Generates a list of the extra energy bounds to add to the input file'

    upgrade_energy_bounds = []

    for ii in range(0, len(energy_grid)):

        if energy_grid[ii] < 99.99:

            if ii == 0:
                upgrade_energy_bounds.append(energy_grid[ii] + 1e-6)
            elif ii == (len(energy_grid) - 1):
                upgrade_energy_bounds.append(energy_grid[ii] - 1e-6)
            else:
                upgrade_energy_bounds.append(energy_grid[ii] - 1e-6)
                upgrade_energy_bounds.append(energy_grid[ii] + 1e-6)

        elif 99.99 <= energy_grid[ii] < 99990:

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

    'Lines that specify the additional energy grid points to add'

    for jj in range(0, len(upgrade_energy_bounds)):

        if jj == 0:
            upgraded_bound_line = (
                '    add_grid_data    (' + str(upgrade_energy_bounds[jj]) + '\n'
            )
            upgrade_lines.append(upgraded_bound_line)

        elif jj == (len(upgrade_energy_bounds) - 1):
            upgraded_bound_line = (
                '        ' + str(upgrade_energy_bounds[jj]) + ')\n'
            )
            upgrade_lines.append(upgraded_bound_line)

        else:
            upgraded_bound_line = (
                '        ' + str(upgrade_energy_bounds[jj]) + '\n'
            )
            upgrade_lines.append(upgraded_bound_line)

    return upgrade_lines


def create_unperturbed_ace_generation_input(
    frendy_Path,
    nuclide,
    endf_file_dat,
    temperature,
    upgrade_Flag=False,
    energy_grid=None
):
    """
    Writes the input file used to generate the unperturbed ACE files.

    Parameters:
        frendy_Path (str): Path to FRENDY installation directory.

    Results:
        ace_file_gen_input_filename (str): Path to the ACE generation input file.
    """

    if energy_grid is None:
        energy_grid = []

    'Generate the input file to be run by FRENDY'

    ace_file_gen_input_filename = (
        str(frendy_Path) + '/frendy/main/' + str(nuclide) + '_acegenerator'
    )

    'Modify input file name based on if upgrades are specified'

    if upgrade_Flag:
        ace_file_gen_input_filename += '_upgrade.dat'
    else:
        ace_file_gen_input_filename += '_normal.dat'

    ace_file_lines = []

    'Line specifying ACE file generation mode'

    file_gen_type_line = 'ace_file_generation_fast_mode\n'
    ace_file_lines.append(file_gen_type_line)

    'Line specifying where to find the nuclear data'

    nucl_data_file_line = (
        '    nucl_file_name    ' + str(endf_file_dat) + '\n'
    )
    ace_file_lines.append(nucl_data_file_line)

    'Line specifying the temperature'

    temp_line = '    temp    ' + str(temperature) + '\n'
    ace_file_lines.append(temp_line)

    'Line specifying output ACE file name'

    if upgrade_Flag:
        ace_file_output_name_line = (
            '    ace_file_name    ' + str(nuclide) + '_upgrade.ace\n'
        )
    else:
        ace_file_output_name_line = (
            '    ace_file_name    ' + str(nuclide) + '.ace\n'
        )

    ace_file_lines.append(ace_file_output_name_line)

    'Section that performs the energy grid upgrade'

    if upgrade_Flag:
        upgrade_lines = write_upgrade_lines(energy_grid=energy_grid)
        for line in upgrade_lines:
            ace_file_lines.append(line)

    'Write the ACE file generation input'

    with open(ace_file_gen_input_filename, 'w') as file:
        file.writelines(ace_file_lines)
        file.close()

    print(
        'The path to the ace file generation input is: '
        + str(ace_file_gen_input_filename)
        + '\n'
    )

    return ace_file_gen_input_filename


# Functions related to generating direct perturbation ACE files


def create_direct_perturbation_inputs(
    nuclide,
    mt_Number,
    energy_grid,
    perturbation_coefficient
):
    """
    Creates a folder to store the direct perturbation inputs, generates the
    inputs, and writes the names of the inputs to a list.

    Parameters:
        nuclide (str): Nuclide whose ACE file will be perturbed.

        mt_Number (int): MT number of the reaction to be perturbed.

        energy_grid (list or ndarray): Energy bounds for perturbations [MeV].

        perturbation_coefficient (float): Multiplicative factor for the
        perturbation.

    Results:
        perturbation_list_lines (list): Names of each direct perturbation input.

        perturbation_input_folder_name (str): Directory containing the inputs.
    """

    'Create a folder to store the perturbation input files'

    perturbation_input_folder_name = (
        str(nuclide) + '_DirectPerturbationInputs_ReactionMT_' + str(mt_Number)
    )

    os.mkdir(perturbation_input_folder_name)

    'Create a blank list to store the names of direct perturbation inputs'

    perturbation_list_lines = []

    'Generate the direct perturbation inputs, and store their names'

    for ii in range(0, len(energy_grid) - 1):

        if ii < 9:
            perturbation_input_file_name = (
                perturbation_input_folder_name
                + '/'
                + str(nuclide)
                + f"_000{ii + 1}"
            )

        elif 9 <= ii <= 98:
            perturbation_input_file_name = (
                perturbation_input_folder_name
                + '/'
                + str(nuclide)
                + f"_00{ii + 1}"
            )

        else:
            perturbation_input_file_name = (
                perturbation_input_folder_name
                + '/'
                + str(nuclide)
                + f"_0{ii + 1}"
            )

        input_file_line = perturbation_input_file_name + '\n'
        perturbation_list_lines.append(input_file_line)

        with open(perturbation_input_file_name, 'w') as file:
            file.write(
                str(mt_Number)
                + '     '
                + str(energy_grid[ii])
                + '     '
                + str(energy_grid[ii + 1])
                + '     '
                + str(perturbation_coefficient)
            )
            file.close()

    return perturbation_list_lines, perturbation_input_folder_name

def create_direct_perturbation_list(
    nuclide,
    mt_Number,
    perturbation_list_lines
):
    """
    Creates a file with a list of the direct perturbation input files.

    Parameters:
        nuclide (str): Name of the nuclide whose ACE file is being perturbed.

        mt_Number (int): MT number of the reaction being perturbed.

        perturbation_list_lines (list): Names of the direct perturbation
        input files.

    Results:
        perturbation_list_filename (str): Name of the file containing the list
        of direct perturbation input files.
    """

    perturbation_list_filename = (
        'perturbation_list_' + str(nuclide) + '_MT_' + str(mt_Number)
    )

    perturbation_list_filename += 'Direct.inp'

    with open(perturbation_list_filename, 'w') as file:
        file.writelines(perturbation_list_lines)
        file.close()

    return perturbation_list_filename


def create_direct_perturbation_command_file(
    frendy_Path,
    perturbation_list_filename,
    unperturbed_ACE_file_path
):
    """
    Creates a .csh file with the commands and inputs to create the direct
    perturbation ACE files.

    Parameters:
        frendy_Path (str): Path to FRENDY installation directory.

        perturbation_list_filename (str): File containing list of direct
        perturbation inputs.

        unperturbed_ACE_file_path (str): Path to the unperturbed ACE file.

    Results:
        create_ace_files_input_filename (str): Path to the .csh command file.
    """

    'Generate the input file to perform the direct perturbations'

    create_ace_files_input_filename = 'run_create_perturbed_ace_file.csh'

    input_file_lines = []

    space_line = '\n'

    first_line = '#!/bin/csh\n'
    input_file_lines.append(first_line)
    input_file_lines.append(space_line)

    executable_line = (
        'set EXE     = '
        + str(frendy_Path)
        + '/tools/perturbation_ace_file/perturbation_ace_file.exe'
    )
    input_file_lines.append(executable_line)
    input_file_lines.append(space_line)

    perturbation_list_line = 'set INP     = ' + str(perturbation_list_filename)
    input_file_lines.append(perturbation_list_line)
    input_file_lines.append(space_line)

    unperturbed_ace_file_line = (
        'set ACE     = ' + str(unperturbed_ACE_file_path)
    )
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


def direct_perturbation_folder_check(
    perturbed_ace_folder_path,
    energy_grid
):
    """
    Checks that all direct perturbation ACE files were created by verifying
    that their expected folders exist.

    Parameters:
        perturbed_ace_folder_path (str): Directory containing direct
        perturbation ACE files.

        energy_grid (list or ndarray): Energy bounds for perturbations.

    Results:
        file_failure_flag (Bool): True if any ACE file is missing.
    """

    file_failure_flag = False

    for ii in range(0, len(energy_grid) - 1):

        if ii < 9:
            folder_to_check = perturbed_ace_folder_path + f"/000{ii + 1}"
        elif 9 <= ii <= 98:
            folder_to_check = perturbed_ace_folder_path + f"/00{ii + 1}"
        else:
            folder_to_check = perturbed_ace_folder_path + f"/0{ii + 1}"

        if os.path.exists(folder_to_check):
            continue
        else:
            file_failure_flag = True
            break

    return file_failure_flag


# Functions related to generating random sampling ACE files


def create_random_sampling_tool_execution_file(
    executable_directory,
    random_sampling_tool_directory
):
    """
    Creates the file needed to execute the random sampling tool.

    Parameters:
        executable_directory (str): Path to the random sampling tool executable.

        random_sampling_tool_directory (str): Directory containing the tool.

    Results:
        execution_filename (str): Path to the .csh execution script.
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

    input_line = (
        'set INP        = '
        + str(random_sampling_tool_directory)
        + '/sample_copy.inp'
    )
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

def create_random_sampling_tool_inputs(
    sample_size,
    seed,
    relative_covariance_matrix_path,
    energy_grid,
    nuclide,
    mt_Number
):
    """
    Creates the input file to be used with the random sampling tool.

    Parameters:
        sample_size (int): Number of random sampling ACE file inputs.

        seed (int): Random seed for the sampling tool.

        relative_covariance_matrix_path (str): Path to CSV with relative
        covariance data.

        energy_grid (list or ndarray): Energy bounds for perturbations.

        nuclide (str): Nuclide name.

        mt_Number (int): MT number for the reaction.

    Results:
        sample_filename (str): Path to the random sampling tool input file.
    """

    'Create the random sampling input file'

    sample_filename = 'sample_copy.inp'
    sample_lines = []

    sample_size_line = '<sample_size>         ' + str(sample_size) + '\n'
    sample_lines.append(sample_size_line)

    linespace = '\n'
    sample_lines.append(linespace)

    seed_line = '<seed>                ' + str(seed) + '\n'
    sample_lines.append(seed_line)
    sample_lines.append(linespace)

    covariance_matrix_line = (
        '<relative_covariance> ' + str(relative_covariance_matrix_path) + '\n'
    )
    sample_lines.append(covariance_matrix_line)
    sample_lines.append(linespace)

    for zz in range(0, len(energy_grid)):

        if zz == 0:
            energy_line = (
                '<energy_grid>          (' + str(energy_grid[zz]) + '\n'
            )
        elif zz == len(energy_grid) - 1:
            energy_line = (
                '                       ' + str(energy_grid[zz]) + ')\n'
            )
        else:
            energy_line = (
                '                       ' + str(energy_grid[zz]) + '\n'
            )

        sample_lines.append(energy_line)

    sample_lines.append(linespace)

    nuclide_line = '<nuclide>             (' + str(nuclide) + ')\n'
    sample_lines.append(nuclide_line)
    sample_lines.append(linespace)

    reaction_line = '<reaction>            (' + str(mt_Number) + ')\n'
    sample_lines.append(reaction_line)
    sample_lines.append(linespace)

    with open(sample_filename, 'w') as file:
        file.writelines(sample_lines)
        file.close()

    return sample_filename


def generate_random_sampling_factors(
    execution_filename,
    random_sampling_tool_directory,
    nuclide,
    sample_filename,
    cleanup_Flag
):
    """
    Execute the creation of the randomly sampled perturbation coefficients.

    Parameters:
        execution_filename (str): Script used to run the sampling tool.

        random_sampling_tool_directory (str): Directory containing the tool.

        nuclide (str): Nuclide name.

        sample_filename (str): Input file for the sampling tool.

        cleanup_Flag (Bool): Remove intermediate files if True.
    """

    perturbation_factor_command = 'csh ./' + str(execution_filename)
    os.system(perturbation_factor_command)

    'Check if the perturbation factors were made successfully'

    if os.path.exists(random_sampling_tool_directory + '/' + str(nuclide)):
        print('Perturbation factors created successfully')
    else:
        print('Perturbation factors not created successfully')

    'Remove extra files if chosen to do so'

    if cleanup_Flag:
        os.remove(sample_filename)
        os.remove(execution_filename)


def move_random_sampling_files(
    random_sampling_tool_directory,
    nuclide,
    frendy_Path,
    mt_Number
):
    """
    Moves the random sampling files from the tools directory to a new
    directory for better management.

    Parameters:
        random_sampling_tool_directory (str): Directory containing the tool.

        nuclide (str): Nuclide name.

        frendy_Path (str): Path to FRENDY installation directory.

        mt_Number (int): MT number of the reaction.

    Results:
        new_inputs_directory_name (str): Directory where the sampling inputs
        are stored.
    """

    'Move the perturbation factor inputs to the root FRENDY directory, '
    'and change their name'

    original_inputs_directory = (
        random_sampling_tool_directory + '/' + str(nuclide)
    )

    new_inputs_directory = frendy_Path
    shutil.move(original_inputs_directory, new_inputs_directory)

    new_inputs_directory_name = (
        str(nuclide)
        + '_RandomSamplingInputs_ReactionMT_'
        + str(mt_Number)
        + '_Inputs'
    )

    shutil.move(
        frendy_Path + '/' + str(nuclide),
        frendy_Path + '/' + new_inputs_directory_name
    )

    return new_inputs_directory_name

def create_random_sampling_pert_list(
    nuclide,
    mt_Number,
    new_inputs_directory_name,
    sample_size
):
    """
    Create the random sampling perturbations list.

    Parameters:
        nuclide (str): Name of the nuclide of interest.

        mt_Number (int): MT number of the reaction of interest.

        new_inputs_directory_name (str): Directory where the random sampling
        inputs are located.

        sample_size (int): Number of random sampling input files generated.

    Results:
        perturbation_list_filename (str): Path to the file with the list of
        random sampling inputs.
    """

    perturbation_list_filename = (
        'perturbation_list_' + str(nuclide) + '_MT_' + str(mt_Number) + '.inp'
    )

    perturbation_list_lines = []

    for ii in range(0, sample_size):

        if ii < 9:
            perturbation_input_line = (
                new_inputs_directory_name
                + '/'
                + str(nuclide)
                + f"_000{ii + 1}\n"
            )

        elif 9 <= ii <= 98:
            perturbation_input_line = (
                new_inputs_directory_name
                + '/'
                + str(nuclide)
                + f"_00{ii + 1}\n"
            )

        else:
            perturbation_input_line = (
                new_inputs_directory_name
                + '/'
                + str(nuclide)
                + f"_0{ii + 1}\n"
            )

        perturbation_list_lines.append(perturbation_input_line)

    with open(perturbation_list_filename, 'w') as file:
        file.writelines(perturbation_list_lines)
        file.close()

    return perturbation_list_filename


def create_random_sampling_ace_directory(
    frendy_Path,
    nuclide,
    mt_Number,
    perturbation_list_filename,
    new_inputs_directory_name
):
    """
    Create a new directory to store the ACE files, and move the needed files
    there.

    Parameters:
        frendy_Path (str): Path to FRENDY installation directory.

        nuclide (str): Name of the nuclide being investigated.

        mt_Number (int): MT number of the reaction of interest.

        perturbation_list_filename (str): Path to the list of random sampling
        inputs.

        new_inputs_directory_name (str): Directory where the sampling inputs
        are located.
    """

    ace_files_directory = (
        frendy_Path
        + '/'
        + str(nuclide)
        + '_RandomSamplingACEFiles_ReactionMT_'
        + str(mt_Number)
    )

    os.mkdir(ace_files_directory)

    shutil.move(
        frendy_Path + '/' + perturbation_list_filename,
        ace_files_directory + '/' + perturbation_list_filename
    )

    shutil.move(
        frendy_Path + '/' + new_inputs_directory_name,
        ace_files_directory + '/' + new_inputs_directory_name
    )

    return ace_files_directory


def create_random_sampling_ace_execution_file(
    frendy_Path,
    ace_files_directory,
    nuclide,
    mt_Number,
    unperturbed_ACE_file_path
):
    """
    Generate the execution file for creating the random sampling ACE files.

    Parameters:
        frendy_Path (str): Path to FRENDY installation directory.

        ace_files_directory (str): Directory where the ACE files will be
        created.

        nuclide (str): Name of the nuclide under investigation.

        mt_Number (int): MT number of the reaction of interest.

        unperturbed_ACE_file_path (str): Path to the unperturbed ACE file.

    Results:
        create_ace_files_input_filename (str): Path to the .csh execution file.
    """

    create_ace_files_input_filename = 'run_create_perturbed_ace_file.csh'

    input_file_lines = []

    first_line = '#!/bin/csh\n'
    linespace = '\n'

    input_file_lines.append(first_line)
    input_file_lines.append(linespace)

    executable_line = (
        'set EXE     = '
        + str(frendy_Path)
        + '/tools/perturbation_ace_file/perturbation_ace_file.exe'
    )
    input_file_lines.append(executable_line)
    input_file_lines.append(linespace)

    perturbation_list_line = (
        'set INP     = '
        + str(ace_files_directory)
        + '/'
        + 'perturbation_list_'
        + str(nuclide)
        + '_MT_'
        + str(mt_Number)
        + '.inp'
    )
    input_file_lines.append(perturbation_list_line)
    input_file_lines.append(linespace)

    unperturbed_ace_file_line = (
        'set ACE     = ' + str(unperturbed_ACE_file_path)
    )
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


def random_sampling_folder_check(
    sample_size,
    ace_files_directory
):
    """
    Check if all of the files were created successfully based on the folder
    numbers they should be in.

    Parameters:
        sample_size (int): Number of samples used in ACE file generation.

        ace_files_directory (str): Directory where the ACE files are located.

    Results:
        file_failure_flag (Bool): True if any ACE file is missing.
    """

    file_failure_flag = False

    for ii in range(0, sample_size):

        if ii < 9:
            folder_to_check = str(ace_files_directory) + f"/000{ii + 1}"
        elif 9 <= ii <= 98:
            folder_to_check = str(ace_files_directory) + f"/00{ii + 1}"
        else:
            folder_to_check = str(ace_files_directory) + f"/0{ii + 1}"
            
        if os.path.exists(folder_to_check):
            continue
        else:
            file_failure_flag = True
            break

    return file_failure_flag
