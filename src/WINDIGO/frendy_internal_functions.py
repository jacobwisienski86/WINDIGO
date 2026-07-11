# Internal functions involving FRENDY for WINDIGO.
# Not intended to be called directly by users.

import shutil
import os


def format_endf_evaluation(endf_Path):
    """
    Format a raw ENDF evaluation into the .dat format required by FRENDY.

    Parameters
    ----------
    endf_Path : str
        Path to the ENDF evaluation used to create an unperturbed ACE file.

    Returns
    -------
    str
        Path to the .dat formatted ENDF evaluation.
    """
    endf_file_original = endf_Path
    endf_file_intermediate = endf_file_original[:-5]
    endf_file_dat = f"{endf_file_intermediate}.dat"

    shutil.copy2(endf_file_original, endf_file_dat)

    return endf_file_dat


def write_upgrade_lines(energy_grid):
    """
    Write optional lines for the unperturbed ACE generation input file to
    add additional energy grid points.

    Parameters
    ----------
    energy_grid : list or ndarray
        Energy bounds used for perturbations.

    Returns
    -------
    list of str
        Lines specifying additional energy grid points.
    """
    upgrade_lines = []
    upgrade_energy_bounds = []

    for ii in range(len(energy_grid)):
        energy = energy_grid[ii]

        if energy < 99.99:
            if ii == 0:
                upgrade_energy_bounds.append(energy + 1e-6)
            elif ii == len(energy_grid) - 1:
                upgrade_energy_bounds.append(energy - 1e-6)
            else:
                upgrade_energy_bounds.append(energy - 1e-6)
                upgrade_energy_bounds.append(energy + 1e-6)

        elif 99.99 <= energy < 99990:
            if ii == 0:
                upgrade_energy_bounds.append(energy + 0.1)
            elif ii == len(energy_grid) - 1:
                upgrade_energy_bounds.append(energy - 0.1)
            else:
                upgrade_energy_bounds.append(energy - 0.1)
                upgrade_energy_bounds.append(energy + 0.1)

        else:
            if ii == 0:
                upgrade_energy_bounds.append(energy + 1000)
            elif ii == len(energy_grid) - 1:
                upgrade_energy_bounds.append(energy - 1000)
            else:
                upgrade_energy_bounds.append(energy - 1000)
                upgrade_energy_bounds.append(energy + 1000)

    for jj, bound in enumerate(upgrade_energy_bounds):
        if jj == 0:
            line = f"    add_grid_data    ({bound}\n"
        elif jj == len(upgrade_energy_bounds) - 1:
            line = f"        {bound})\n"
        else:
            line = f"        {bound}\n"
        upgrade_lines.append(line)

    return upgrade_lines


def create_unperturbed_ace_generation_input(
    frendy_Path,
    nuclide,
    endf_file_dat,
    temperature,
    upgrade_Flag=False,
    energy_grid=None,
):
    """
    Write the input file used to generate unperturbed ACE files.

    Parameters
    ----------
    frendy_Path : str
        Path to FRENDY installation directory.

    nuclide : str
        Name of the nuclide whose ENDF evaluation is used.
    
    endf_file_dat: str
        Name of the .dat-formatted ENDF evaluation used for
        ACE file generation.

    temperature : int
        Temperature at which to generate the ACE file.

    upgrade_Flag : bool, optional
        Add additional energy grid points if True.

    energy_grid : list or ndarray, optional
        Energy grid used for perturbation bounds [eV].

    Returns
    -------
    str
        Path to the ACE generation input file.
    """
    if energy_grid is None:
        energy_grid = []

    ace_file_gen_input_filename = (
        f"{frendy_Path}/frendy/main/{nuclide}_acegenerator"
    )

    if upgrade_Flag:
        ace_file_gen_input_filename += "_upgrade.dat"
    else:
        ace_file_gen_input_filename += "_normal.dat"

    ace_file_lines = []

    # ACE generation mode
    ace_file_lines.append("ace_file_generation_fast_mode\n")

    # Nuclear data file
    ace_file_lines.append(
        f"    nucl_file_name    {endf_file_dat}\n"
    )

    # Temperature
    ace_file_lines.append(f"    temp    {temperature}\n")

    # Output ACE file name
    if upgrade_Flag:
        ace_file_lines.append(
            f"    ace_file_name    {nuclide}_upgrade.ace\n"
        )
    else:
        ace_file_lines.append(
            f"    ace_file_name    {nuclide}.ace\n"
        )

    # Add upgrade lines if needed
    if upgrade_Flag:
        upgrade_lines = write_upgrade_lines(energy_grid=energy_grid)
        ace_file_lines.extend(upgrade_lines)

    # Write file
    with open(ace_file_gen_input_filename, "w") as file:
        file.writelines(ace_file_lines)

    print(
        "The path to the ace file generation input is: "
        f"{ace_file_gen_input_filename}\n"
    )

    return ace_file_gen_input_filename


