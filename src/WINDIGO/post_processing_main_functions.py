# Functions adding data post-processing capabilities
# within WINDIGO.

import numpy as np
from .post_processing_internal_functions import (
    check_input_types,
    calculate_forward_coefficients,
    calculate_backward_coefficients,
    calculate_central_coefficients,
    convert_per_lethargy,
    plot_relative_sens,
    calculate_mean_error,
    calculate_random_sampling_variance_error,
    calculate_uncertainty_error,
)


def generate_relative_sensitivity_plot(
    energy_grid_MeV,
    sens_calculation_method,
    unperturbed_output,
    original_inputs,
    positive_perturbed_outputs=None,
    negative_perturbed_outputs=None,
    positive_perturbed_inputs=None,
    negative_perturbed_inputs=None,
    perturbation_coefficient=1.0,
):
    """
    Generates a relative sensitivity per lethargy width 
    plot of the outputs with respect to incident neutron
    energy.

    Parameters
    ----------
    energy_grid_MeV: list or ndarray
        Grid defining the energy bounds used to perturb inputs
        in MeV

    sens_calculation_method: str
        Desired method used to calculate sensitivity coefficients.
        Options: Forward, Backward, Central

    unperturbed_output: int
        Output from a simulation that used unperturbed inputs. This
        is the reference value that perturbed outputs deviate from.

    original_inputs: list or ndarray
        Unperturbed inputs used to obtain the unperturbed simulation
        output(s) of interest.

    positive_perturbed_outputs: list or ndarray, optional
        Outputs from simulations that utilized positively-perturbed 
        inputs. Required for Forward and Central sensitivity coefficient
        calculations.
        Default is blank list.

    negative_perturbed_outputs: list or ndarray, optional
        Outputs from simulations that utilized negatively-perturbed 
        inputs. Required for Backward and Central sensitivity coefficient
        calculations.
        Default is blank list.   

    positive_perturbed_inputs: list or ndarray, optional
        Inputs used in simulations to obtain the outputs given in
        positive_perturbed_outputs. Required for the Forward sensitivity
        coefficient calculations.
        Default is blank list.

    negative_perturbed_inputs: list or ndarray, optional
        Inputs used in simulations to obtain the outputs given in
        negative_perturbed_outputs. Required for the Backward sensitivity
        coefficient calculations.
        Default is blank list.      

    perturbation_coefficient: float, optional
        Fractional multiplier used to perturb the inputs in the 
        sensitivity calculation simulations. Required for the Central 
        sensitivity coefficient calculations. Assumes that the positive
        and negative input perturbations were by the same amount. For 
        example, for 10% positive and negative perturbations, the 
        given value should be 0.1.
        Default is 1.0.

    """

    # Ensure that parameters are ndarrays as necessary

    if positive_perturbed_outputs is None:
        positive_perturbed_outputs = []
    if negative_perturbed_outputs is None:
        negative_perturbed_outputs = []
    if positive_perturbed_inputs is None:
        positive_perturbed_inputs = []
    if negative_perturbed_inputs is None:
        negative_perturbed_inputs = []

    inputs = [
        energy_grid_MeV,
        original_inputs,
        positive_perturbed_outputs,
        negative_perturbed_outputs,
        positive_perturbed_inputs,
        negative_perturbed_inputs,
    ]

    modified_inputs = check_input_types(inputs=inputs)

    energy_grid_MeV = modified_inputs[0]
    original_inputs = modified_inputs[1]
    positive_perturbed_outputs = modified_inputs[2]
    negative_perturbed_outputs = modified_inputs[3]
    positive_perturbed_inputs = modified_inputs[4]
    negative_perturbed_inputs = modified_inputs[5]

    # Check that a correct sensitivity coefficient calculation method has been input

    if (
        (sens_calculation_method != 'Forward')
        and (sens_calculation_method != 'Backward')
        and (sens_calculation_method != 'Central')
    ):
        raise Exception('Invalid sensitivity coefficient calculation method')

    # Calculate the relative sensitivity coefficients

    relative_flag = True

    if sens_calculation_method == 'Forward':
        relative_sens_coefficients = calculate_forward_coefficients(
            positive_perturbed_outputs=positive_perturbed_outputs,
            unperturbed_output=unperturbed_output,
            positive_perturbed_inputs=positive_perturbed_inputs,
            original_inputs=original_inputs,
            relative_flag=relative_flag,
        )

    elif sens_calculation_method == 'Backward':
        relative_sens_coefficients = calculate_backward_coefficients(
            negative_perturbed_outputs=negative_perturbed_outputs,
            unperturbed_output=unperturbed_output,
            negative_perturbed_inputs=negative_perturbed_inputs,
            original_inputs=original_inputs,
            relative_flag=relative_flag,
        )

    elif sens_calculation_method == 'Central':
        relative_sens_coefficients = calculate_central_coefficients(
            positive_perturbed_outputs=positive_perturbed_outputs,
            negative_perturbed_outputs=negative_perturbed_outputs,
            unperturbed_output=unperturbed_output,
            original_inputs=original_inputs,
            perturbation_coefficient=perturbation_coefficient,
            relative_flag=relative_flag,
        )

    else:
        raise Exception(
            "Invalid sensitivity coefficient calculation method. Please use either 'Forward', 'Backward', or 'Central'. "
        )

    # Calculate the relative sensitivity per lethargy width

    relative_sens_per_lethargy = convert_per_lethargy(
        relative_sens_coefficients=relative_sens_coefficients,
        energy_grid_MeV=energy_grid_MeV,
    )

    # Generate the relative sensitivity plot

    plot_relative_sens(
        relative_sens_per_lethargy=relative_sens_per_lethargy,
        energy_grid_MeV=energy_grid_MeV,
    )


