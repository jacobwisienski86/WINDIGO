#Internal functions to assist with WINDIGO's data
#post-processing capabilities.
#Not intended to be called directly by users.

import numpy as np
import matplotlib.pyplot as plt

def check_input_types(inputs):

    modified_inputs = []
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
    
    coefficients = (positive_perturbed_outputs-unperturbed_output)/(positive_perturbed_inputs-original_inputs)

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
    
    coefficients = (unperturbed_output - negative_perturbed_outputs)/(original_inputs - negative_perturbed_inputs)

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
    
    coefficients = (positive_perturbed_outputs - negative_perturbed_outputs)/(2*perturbation_coefficient*original_inputs)

    if relative_flag:
        coefficients = coefficients * (original_inputs/unperturbed_output)

    return coefficients

def convert_per_lethargy(
        relative_sens_coefficients,
        energy_grid_MeV,
):

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