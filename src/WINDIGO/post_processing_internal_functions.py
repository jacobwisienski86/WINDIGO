# Internal functions to assist with WINDIGO's data post-processing capabilities.
# Not intended to be called directly by users.

import numpy as np
import matplotlib.pyplot as plt


def check_input_types(inputs):
    """
    Checks if the associated inputs are of type ndarray, and if not converts
    them to the ndarray data type.

    Parameters
    ----------
    inputs : list
        List of the inputs to be checked and possibly converted to the ndarray
        data type.

    Returns
    -------
    modified_inputs : list
        List of the original inputs that are all formatted to the ndarray data
        type.
    """
    # Create a blank list to store the modified inputs
    modified_inputs = []

    # Iterate over the inputs and convert their data type to ndarrays if needed
    for item in inputs:
        if type(item) is not np.ndarray:
            item = np.array(item)
        modified_inputs.append(item)

    return modified_inputs


def calculate_forward_coefficients(
    positive_perturbed_outputs,
    unperturbed_output,
    positive_perturbed_inputs,
    original_inputs,
    relative_flag,
):
    """
    Calculates sensitivity coefficients using a forward-differencing method.
    Performs an additional multiplication to non-dimensionalize the
    coefficients into their relative forms if needed.

    Parameters
    ----------
    positive_perturbed_outputs : ndarray
        Outputs from simulations that utilized positively perturbed inputs.

    unperturbed_output : int
        Output from a simulation that used unperturbed inputs. This is the
        reference value that perturbed outputs deviate from.

    positive_perturbed_inputs : ndarray
        Inputs used in simulations to obtain the outputs given in
        positive_perturbed_outputs.

    original_inputs : ndarray
        Unperturbed inputs used to obtain the unperturbed simulation output(s)
        of interest.

    relative_flag : bool
        Flag used to determine whether the sensitivity coefficients will be in
        their absolute or relative forms.

    Returns
    -------
    coefficients : ndarray
        Numpy array of either relative or absolute sensitivity coefficients.
    """
    # Calculate the absolute sensitivity coefficients using forward differencing
    coefficients = (
        positive_perturbed_outputs - unperturbed_output
    ) / (positive_perturbed_inputs - original_inputs)

    # Convert the absolute coefficients to relative ones if needed
    if relative_flag:
        coefficients = coefficients * (original_inputs / unperturbed_output)

    return coefficients


def calculate_backward_coefficients(
    negative_perturbed_outputs,
    unperturbed_output,
    negative_perturbed_inputs,
    original_inputs,
    relative_flag,
):
    """
    Calculates sensitivity coefficients using a backward-differencing method.
    Performs an additional multiplication to non-dimensionalize the
    coefficients into their relative forms if needed.

    Parameters
    ----------
    negative_perturbed_outputs : ndarray
        Outputs from simulations that utilized negatively perturbed inputs.

    unperturbed_output : int
        Output from a simulation that used unperturbed inputs.

    negative_perturbed_inputs : ndarray
        Inputs used in simulations to obtain the outputs given in
        negative_perturbed_outputs.

    original_inputs : ndarray
        Unperturbed inputs used to obtain the unperturbed simulation output(s)
        of interest.

    relative_flag : bool
        Flag used to determine whether the sensitivity coefficients will be in
        their absolute or relative forms.

    Returns
    -------
    coefficients : ndarray
        Numpy array of either relative or absolute sensitivity coefficients.
    """
    # Calculate the absolute sensitivity coefficients using backward differencing
    coefficients = (
        unperturbed_output - negative_perturbed_outputs
    ) / (original_inputs - negative_perturbed_inputs)

    # Convert the absolute coefficients to relative ones if needed
    if relative_flag:
        coefficients = coefficients * (original_inputs / unperturbed_output)

    return coefficients


