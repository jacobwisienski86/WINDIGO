# Functions related to FRENDY functionality for WINDIGO

import os
import shutil

from .frendy_internal_functions import (
    format_endf_evaluation,
    create_unperturbed_ace_generation_input,
    create_direct_perturbation_inputs,
    create_direct_perturbation_list,
    create_direct_perturbation_command_file,
    direct_perturbation_folder_check,
    create_random_sampling_tool_execution_file,
    create_random_sampling_tool_inputs,
    generate_random_sampling_factors,
    move_random_sampling_files,
    create_random_sampling_pert_list,
    create_random_sampling_ace_directory,
    create_random_sampling_ace_execution_file,
    random_sampling_folder_check,
)


def generate_unperturbed_neutron_ace_file(
    frendy_Path,
    endf_Path,
    temperature,
    nuclide,
    upgrade_Flag=False,
    energy_grid=None,
    cleanup_Flag=True,
):
    """
    Generate unperturbed neutron cross section ACE files for use in the
    workflow.

    Parameters
    ----------
    frendy_Path : str
        Full path to the FRENDY installation directory.

    endf_Path : str
        Full path to the ENDF evaluation for the nuclide.

    temperature : int
        Temperature at which to generate the ACE file.

    nuclide : str
        Name of the nuclide whose ENDF evaluation is used.

    upgrade_Flag : bool, optional
        Add additional energy grid points if True.

    energy_grid : list or ndarray, optional
        Energy grid used for perturbation bounds [eV].

    cleanup_Flag : bool, optional
        Delete intermediate files if True.

    Returns
    -------
    str
        Path to the generated ACE file.
    """
    if energy_grid is None:
        energy_grid = []

    # Convert ENDF evaluation to .dat format
    endf_file_dat = format_endf_evaluation(endf_Path=endf_Path)

    # Create FRENDY input file
    ace_file_gen_input_filename = create_unperturbed_ace_generation_input(
        frendy_Path=frendy_Path,
        nuclide=nuclide,
        endf_file_dat=endf_file_dat,
        temperature=temperature,
        upgrade_Flag=upgrade_Flag,
        energy_grid=energy_grid,
    )

    # Build command and switch directories
    executable_directory = f"{frendy_Path}/frendy/main"
    run_command = f"./frendy.exe {ace_file_gen_input_filename}"

    starting_directory = os.getcwd()
    os.chdir(executable_directory)
    os.system(run_command)
    os.chdir(starting_directory)

    # Cleanup intermediate files
    if cleanup_Flag:
        os.remove(endf_file_dat)
        os.remove(ace_file_gen_input_filename)

    # Determine output ACE file path
    if upgrade_Flag:
        output_file_path = (
            f"{executable_directory}/{nuclide}_upgrade.ace"
        )
        if cleanup_Flag:
            os.remove(
                f"{executable_directory}/{nuclide}_upgrade.ace.ace.dir"
            )
            print("Intermediate Files Removed")
    else:
        output_file_path = f"{executable_directory}/{nuclide}.ace"
        if cleanup_Flag:
            os.remove(
                f"{executable_directory}/{nuclide}.ace.ace.dir"
            )
            print("Intermediate Files Removed")

    # Report success or failure
    print("\n")
    if os.path.exists(output_file_path):
        print(
            "ACE file successfully generated. The path to it is: "
            f"{output_file_path}"
        )
    else:
        print(
            "ACE file couldn't generate; consult terminal output for "
            "assistance"
        )

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
    Generate direct perturbation ACE files.

    Parameters
    ----------
    frendy_Path : str
        Path to FRENDY installation.

    unperturbed_ACE_file_path : str
        Path to the unperturbed ACE file.

    energy_grid : list or ndarray
        Energy bounds for perturbations [MeV].

    mt_Number : int
        MT number of the reaction to perturb.

    nuclide : str
        Nuclide whose ACE file will be perturbed.

    perturbation_coefficient : float
        Multiplicative factor for perturbation.

    cleanup_Flag : bool, optional
        Delete intermediate files if True.

    Returns
    -------
    str
        Directory containing perturbed ACE files.
    """
    starting_directory = os.getcwd()
    os.chdir(frendy_Path)

    # Create directory for perturbed ACE files
    perturbed_ace_folder_path = (
        f"{frendy_Path}/{nuclide}_DirectPerturbationACEFiles_"
        f"ReactionMT_{mt_Number}"
    )
    os.makedirs(perturbed_ace_folder_path)

    os.chdir(perturbed_ace_folder_path)

    # Create direct perturbation inputs
    (
        perturbation_list_lines,
        perturbation_input_folder_name
    ) = create_direct_perturbation_inputs(
        nuclide=nuclide,
        mt_Number=mt_Number,
        energy_grid=energy_grid,
        perturbation_coefficient=perturbation_coefficient
    )

    # Create list file
    perturbation_list_filename = create_direct_perturbation_list(
        nuclide=nuclide,
        mt_Number=mt_Number,
        perturbation_list_lines=perturbation_list_lines
    )

    # Create execution file
    create_ace_files_input_filename = (
        create_direct_perturbation_command_file(
            frendy_Path=frendy_Path,
            perturbation_list_filename=perturbation_list_filename,
            unperturbed_ACE_file_path=unperturbed_ACE_file_path
        )
    )

    # Run FRENDY command
    os.system("csh ./run_create_perturbed_ace_file.csh")

    # Check for failures
    file_failure_flag = direct_perturbation_folder_check(
        perturbed_ace_folder_path=perturbed_ace_folder_path,
        energy_grid=energy_grid
    )

    # Cleanup
    if cleanup_Flag:
        os.remove(perturbation_list_filename)
        shutil.rmtree(perturbation_input_folder_name)
        os.remove(create_ace_files_input_filename)
        os.remove(f"{perturbed_ace_folder_path}/results.log")
        print("Intermediate Files Removed")

    os.chdir(starting_directory)

    # Report results
    if file_failure_flag:
        print(
            "One or more ACE files failed to generate; consult outputs "
            "for details"
        )
    else:
        print(
            "All ACE files have successfully generated; they are located in: "
            f"{perturbed_ace_folder_path}"
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
    Generate ACE files perturbed using randomly sampled perturbation
    coefficients.

    Parameters
    ----------
    frendy_Path : str
        Path to FRENDY installation directory.

    relative_covariance_matrix_path : str
        Path to CSV containing relative covariance matrix data.

    unperturbed_ACE_file_path : str
        Path to the unperturbed ACE file.

    energy_grid : list or ndarray
        Energy bounds for perturbations [MeV].

    mt_Number : int
        MT number for the reaction of interest.

    nuclide : str
        Nuclide name without hyphens (e.g., H1, U235).

    seed : int, optional
        Random sampling seed. Default is 1234567.

    sample_size : int, optional
        Number of random sampling input files. Default is 100.

    cleanup_Flag : bool, optional
        Delete intermediate files if True.

    Returns
    -------
    str
        Directory where the random sampling ACE files are located.
    """
    # Save starting directory
    starting_directory = os.getcwd()

    # Set up random sampling tool paths
    random_sampling_tool_directory = (
        f"{frendy_Path}/tools/make_perturbation_factor"
    )
    executable_directory = (
        f"{random_sampling_tool_directory}/make_perturbation_factor.exe"
    )

    os.chdir(random_sampling_tool_directory)

    # Create execution file for random sampling tool
    execution_filename = create_random_sampling_tool_execution_file(
        executable_directory=executable_directory,
        random_sampling_tool_directory=random_sampling_tool_directory
    )

    # Create random sampling input file
    sample_filename = create_random_sampling_tool_inputs(
        sample_size=sample_size,
        seed=seed,
        relative_covariance_matrix_path=relative_covariance_matrix_path,
        energy_grid=energy_grid,
        nuclide=nuclide,
        mt_Number=mt_Number
    )

    # Generate random perturbation factors
    generate_random_sampling_factors(
        execution_filename=execution_filename,
        random_sampling_tool_directory=random_sampling_tool_directory,
        nuclide=nuclide,
        sample_filename=sample_filename,
        cleanup_Flag=cleanup_Flag
    )

    # Move sampled perturbation factors to FRENDY root directory
    new_inputs_directory_name = move_random_sampling_files(
        random_sampling_tool_directory=random_sampling_tool_directory,
        nuclide=nuclide,
        frendy_Path=frendy_Path,
        mt_Number=mt_Number
    )

    # Move to FRENDY root directory
    os.chdir(frendy_Path)

    # Create list of random sampling inputs
    perturbation_list_filename = create_random_sampling_pert_list(
        nuclide=nuclide,
        mt_Number=mt_Number,
        new_inputs_directory_name=new_inputs_directory_name,
        sample_size=sample_size
    )

    # Create directory for ACE files and move inputs into it
    ace_files_directory = create_random_sampling_ace_directory(
        frendy_Path=frendy_Path,
        nuclide=nuclide,
        mt_Number=mt_Number,
        perturbation_list_filename=perturbation_list_filename,
        new_inputs_directory_name=new_inputs_directory_name
    )

    # Move into ACE file directory
    os.chdir(ace_files_directory)

    # Create execution file for ACE generation
    create_ace_files_input_filename = (
        create_random_sampling_ace_execution_file(
            frendy_Path=frendy_Path,
            ace_files_directory=ace_files_directory,
            nuclide=nuclide,
            mt_Number=mt_Number,
            unperturbed_ACE_file_path=unperturbed_ACE_file_path
        )
    )

    # Run ACE generation command
    random_sampling_file_command = (
        f"csh ./{create_ace_files_input_filename}"
    )
    os.system(random_sampling_file_command)

    # Check for failures
    file_failure_flag = random_sampling_folder_check(
        sample_size=sample_size,
        ace_files_directory=ace_files_directory
    )

    # Cleanup
    if cleanup_Flag:
        os.remove(perturbation_list_filename)
        shutil.rmtree(new_inputs_directory_name)
        os.remove(create_ace_files_input_filename)
        os.remove("results.log")
        print("Intermediate Files Removed")

    # Return to starting directory
    os.chdir(starting_directory)

    # Report results
    if file_failure_flag:
        print(
            "ACE files not generated successfully; check outputs for more "
            "information"
        )
    else:
        print(
            "All ACE files generated successfully and are located in: "
            f"{ace_files_directory}"
        )
        return ace_files_directory