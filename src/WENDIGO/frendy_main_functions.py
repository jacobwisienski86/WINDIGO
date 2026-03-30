# Set of functions related to the workflow that make use of FRENDY


def generate_unperturbed_neutron_ace_file(
    frendy_Path,
    endf_Path,
    temperature,
    nuclide,
    upgrade_Flag=False,
    energy_grid=None,
    cleanup_Flag=True
):
    """
    Generates unperturbed neutron cross section ACE files for use in the workflow.

    Parameters:
        frendy_Path (str): Full path to the FRENDY installation directory.

        endf_Path (str): Full path to the ENDF evaluation for the nuclide.

        temperature (int): Temperature at which to generate the ACE file.

        nuclide (str): Name of the nuclide whose ENDF evaluation is used.

        upgrade_Flag (Bool): Add additional energy grid points if True.

        energy_grid (list or ndarray): Energy grid used for perturbation bounds.

        cleanup_Flag (Bool): Delete intermediate files if True.

    Results:
        output_file_path (str): Path to the generated ACE file.
    """

    'Import modules and internal functions'

    import os
    from .FRENDYInternalFunctions import (
        format_endf_evaluation,
        create_unperturbed_ace_generation_input
    )

    if energy_grid is None:
        energy_grid = []

    'Format the endf file into a .dat format'

    endf_file_dat = format_endf_evaluation(endf_Path=endf_Path)

    'Write the input file for the ACE file generation'

    ace_file_gen_input_filename = create_unperturbed_ace_generation_input(
        frendy_Path=frendy_Path,
        nuclide=nuclide,
        endf_file_dat=endf_file_dat,
        temperature=temperature,
        upgrade_Flag=upgrade_Flag,
        energy_grid=energy_grid
    )

    'Specifies the executable directory and the ACE file generation command'

    executable_directory = frendy_Path + '/frendy/main'
    run_command = './frendy.exe ' + str(ace_file_gen_input_filename)

    'Save the starting directory so that it can be returned to after FRENDY runs'

    starting_directory = os.getcwd()

    'Set the current directory to that of the FRENDY executable, and run the command'

    os.chdir(executable_directory)
    os.system(str(run_command))

    'Return to the starting directory after FRENDY runs'

    os.chdir(starting_directory)

    'First portion of the optional intermediate file cleanup'

    if cleanup_Flag:
        os.remove(endf_file_dat)
        os.remove(ace_file_gen_input_filename)

    (
        "Specify output ACE file's name for printing later, and perform any "
        "remaining file cleanup if needed"
    )

    if upgrade_Flag:
        output_file_path = executable_directory + '/' + str(nuclide) + '_upgrade.ace'

        if cleanup_Flag:
            os.remove(executable_directory + '/' + str(nuclide) + '_upgrade.ace.ace.dir')
            print('Intermediate Files Removed')

    else:
        output_file_path = executable_directory + '/' + str(nuclide) + '.ace'

        if cleanup_Flag:
            os.remove(executable_directory + '/' + str(nuclide) + '.ace.ace.dir')
            print('Intermediate Files Removed')

    'Check if the ACE file was successfully generated'

    if os.path.exists(output_file_path):
        print('\n')
        print("ACE file successfully generated. The path to it is: " + str(output_file_path))
    else:
        print('\n')
        print("ACE file couldn't generate; consult terminal output for assistance")

    return output_file_path


def generate_direct_perturbation_ace_files(
    frendy_Path,
    unperturbed_ACE_file_path,
    energy_grid,
    mt_Number,
    nuclide,
    perturbation_coefficient,
    cleanup_Flag=True
):
    """
    Generates direct perturbation ACE files.

    Parameters:
        frendy_Path (str): Path to FRENDY installation.

        unperturbed_ACE_file_path (str): Path to the unperturbed ACE file.

        energy_grid (list or ndarray): Energy bounds for perturbations [MeV].

        mt_Number (int): MT number of the reaction to perturb.

        nuclide (str): Nuclide whose ACE file will be perturbed.

        perturbation_coefficient (float): Multiplicative factor for perturbation.

        cleanup_Flag (Bool): Delete intermediate files if True.

    Results:
        perturbed_ace_folder_path (str): Directory containing perturbed ACE files.
    """

    'Import necessary modules and functions'

    import os
    import shutil
    from .FRENDYInternalFunctions import (
        create_direct_perturbation_inputs,
        create_direct_perturbation_list,
        create_direct_perturbation_command_file,
        direct_perturbation_folder_check
    )

    'Store the initial directory to return to after creating the ACE files'

    starting_directory = os.getcwd()

    'Set the current directory to that of FRENDY'

    os.chdir(frendy_Path)

    'Create a folder to store the directly perturbed ACE files'

    perturbed_ace_folder_path = (
        frendy_Path + '/' + str(nuclide)
        + '_DirectPerturbationACEFiles_ReactionMT_' + str(mt_Number)
    )

    os.makedirs(perturbed_ace_folder_path)

    'Set the current directory to that folder for ease of generation'

    os.chdir(perturbed_ace_folder_path)

    'Create the direct perturbation input files'

    (
        perturbation_list_lines,
        perturbation_input_folder_name
    ) = create_direct_perturbation_inputs(
        nuclide=nuclide,
        mt_Number=mt_Number,
        energy_grid=energy_grid,
        perturbation_coefficient=perturbation_coefficient
    )

    'Create a list of the direct perturbation input files'

    perturbation_list_filename = create_direct_perturbation_list(
        nuclide=nuclide,
        mt_Number=mt_Number,
        perturbation_list_lines=perturbation_list_lines
    )

    'Create the execution file for the direct perturbations'

    create_ace_files_input_filename = create_direct_perturbation_command_file(
        frendy_Path=frendy_Path,
        perturbation_list_filename=perturbation_list_filename,
        unperturbed_ACE_file_path=unperturbed_ACE_file_path
    )

    'Run the file generation command'

    file_generation_command = 'csh ./run_create_perturbed_ace_file.csh'
    os.system(file_generation_command)

    'Check if all of the files were created successfully'

    file_failure_flag = direct_perturbation_folder_check(
        perturbed_ace_folder_path=perturbed_ace_folder_path,
        energy_grid=energy_grid
    )

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
        print(
            "All ACE files have successfully generated; they are located in: "
            + str(perturbed_ace_folder_path)
        )
        return perturbed_ace_folder_path