def create_direct_perturbation_inputs(
    nuclide,
    mt_Number,
    energy_grid,
    perturbation_coefficient
):
    """
    Create a folder to store direct perturbation inputs, generate the input
    files, and return their names.

    Parameters
    ----------
    nuclide : str
        Nuclide whose ACE file will be perturbed.

    mt_Number : int
        MT number of the reaction to perturb.

    energy_grid : list or ndarray
        Energy bounds for perturbations [MeV].

    perturbation_coefficient : float
        Multiplicative factor for the perturbation.

    Returns
    -------
    list of str
        Names of each direct perturbation input file.

    str
        Directory containing the input files.
    """
    folder_name = (
        f"{nuclide}_DirectPerturbationInputs_ReactionMT_{mt_Number}"
    )
    os.mkdir(folder_name)

    perturbation_list_lines = []

    for ii in range(len(energy_grid) - 1):
        if ii < 9:
            suffix = f"_000{ii + 1}"
        elif 9 <= ii <= 98:
            suffix = f"_00{ii + 1}"
        else:
            suffix = f"_0{ii + 1}"

        input_file_path = f"{folder_name}/{nuclide}{suffix}"
        perturbation_list_lines.append(f"{input_file_path}\n")

        with open(input_file_path, "w") as file:
            file.write(
                f"{mt_Number}     {energy_grid[ii]}     "
                f"{energy_grid[ii + 1]}     {perturbation_coefficient}"
            )

    return perturbation_list_lines, folder_name

def create_direct_perturbation_list(
    nuclide,
    mt_Number,
    perturbation_list_lines
):
    """
    Create a file containing the list of direct perturbation input files.

    Parameters
    ----------
    nuclide : str
        Name of the nuclide whose ACE file is being perturbed.

    mt_Number : int
        MT number of the reaction being perturbed.

    perturbation_list_lines : list of str
        Names of the direct perturbation input files.

    Returns
    -------
    str
        Name of the file containing the list of direct perturbation inputs.
    """
    perturbation_list_filename = (
        f"perturbation_list_{nuclide}_MT_{mt_Number}Direct.inp"
    )

    with open(perturbation_list_filename, "w") as file:
        file.writelines(perturbation_list_lines)

    return perturbation_list_filename


def create_direct_perturbation_command_file(
    frendy_Path,
    perturbation_list_filename,
    unperturbed_ACE_file_path
):
    """
    Create a .csh script containing commands to generate direct
    perturbation ACE files.

    Parameters
    ----------
    frendy_Path : str
        Path to FRENDY installation directory.

    perturbation_list_filename : str
        File containing list of direct perturbation inputs.

    unperturbed_ACE_file_path : str
        Path to the unperturbed ACE file.

    Returns
    -------
    str
        Path to the generated .csh command file.
    """
    create_ace_files_input_filename = "run_create_perturbed_ace_file.csh"

    input_file_lines = []
    newline = "\n"

    input_file_lines.append("#!/bin/csh\n")
    input_file_lines.append(newline)

    exe_line = (
        f"set EXE     = {frendy_Path}"
        "/tools/perturbation_ace_file/perturbation_ace_file.exe"
    )
    input_file_lines.append(exe_line)
    input_file_lines.append(newline)

    inp_line = f"set INP     = {perturbation_list_filename}"
    input_file_lines.append(inp_line)
    input_file_lines.append(newline)

    ace_line = f"set ACE     = {unperturbed_ACE_file_path}"
    input_file_lines.append(ace_line)
    input_file_lines.append(newline)

    input_file_lines.append("set LOG = results.log\n")
    input_file_lines.append('echo "${EXE}  ${ACE}  ${INP}"      > ${LOG}\n')
    input_file_lines.append('echo ""                           >> ${LOG}\n')
    input_file_lines.append("${EXE}  ${ACE}  ${INP} >> ${LOG}\n")

    with open(create_ace_files_input_filename, "w") as file:
        file.writelines(input_file_lines)

    return create_ace_files_input_filename


def direct_perturbation_folder_check(
    perturbed_ace_folder_path,
    energy_grid
):
    """
    Check that all direct perturbation ACE files were created by verifying
    that their expected folders exist.

    Parameters
    ----------
    perturbed_ace_folder_path : str
        Directory containing direct perturbation ACE files.

    energy_grid : list or ndarray
        Energy bounds for perturbations.

    Returns
    -------
    bool
        True if any ACE file folder is missing, False otherwise.
    """
    file_failure_flag = False

    for ii in range(len(energy_grid) - 1):
        if ii < 9:
            folder_to_check = f"{perturbed_ace_folder_path}/000{ii + 1}"
        elif 9 <= ii <= 98:
            folder_to_check = f"{perturbed_ace_folder_path}/00{ii + 1}"
        else:
            folder_to_check = f"{perturbed_ace_folder_path}/0{ii + 1}"

        if not os.path.exists(folder_to_check):
            file_failure_flag = True
            break

    return file_failure_flag


