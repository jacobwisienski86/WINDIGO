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

def calculate_absolute_forward_coefficient_errors(
    original_inputs,
    positive_perturbed_inputs,
    unperturbed_output_error,
    positive_perturbed_output_errors
):
    
    """ 
    Calculates the errors of the forward-differencing absolute sensitivity coefficients

    Parameters
    ----------
    original_inputs : ndarray
        Unperturbed inputs used to obtain the unperturbed simulation output(s)
        of interest.

    positive_perturbed_inputs : ndarray
        Inputs used in simulations to obtain the outputs given in
        positive_perturbed_outputs.

    unperturbed_output_error : float
        Error of the output parameter calculated using unperturbed inputs.

    positive_perturbed_output_errors : ndarray
        Errors of the output parameters calculated using positively-perturbed
        inputs.

    Returns
    ----------
    absolute_coefficient_errors : ndarray
        Errors of the absolute sensitivity coefficients
    """

    absolute_coefficients_errors = ((1/(positive_perturbed_inputs - original_inputs)) *
                                    np.sqrt(positive_perturbed_output_errors**2 + unperturbed_output_error**2))

    return absolute_coefficients_errors 

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

def calculate_absolute_backward_coefficient_errors(
    original_inputs,
    negative_perturbed_inputs,
    unperturbed_output_error,
    negative_perturbed_output_errors
):
    
    """
    Calculates the errors of the backward-differencing absolute sensitivity coefficients

    Parameters
    ----------
    original_inputs : ndarray
        Unperturbed inputs used to obtain the unperturbed simulation output(s)
        of interest.

    negative_perturbed_inputs : ndarray
        Inputs used in simulations to obtain the outputs given in
        negative_perturbed_outputs.

    unperturbed_output_error : float
        Error of the output parameter calculated using unperturbed inputs.

    negative_perturbed_output_errors : ndarray
        Errors of the output parameters calculated using negatively-perturbed
        inputs.

    Returns
    ----------
    absolute_coefficient_errors : ndarray
        Errors of the absolute sensitivity coefficients
    """

    absolute_coefficient_errors = ((1/(original_inputs - negative_perturbed_inputs)) * 
                                   np.sqrt(unperturbed_output_error**2 + negative_perturbed_output_errors**2))
    
    return absolute_coefficient_errors

def calculate_central_coefficients(
    positive_perturbed_outputs,
    negative_perturbed_outputs,
    unperturbed_output,
    original_inputs,
    positive_perturbed_inputs,
    negative_perturbed_inputs,
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

    positive_perturbed_inputs : ndarray
        Inputs used in simulations to obtain the outputs given in
        positive_perturbed_outputs.

    negative_perturbed_inputs : ndarray
        Inputs used in simulations to obtain the outputs given in
        negative_perturbed_outputs.         

    relative_flag : bool
        Flag used to determine whether the sensitivity coefficients will be in
        their absolute or relative forms.

    Returns
    -------
    coefficients : ndarray
        Numpy array of either relative or absolute sensitivity coefficients.
    """
    # Calculate absolute coefficients using central differencing
    coefficients = (
        positive_perturbed_outputs - negative_perturbed_outputs
    ) / (positive_perturbed_inputs - negative_perturbed_inputs)

    # Convert the absolute coefficients to relative ones if needed
    if relative_flag:
        coefficients = coefficients * (original_inputs / unperturbed_output)

    return coefficients

def calculate_absolute_central_coefficient_errors(
        positive_perturbed_inputs,
        negative_perturbed_inputs,
        positive_perturbed_output_errors,
        negative_perturbed_output_errors
):
    
    """
    Calculates the errors of the central-differencing absolute sensitivity coefficients

    Parameters
    ----------
    positive_perturbed_inputs : ndarray
        Inputs used in simulations to obtain the outputs given in
        positive_perturbed_outputs.

    negative_perturbed_inputs : ndarray
        Inputs used in simulations to obtain the outputs given in
        negative_perturbed_outputs.

    positive_perturbed_output_errors : ndarray
        Errors of the output parameters calculated using positively-perturbed
        inputs.

    negative_perturbed_output_errors : ndarray
        Errors of the output parameters calculated using negatively-perturbed
        inputs.

    Returns
    ----------
    absolute_coefficient_errors : ndarray
        Errors of the absolute sensitivity coefficients
    """

    absolute_coefficient_errors = ((1/(positive_perturbed_inputs - negative_perturbed_inputs)) * 
                                   np.sqrt(positive_perturbed_output_errors**2 + negative_perturbed_output_errors**2))
    
    return absolute_coefficient_errors

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

def calculate_direct_perturbation_variance_error():
    """
    Calculates the error of the variance calculated from the direct 
    perturbation methodology utilizing the Sandwich Rule.

    Parameters
    ----------

    Returns
    ----------
    """

def calculate_mean_error(perturbed_output_errors):
    """
    Calculates the error of the mean perturbed output using first-order error
    propagation.

    Parameters
    ----------
    perturbed_output_errors : ndarray
        Set of errors associated with the outputs within the perturbed_outputs
        input. 

    Returns
    ----------
    mean_output_error : float
        Calculated error of the mean of the outputs given in 
        perturbed_outputs.
    """

    # Find the number of perturbed outputs
    n = len(perturbed_output_errors)

    # Calculate the variances of the perturbed outputs
    perturbed_output_variances = perturbed_output_errors**2

    # Calculate the error of the mean output
    mean_output_error = (1/n) * np.sqrt(np.sum(perturbed_output_variances))

    return mean_output_error

def calculate_random_sampling_variance_error(perturbed_outputs,
                                             mean_output,
                                             perturbed_output_errors,
                                             mean_output_error):
    """
    Calculates the error of the variance from the random sampling uncertainty
    propagation procedure.

    Parameters
    ----------
    perturbed_outputs : ndarray
        Set of output parameters calculated using inputs perturbed using 
        randomly sampled perturbation coefficients.

    mean_output : float
        Calculated error of the mean of the outputs given in 
        perturbed_outputs.

    perturbed_output_errors : ndarray
        Set of errors associated with the outputs within the perturbed_outputs
        input.

    mean_output_error : float
        Error of the mean of the perturbed outputs.

    Returns
    ----------
    variance_error : float
        Error of the variance calculated from the random sampling methodology.
    """

    # Calculate an array of new variable tau and their associated errors

    taus = (perturbed_outputs - mean_output)**2

    tau_errors = np.sqrt((2 * np.sqrt(taus))**2 * perturbed_output_errors**2 + 
                         (2 * -1  * np.sqrt(taus))**2 * mean_output_error**2)
    
    # Calculate the error of the random sampling variance

    variance_error = 1/(len(perturbed_outputs)-1) * np.sqrt(np.sum(tau_errors**2))

    return variance_error

def calculate_uncertainty_error(propagated_uncertainty,
                                variance_error):
    """
    Calculate the error of the uncertainty from a given variance. 
    This assumes that the uncertainty is given by the square root of the variance.

    Parameters
    ----------
    propagated_uncertainty : float
        Final uncertainty calculated from either the direct perturbation or random 
        sampling uncertainty propagation methodology.

    variance_error : float
        Error of the variance computed from either the direct perturbation or random 
        sampling uncertainty propagation methodology.
    
    Return
    ----------
    uncertainty_error : float
        Error of the uncertainty from the direct perturbation or random sampling
        uncertainty propagation methodologies.
    """

    # Calculate the error of the propagated final uncertainty

    uncertainty_error = variance_error / (2 * propagated_uncertainty)

    return uncertainty_error