def calculate_direct_perturbation_uncertainty(
    sens_calculation_method,
    covariance_matrix,
    unperturbed_output,
    original_inputs,
    positive_perturbed_outputs=None,
    negative_perturbed_outputs=None,
    positive_perturbed_inputs=None,
    negative_perturbed_inputs=None,
    perturbation_coefficient=1.0,
):

    """
    Calculates the propagated uncertainty from direct perturbation method
    outputs and an inputted covariance matrix using the Sandwich Rule.

    Parameters
    ----------
    sens_calculation_method: str
        Desired method used to calculate sensitivity coefficients.
        Options: Forward, Backward, Central

    covariance_matrix: list or ndarray
        Matrix representing the covariances between the original inputs 
        that are subsequently altered as part of the direct perturbation 
        uncertainty quantification procedure.

    unperturbed_output: int
        Output from a simulation that used unperturbed inputs. This
        is the reference value that perturbed outputs deviate from.

    original_inputs: list or ndarray
        Unperturbed inputs used to obtain the unperturbed simulation
        output(s) of interest.

    positive_perturbed_outputs: list or ndarray, optional
        Outputs from simulations that utilized positively-perturbed 
        inputs. Required for Forward and Central sensitivity coefficient
        calculations.
        Default is blank list.

    negative_perturbed_outputs: list or ndarray, optional
        Outputs from simulations that utilized negatively-perturbed 
        inputs. Required for Backward and Central sensitivity coefficient
        calculations.
        Default is blank list.   

    positive_perturbed_inputs: list or ndarray, optional
        Inputs used in simulations to obtain the outputs given in
        positive_perturbed_outputs. Required for the Forward sensitivity
        coefficient calculations.
        Default is blank list.

    negative_perturbed_inputs: list or ndarray, optional
        Inputs used in simulations to obtain the outputs given in
        negative_perturbed_outputs. Required for the Backward sensitivity
        coefficient calculations.
        Default is blank list.      

    perturbation_coefficient: float, optional
        Fractional multiplier used to perturb the inputs in the 
        sensitivity calculation simulations. Required for the Central 
        sensitivity coefficient calculations. Assumes that the positive
        and negative input perturbations were by the same amount. For 
        example, for 10% positive and negative perturbations, the 
        given value should be 0.1.
        Default is 1.0.

    Returns
    ----------
    float
        Calculated uncertainty of the outputs due to the uncertainties
        of the inputs from the inputted covariance matrix.
    """

    # Check that the inputted covariance matrix is square

    if (np.shape(covariance_matrix)[0] != np.shape(covariance_matrix)[1]):
        raise Exception(
            'Invalid covariance matrix shape. A square matrix is required.'
        )

    # Check that the length of the sensitivity array is the same as the number of rows/columns in the covariance matrix

    if np.shape(covariance_matrix)[0] != len(original_inputs):
        raise Exception(
            'Invalid data shapes. The number of rows/columns in'
            'the covariance matrix must be the same as the length of the unperturbed'
            'inputs array.'
        )

    # Set the flag to calculate absolute sensitivity coefficients 

    relative_flag = False

    # Check if data inputs have the right shapes based on the sensitivity coefficient calculation method, and calculate the sensitivity coefficients

    if positive_perturbed_outputs is None:
        positive_perturbed_outputs = []
    if negative_perturbed_outputs is None:
        negative_perturbed_outputs = []
    if positive_perturbed_inputs is None:
        positive_perturbed_inputs = []
    if negative_perturbed_inputs is None:
        negative_perturbed_inputs = []

    if sens_calculation_method == 'Forward':

        if (
            (len(positive_perturbed_outputs) != len(original_inputs))
            or (len(positive_perturbed_inputs) != len(original_inputs))
        ):
            raise Exception(
                'Invalid data shapes. All inputs and outputs arrays'
                'must have the same length'
            )

        absolute_sensitivity_coefficients = calculate_forward_coefficients(
            positive_perturbed_outputs=positive_perturbed_outputs,
            unperturbed_output=unperturbed_output,
            positive_perturbed_inputs=positive_perturbed_inputs,
            original_inputs=original_inputs,
            relative_flag=relative_flag,
        )

    elif sens_calculation_method == 'Backward':

        if (
            (len(negative_perturbed_outputs) != len(original_inputs))
            or (len(negative_perturbed_inputs) != len(original_inputs))
        ):
            raise Exception(
                'Invalid data shapes. All inputs and outputs arrays'
                'must have the same length'
            )

        absolute_sensitivity_coefficients = calculate_backward_coefficients(
            negative_perturbed_outputs=negative_perturbed_outputs,
            unperturbed_output=unperturbed_output,
            negative_perturbed_inputs=negative_perturbed_inputs,
            original_inputs=original_inputs,
            relative_flag=relative_flag,
        )

    elif sens_calculation_method == 'Central':

        if (
            (len(positive_perturbed_outputs) != len(original_inputs))
            or (len(negative_perturbed_outputs) != len(original_inputs))
        ):
            raise Exception(
                'Invalid data shapes. All inputs and outputs arrays'
                'must have the same length'
            )

        absolute_sensitivity_coefficients = calculate_central_coefficients(
            positive_perturbed_outputs=positive_perturbed_outputs,
            negative_perturbed_outputs=negative_perturbed_outputs,
            unperturbed_output=unperturbed_output,
            original_inputs=original_inputs,
            perturbation_coefficient=perturbation_coefficient,
            relative_flag=relative_flag,
        )

    else:
        raise Exception('Invalid sensitivity coefficient calculation method')

    # Calculate the uncertainty using the sensitivity coefficients and covariance matrix

    propagated_uncertainty = np.sqrt(
        absolute_sensitivity_coefficients
        @ covariance_matrix
        @ absolute_sensitivity_coefficients.T
    )

    # Print the calculated unceratainty

    print(
        'The direct perturbatation uncertainty is: '
        + str(propagated_uncertainty)
    )

    return propagated_uncertainty