def create_random_sampling_tool_execution_file(
    executable_directory,
    random_sampling_tool_directory
):
    """
    Create the .csh script needed to execute the random sampling tool.

    Parameters
    ----------
    executable_directory : str
        Path to the random sampling tool executable.

    random_sampling_tool_directory : str
        Directory containing the tool.

    Returns
    -------
    str
        Path to the .csh execution script.
    """
    execution_filename = "run_make_perturbation_factor.csh"

    lines = []
    newline = "\n"

    lines.append("#!/bin/csh\n")
    lines.append(newline)

    lines.append(f"set EXE     = {executable_directory}\n")
    lines.append(newline)

    inp_line = (
        "set INP        = "
        f"{random_sampling_tool_directory}/sample_copy.inp"
    )
    lines.append(inp_line)
    lines.append(newline)
    lines.append(newline)

    lines.append("set LOG = result.log\n")
    lines.append('echo "${EXE}  ${INP}"      > ${LOG}\n')
    lines.append('echo ""                   >> ${LOG}\n')
    lines.append("${EXE}  ${INP} >> ${LOG}\n")

    with open(execution_filename, "w") as file:
        file.writelines(lines)

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
    Create the input file used by the random sampling tool.

    Parameters
    ----------
    sample_size : int
        Number of random sampling ACE file inputs.

    seed : int
        Random seed for the sampling tool.

    relative_covariance_matrix_path : str
        Path to CSV containing relative covariance data.

    energy_grid : list or ndarray
        Energy bounds for perturbations.

    nuclide : str
        Nuclide name.

    mt_Number : int
        MT number for the reaction.

    Returns
    -------
    str
        Path to the random sampling tool input file.
    """
    sample_filename = "sample_copy.inp"
    sample_lines = []

    sample_lines.append(f"<sample_size>         {sample_size}\n")
    sample_lines.append("\n")

    sample_lines.append(f"<seed>                {seed}\n")
    sample_lines.append("\n")

    sample_lines.append(
        f"<relative_covariance> {relative_covariance_matrix_path}\n"
    )
    sample_lines.append("\n")

    for zz, energy in enumerate(energy_grid):
        if zz == 0:
            line = f"<energy_grid>          ({energy}\n"
        elif zz == len(energy_grid) - 1:
            line = f"                       {energy})\n"
        else:
            line = f"                       {energy}\n"
        sample_lines.append(line)

    sample_lines.append("\n")
    sample_lines.append(f"<nuclide>             ({nuclide})\n")
    sample_lines.append("\n")
    sample_lines.append(f"<reaction>            ({mt_Number})\n")
    sample_lines.append("\n")

    with open(sample_filename, "w") as file:
        file.writelines(sample_lines)

    return sample_filename


def generate_random_sampling_factors(
    execution_filename,
    random_sampling_tool_directory,
    nuclide,
    sample_filename,
    cleanup_Flag
):
    """
    Execute the creation of randomly sampled perturbation coefficients.

    Parameters
    ----------
    execution_filename : str
        Script used to run the sampling tool.

    random_sampling_tool_directory : str
        Directory containing the tool.

    nuclide : str
        Nuclide name.

    sample_filename : str
        Input file for the sampling tool.

    cleanup_Flag : bool
        Remove intermediate files if True.
    """
    command = f"csh ./{execution_filename}"
    os.system(command)

    # Check success
    if os.path.exists(f"{random_sampling_tool_directory}/{nuclide}"):
        print("Perturbation factors created successfully")
    else:
        print("Perturbation factors not created successfully")

    # Cleanup
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
    Move random sampling files from the tool directory to a new directory
    for better management.

    Parameters
    ----------
    random_sampling_tool_directory : str
        Directory containing the tool.

    nuclide : str
        Nuclide name.

    frendy_Path : str
        Path to FRENDY installation directory.

    mt_Number : int
        MT number of the reaction.

    Returns
    -------
    str
        Directory where the sampling inputs are stored.
    """
    original_inputs_directory = (
        f"{random_sampling_tool_directory}/{nuclide}"
    )

    shutil.move(original_inputs_directory, frendy_Path)

    new_inputs_directory_name = (
        f"{nuclide}_RandomSamplingInputs_ReactionMT_{mt_Number}_Inputs"
    )

    shutil.move(
        f"{frendy_Path}/{nuclide}",
        f"{frendy_Path}/{new_inputs_directory_name}"
    )

    return new_inputs_directory_name