#Calculation method based on methodology from Kleedtke et al. (2023)
#DOI: https://doi.org/10.1016/j.anucene.2023.110031
def calculate_central_coefficients(
    positive_perturbed_outputs,
    negative_perturbed_outputs,
    unperturbed_output,
    original_inputs,
    perturbation_coefficient,
    relative_flag,
):
    """
    Calculates sensitivity coefficients using a central-differencing method.
    Performs an additional multiplication to non-dimensionalize the
    coefficients into their relative forms if needed.

    Parameters
    ----------
    positive_perturbed_outputs : ndarray
        Outputs from simulations that utilized positively perturbed inputs.

    negative_perturbed_outputs : ndarray
        Outputs from simulations that utilized negatively perturbed inputs.

    unperturbed_output : int
        Output from a simulation that used unperturbed inputs.

    original_inputs : ndarray
        Unperturbed inputs used to obtain the unperturbed simulation output(s)
        of interest.

    perturbation_coefficient : float
        Fractional multiplier used to perturb the inputs in the sensitivity
        calculation simulations. Assumes symmetric positive and negative
        perturbations.

    relative_flag : bool
        Flag used to determine whether the sensitivity coefficients will be in
        their absolute or relative forms.

    Returns
    -------
    coefficients : ndarray
        Numpy array of either relative or absolute sensitivity coefficients.
    """
    # Calculate absolute coefficients using central differencing with symmetric
    # positive and negative perturbations
    coefficients = (
        positive_perturbed_outputs - negative_perturbed_outputs
    ) / (2 * perturbation_coefficient * original_inputs)

    # Convert the absolute coefficients to relative ones if needed
    if relative_flag:
        coefficients = coefficients * (original_inputs / unperturbed_output)

    return coefficients


def convert_per_lethargy(relative_sens_coefficients, energy_grid_MeV):
    """
    Converts a set of relative sensitivity coefficients to being per lethargy
    width based on a given energy grid.

    Parameters
    ----------
    relative_sens_coefficients : ndarray
        Relative sensitivity coefficients.

    energy_grid_MeV : ndarray
        Energy bounds of the perturbation intervals used for finding the
        relative sensitivity coefficients.

    Returns
    -------
    relative_sens_per_lethargy : ndarray
        Relative sensitivity coefficients converted to be per lethargy width.
    """
    # Create an array of lethargy widths
    lethargy_widths = []

    for ii in range(len(energy_grid_MeV) - 1):
        lethargy_width = np.log(
            energy_grid_MeV[ii + 1] / energy_grid_MeV[ii]
        )
        lethargy_widths.append(lethargy_width)

    lethargy_widths = np.array(lethargy_widths)

    # Compute the relative sensitivity per lethargy width
    relative_sens_per_lethargy = (
        relative_sens_coefficients / lethargy_widths
    )

    # Add an extra zero to assist with plotting
    relative_sens_per_lethargy = np.insert(
        relative_sens_per_lethargy, 0, 0
    )

    return relative_sens_per_lethargy


def plot_relative_sens(relative_sens_per_lethargy, energy_grid_MeV):
    """
    Generates a plot of the relative sensitivity coefficients per lethargy width
    plotted against the incident neutron energy in MeV.

    Parameters
    ----------
    relative_sens_per_lethargy : ndarray
        Relative sensitivity coefficients per lethargy width.

    energy_grid_MeV : ndarray
        Energy bounds of the perturbation intervals used for finding the
        relative sensitivity coefficients.
    """
    # Plot the sensitivity profile
    fig, ax = plt.subplots(figsize=(8, 6))

    ax.step(energy_grid_MeV, relative_sens_per_lethargy, color="black")
    ax.tick_params(axis="x", labelsize=18)
    ax.tick_params(axis="y", labelsize=18)
    ax.set_xscale("log")
    ax.set_xlabel("Energy (MeV)", fontsize=18)
    ax.set_ylabel("Relative Sensitivity Per Lethargy Width", fontsize=18)
    ax.grid()

    plt.tight_layout()
    plt.savefig("RelativeSensitivityPlot.png", dpi=350, bbox_inches="tight")
    plt.show()