def generate_random_sampling_ace_files(
    frendy_Path,
    relative_covariance_matrix_path,
    unperturbed_ACE_file_path,
    energy_grid,
    mt_Number,
    nuclide,
    seed=1234567,
    sample_size=100,
    cleanup_Flag=True
):
    """
    Generates ACE files perturbed using randomly sampled perturbation coefficients.

    Parameters:
        frendy_Path (str): Path to FRENDY installation directory.

        relative_covariance_matrix_path (str): Path to CSV with relative
        covariance matrix data.

        unperturbed_ACE_file_path (str): Path to the unperturbed ACE file.

        energy_grid (list or ndarray): Energy bounds for perturbations [MeV].

        mt_Number (int): MT number for the reaction of interest.

        nuclide (str): Nuclide name without hyphens (e.g., H1, U235).

        seed (int): Random sampling seed. Default: 1234567.

        sample_size (int): Number of random sampling input files. Default: 100.

        cleanup_Flag (Bool): Delete intermediate files if True.

    Results:
        ace_files_directory (str): Directory where the random sampling ACE
        files are located.
    """

    'Import modules'

    import os
    import shutil
    from .frendy_internal_functions import (
        create_random_sampling_tool_execution_file,
        create_random_sampling_tool_inputs,
        generate_random_sampling_factors,
        move_random_sampling_files,
        create_random_sampling_pert_list,
        create_random_sampling_ace_directory,
        create_random_sampling_ace_execution_file,
        random_sampling_folder_check
    )

    'Grab the starting directory to return to as need be'

    starting_directory = os.getcwd()

    'Retrieve the directory for the random sampling'

    random_sampling_tool_directory = frendy_Path + '/tools/make_perturbation_factor'
    executable_directory = random_sampling_tool_directory + '/make_perturbation_factor.exe'

    os.chdir(random_sampling_tool_directory)

    'Create the file used to execute the commands for generating the random sampling perturbation coefficients'

    execution_filename = create_random_sampling_tool_execution_file(
        executable_directory=executable_directory,
        random_sampling_tool_directory=random_sampling_tool_directory
    )

    'Create random sampling tool inputs'

    sample_filename = create_random_sampling_tool_inputs(
        sample_size=sample_size,
        seed=seed,
        relative_covariance_matrix_path=relative_covariance_matrix_path,
        energy_grid=energy_grid,
        nuclide=nuclide,
        mt_Number=mt_Number
    )

    'Generate the randomly sampled perturbation factors'

    generate_random_sampling_factors(
        execution_filename=execution_filename,
        random_sampling_tool_directory=random_sampling_tool_directory,
        nuclide=nuclide,
        sample_filename=sample_filename,
        cleanup_Flag=cleanup_Flag
    )

    'Move the randomly sampled perturbation factors to the main FRENDY'
    'directory, and rename the associated folder'

    new_inputs_directory_name = move_random_sampling_files(
        random_sampling_tool_directory=random_sampling_tool_directory,
        nuclide=nuclide,
        frendy_Path=frendy_Path,
        mt_Number=mt_Number
    )

    'Move to the root FRENDY directory'

    os.chdir(frendy_Path)

    'Generate a file with a list of the random sampling inputs'

    perturbation_list_filename = create_random_sampling_pert_list(
        nuclide=nuclide,
        mt_Number=mt_Number,
        new_inputs_directory_name=new_inputs_directory_name,
        sample_size=sample_size
    )

    
    'Create a directory to store the random sampling ACE files, and move '
    'the inputs and perturbation list into it'

    ace_files_directory = create_random_sampling_ace_directory(
        frendy_Path=frendy_Path,
        nuclide=nuclide,
        mt_Number=mt_Number,
        perturbation_list_filename=perturbation_list_filename,
        new_inputs_directory_name=new_inputs_directory_name
    )

    'Set the current directory to that where the randomly sampled ACE files will be stored'

    os.chdir(ace_files_directory)

    'Create the file with the commands to create the ACE files'

    create_ace_files_input_filename = create_random_sampling_ace_execution_file(
        frendy_Path=frendy_Path,
        ace_files_directory=ace_files_directory,
        nuclide=nuclide,
        mt_Number=mt_Number,
        unperturbed_ACE_file_path=unperturbed_ACE_file_path
    )

    'Run the command to generate the ACE files'

    random_sampling_file_command = 'csh ./' + str(create_ace_files_input_filename)
    os.system(random_sampling_file_command)

    'Check if all of the ACE files were created properly'

    file_failure_flag = random_sampling_folder_check(
        sample_size=sample_size,
        ace_files_directory=ace_files_directory
    )

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

    if file_failure_flag is False:
        print('ACE files not generated successfully; check outputs for more information')
    else:
        print(
            'All ACE files generated successfully and are located in: '
            + str(ace_files_directory)
        )
        return ace_files_directory