def calculate_random_sampling_uncertainty(perturbed_outputs,
                                          error_propagation_flag = False,
                                          perturbed_output_errors = None,
                                          ):
    """
    Calculates the standard deviation of a set of perturbed outputs. 
    This standard deviation serves as the uncertainty calculated using 
    the random sampling method.

    Parameters
    ----------
    perturbed_outputs: list or ndarray
        Set of output parameters calculated using inputs perturbed using 
        randomly sampled perturbation coefficients.

    error_propagation_flag: bool, optional
        Flag to determine if first-order error propagation to obtain the uncertainty 
        of the calculated random sampling uncertainty. 
        Default is False.

    perturbed_output_errors: list or ndarray
        Set of errors associated with the outputs within the perturbed_outputs
        input. Required to perform first-order error propagation.
        Default is None. 

    Returns
    ----------
    propagated_uncertainty: float
        Calculated uncertainty of the outputs due to the uncertainties
        of the inputs. Assumes that the propagated uncertainty to the outputs
        is the square root of the variance of the perturbed outputs. 

    uncertainty_error: float
        Propagated error associated with propagated_uncertainty calculated
        using a simple first-order error propagation scheme.
    """

    # Check that the type of perturbed_outputs is np.ndarray, and change to it if necessary
    if type(perturbed_outputs) is not np.ndarray:
        perturbed_outputs = np.array(perturbed_outputs)

    # Check if perturbed_output_errors was given, and convert it to a np.ndarray if necessary
    if (perturbed_output_errors != None) and type(perturbed_output_errors) is not np.ndarray:
        perturbed_output_errors =  np.array(perturbed_output_errors)

    # Find the total number of perturbed outputs
    n = len(perturbed_outputs)

    # Calculate the mean of the perturbed outputs
    mean_output = np.mean(perturbed_outputs)

    # Calcuate the error of the mean of the perturbed outputs
    if (error_propagation_flag) and (perturbed_output_errors != None):
        mean_output_error = calculate_mean_error(
            perturbed_output_errors = perturbed_output_errors
            )
    
    # Find the squared distances between the individual perturbed outputs and the mean perturbed output
    squared_distances = (perturbed_outputs - mean_output) ** 2

    # Calculate the random sampling uncertainty
    propagated_uncertainty = np.sqrt(np.sum(squared_distances) / (n - 1))

    # Calcuate the error of the random sampling variance and uncertainty
    if error_propagation_flag:
        variance_error = calculate_random_sampling_variance_error(
            perturbed_outputs=perturbed_outputs,
            mean_output=mean_output,
            perturbed_output_errors=perturbed_output_errors,
            mean_output_error=mean_output_error
            )
        
        uncertainty_error = calculate_uncertainty_error(
            propagated_uncertainty=propagated_uncertainty,
            variance_error=variance_error
        )
    if (error_propagation_flag) and (uncertainty_error != None):
        # Print the random sampling uncertainty and its associated error
        print('The random sampling uncertainty is: ' + str(propagated_uncertainty) + '± ' + str(uncertainty_error))
    else:
        # Print the random sampling uncertainty 
        print('The random sampling uncertainty is: ' + str(propagated_uncertainty))

    return propagated_uncertainty, uncertainty_error
