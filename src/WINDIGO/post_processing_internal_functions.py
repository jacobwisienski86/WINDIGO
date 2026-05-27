#Internal functions to assist with WINDIGO's data
#post-processing capabilities.
#Not intended to be called directly by users.

import numpy as np
import matplotlib.pyplot as plt

def check_input_types(inputs):

    """
    Checks if the associated inputs are of type ndarray, and if not converts them to the ndarray data type.

    Parameters
    ----------

    inputs: list
        List of the inputs to be checked and possibly converted to the ndarray data type.

    Returns
    ----------

    modified_inputs: list
        List of the original inputs that are all formatted to the ndarray data type.

    """

    #Create a blank list to store the modified inputs

    modified_inputs = []

    #Iterate over the inputs, and convert their data type to ndarrays if necessary

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
    Calculates sensititivity coefficients using a Forward-Differencing method. Performs an additional multiplication
    to non-dimensionalize the coefficients into their relative forms if need be.

    Parameters
    ----------


   positive_perturbed_outputs: ndarray
      Outputs from simulations that utilized positively-perturbed 
      inputs.

   unperturbed_output: int
        Output from a simulation that used unperturbed inputs. This
        is the reference value that perturbed outputs deviate from.

   positive_perturbed_inputs: list or ndarray, optional
      Inputs used in simulations to obtain the outputs given in
      positive_perturbed_outputs. 

    original_inputs: list or ndarray
    Unperturbed inputs used to obtain the unperturbed simulation
    output(s) of interest.

   relative_flag: Bool
    Flag used to determine the sensitivity coefficients will be in their absolute or relative
    forms.


    Returns
    ----------

    coefficients: ndarray
        Numpy array of either relative or absolute sensitivity coefficients.
    """
    
    #Calculate the absolute sensitivity coefficients using forward-differencing

    coefficients = (positive_perturbed_outputs-unperturbed_output)/(positive_perturbed_inputs-original_inputs)

    #Convert the absolute coefficients to relative ones if need be

    if relative_flag:
        coefficients = coefficients * (original_inputs/unperturbed_output)

    return coefficients

def calculate_backward_coefficients(
        negative_perturbed_outputs,
        unperturbed_output,
        negative_perturbed_inputs,
        original_inputs,
        relative_flag
):
    
    """
    Calculates sensititivity coefficients using a Backward-Differencing method. Performs an additional multiplication
    to non-dimensionalize the coefficients into their relative forms if need be.


   negative_perturbed_outputs: list or ndarray, optional
      Outputs from simulations that utilized negatively-perturbed 
      inputs. 

    unperturbed_output: int
   Output from a simulation that used unperturbed inputs. This
   is the reference value that perturbed outputs deviate from.

   negative_perturbed_inputs: ndarray
      Inputs used in simulations to obtain the outputs given in
      negative_perturbed_outputs.
         

   original_inputs: ndarray
   Unperturbed inputs used to obtain the unperturbed simulation
   output(s) of interest.

    
    relative_flag: Bool
    Flag used to determine the sensitivity coefficients will be in their absolute or relative
    forms.
    
    Returns
    ----------

    coefficients: ndarray
        Numpy array of either relative or absolute sensitivity coefficients.
    """
    
    #Calculate the absolute sensitivity coefficients using a backward-differencing method

    coefficients = (unperturbed_output - negative_perturbed_outputs)/(original_inputs - negative_perturbed_inputs)

    #Convert the absolute coefficients to relative ones if need be
    
    if relative_flag:
        coefficients = coefficients * (original_inputs/unperturbed_output)

    return coefficients

def calculate_central_coefficients(
    positive_perturbed_outputs,
    negative_perturbed_outputs,
    unperturbed_output,
    original_inputs,
    perturbation_coefficient,
    relative_flag      
):
    
    """
    Calculates sensititivity coefficients using a Central-Differencing method. Performs an additional multiplication
    to non-dimensionalize the coefficients into their relative forms if need be.

   positive_perturbed_outputs: list or ndarray, optional
      Outputs from simulations that utilized positively-perturbed 
      inputs.

   negative_perturbed_outputs: list or ndarray, optional
      Outputs from simulations that utilized negatively-perturbed 
      inputs.

   unperturbed_output: int
   Output from a simulation that used unperturbed inputs. This
   is the reference value that perturbed outputs deviate from.

   original_inputs: list or ndarray
   Unperturbed inputs used to obtain the unperturbed simulation
   output(s) of interest.     

   perturbation_coefficient: float, optional
   Fractional multiplier used to perturb the inputs in the 
   sensitivity calculation simulations. Required for the Central 
   sensitivity coefficient calculations. Assumes that the positive
   and negative input perturbations were by the same amount. For 
   example, for 10% positive and negative perturbations, the 
   given value should be 0.1.

    relative_flag: Bool
    Flag used to determine the sensitivity coefficients will be in their absolute or relative
    forms.

    Returns
    ----------

    coefficients: ndarray
        Numpy array of either relative or absolute sensitivity coefficients.
    """
    
    #Calculate the absolute sensitivity coefficients using a central differencing method. Assumes that the positive and
    #negative perturbations were by the same multiplicative factor (ex. +10% and -10$)

    coefficients = (positive_perturbed_outputs - negative_perturbed_outputs)/(2*perturbation_coefficient*original_inputs)

    #Convert the absolute coefficients to relative ones if need be
    
    if relative_flag:
        coefficients = coefficients * (original_inputs/unperturbed_output)

    return coefficients

def convert_per_lethargy(
        relative_sens_coefficients,
        energy_grid_MeV,
):
    """
    Converts a set of relative sensitivity coefficients to being per unit lethargy
    based on a given energy grid.

    Parameters
    ----------

    relative_sens_coefficients: ndarray
        Numpy array of relative sensitivity coefficients.

    energy_grid_MeV: nd.array
        Numpy array containing the energy bounds of the perturbation intervals used for finding
        the relative sensitivity coefficients.

    Returns
    ---------

    relative_sens_per_lethargy: ndarray
        Numpy array of the relative sensitivity coefficients converted to be per
        unit lethargy.    
    """

    #Create an array of lethargy widths

    lethargy_widths = []

    for ii in range(0, len(energy_grid_MeV)-1):
        lethargy_width = np.log(energy_grid_MeV[ii+1] / energy_grid_MeV[ii])
        lethargy_widths.append(lethargy_width)

    lethargy_width = np.array(lethargy_widths)

    #Compute the relative sensitivity per lethargy

    relative_sens_per_lethargy = relative_sens_coefficients/lethargy_widths

    #Add an extra zero to relative_sens_per_lethargy to assist with plotting

    relative_sens_per_lethargy = np.insert(relative_sens_per_lethargy, 0, 0)

    return relative_sens_per_lethargy

def plot_relative_sens(
    relative_sens_per_lethargy,
    energy_grid_MeV,      
):
   
   """
    Generates a plot of the relative sensitivity coefficients per unit lethargy plotted against
    the incident neutron energy in units of MeV.

    Parameters
    ----------

    relative_sens_per_lethargy: ndarray
        Numpy array containing the relative sensitivity coefficients per unit lethargy

    energy_grid_MeV: ndarray
        Numpy array containing the energy bounds of the perturbation intervals used for finding
        the relative sensitivity coefficients.

   """

   #Plot the sensitivity profile

   fig, ax = plt.subplots(figsize = (8,6))

   ax.step(energy_grid_MeV, relative_sens_per_lethargy, color = 'black')
   ax.tick_params(axis = 'x', labelsize = 18)
   ax.tick_params(axis = 'y', labelsize = 18)
   ax.set_xscale('log')
   ax.set_xlabel('Energy (MeV)', fontsize = 18)
   ax.set_ylabel('Relative Sensitivity Per Lethargy Width', fontsize = 18)
   ax.grid()

   plt.tight_layout()
   plt.savefig('RelativeSensitivityPlot.png', dpi = 350, bbox_inches = 'tight')
   plt.show()