def create_random_sampling_pert_list(
    nuclide,
    mt_Number,
    new_inputs_directory_name,
    sample_size
):
    """
    Create the random sampling perturbation list file.

    Parameters
    ----------
    nuclide : str
        Name of the nuclide of interest.

    mt_Number : int
        MT number of the reaction of interest.

    new_inputs_directory_name : str
        Directory where the random sampling inputs are located.

    sample_size : int
        Number of random sampling input files generated.

    Returns
    -------
    str
        Path to the file containing the list of random sampling inputs.
    """
    perturbation_list_filename = (
        f"perturbation_list_{nuclide}_MT_{mt_Number}.inp"
    )

    perturbation_list_lines = []

    for ii in range(sample_size):
        if ii < 9:
            suffix = f"_000{ii + 1}"
        elif 9 <= ii <= 98:
            suffix = f"_00{ii + 1}"
        else:
            suffix = f"_0{ii + 1}"

        line = f"{new_inputs_directory_name}/{nuclide}{suffix}\n"
        perturbation_list_lines.append(line)

    with open(perturbation_list_filename, "w") as file:
        file.writelines(perturbation_list_lines)

    return perturbation_list_filename


def create_random_sampling_ace_directory(
    frendy_Path,
    nuclide,
    mt_Number,
    perturbation_list_filename,
    new_inputs_directory_name
):
    """
    Create a directory to store ACE files and move required files into it.

    Parameters
    ----------
    frendy_Path : str
        Path to FRENDY installation directory.

    nuclide : str
        Name of the nuclide being investigated.

    mt_Number : int
        MT number of the reaction of interest.

    perturbation_list_filename : str
        Path to the list of random sampling inputs.

    new_inputs_directory_name : str
        Directory where the sampling inputs are located.

    Returns
    -------
    str
        Path to the directory containing the ACE files.
    """
    ace_files_directory = (
        f"{frendy_Path}/{nuclide}_RandomSamplingACEFiles_"
        f"ReactionMT_{mt_Number}"
    )

    os.mkdir(ace_files_directory)

    shutil.move(
        f"{frendy_Path}/{perturbation_list_filename}",
        f"{ace_files_directory}/{perturbation_list_filename}"
    )

    shutil.move(
        f"{frendy_Path}/{new_inputs_directory_name}",
        f"{ace_files_directory}/{new_inputs_directory_name}"
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
    Generate the execution file for creating random sampling ACE files.

    Parameters
    ----------
    frendy_Path : str
        Path to FRENDY installation directory.

    ace_files_directory : str
        Directory where the ACE files will be created.

    nuclide : str
        Name of the nuclide under investigation.

    mt_Number : int
        MT number of the reaction of interest.

    unperturbed_ACE_file_path : str
        Path to the unperturbed ACE file.

    Returns
    -------
    str
        Path to the .csh execution file.
    """
    create_ace_files_input_filename = "run_create_perturbed_ace_file.csh"

    lines = []
    newline = "\n"

    lines.append("#!/bin/csh\n")
    lines.append(newline)

    exe_line = (
        f"set EXE     = {frendy_Path}"
        "/tools/perturbation_ace_file/perturbation_ace_file.exe"
    )
    lines.append(exe_line)
    lines.append(newline)

    inp_line = (
        f"set INP     = {ace_files_directory}/"
        f"perturbation_list_{nuclide}_MT_{mt_Number}.inp"
    )
    lines.append(inp_line)
    lines.append(newline)

    ace_line = f"set ACE     = {unperturbed_ACE_file_path}"
    lines.append(ace_line)
    lines.append(newline)

    lines.append("set LOG = results.log\n")
    lines.append('echo "${EXE}  ${ACE}  ${INP}"      > ${LOG}\n')
    lines.append('echo ""                           >> ${LOG}\n')
    lines.append("${EXE}  ${ACE}  ${INP} >> ${LOG}\n")

    with open(create_ace_files_input_filename, "w") as file:
        file.writelines(lines)

    return create_ace_files_input_filename


def random_sampling_folder_check(
    sample_size,
    ace_files_directory
):
    """
    Check whether all expected ACE file folders were created.

    Parameters
    ----------
    sample_size : int
        Number of samples used in ACE file generation.

    ace_files_directory : str
        Directory where the ACE files are located.

    Returns
    -------
    bool
        True if any ACE file folder is missing, False otherwise.
    """
    file_failure_flag = False

    for ii in range(sample_size):
        if ii < 9:
            folder = f"{ace_files_directory}/000{ii + 1}"
        elif 9 <= ii <= 98:
            folder = f"{ace_files_directory}/00{ii + 1}"
        else:
            folder = f"{ace_files_directory}/0{ii + 1}"

        if not os.path.exists(folder):
            file_failure_flag = True
            break

    return file_failure_flag
