#Functions adding data post-processing capabilities
#within WINDIGO.

import matplotlib.pyplot as plt
import numpy as np

def generate_relative_sensitivity_plot(
        energy_grid_MeV,
        sens_calculation_method,
        unperturbed_output,
        original_inputs,
        positive_perturbed_outputs=[],
        negative_perturbed_outputs=[],
        positive_perturbed_inputs=[],
        negative_perturbed_inputs=[],
        perturbation_coefficient=1.0,
):
   """
   Generates a relative sensitivity per unit lethargy 
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

   Returns
   ---------
      Plot of the relative sensitivity per unit lethargy of the perturbed outputs
      versus the incident neutron energy.   
   """ 

   #Ensure that parameters are ndarrays as necessary

   if type(energy_grid_MeV) is not np.ndarray:
      energy_grid_MeV = np.array(energy_grid_MeV)
   if type(original_inputs) is not np.array:
      original_inputs = np.array(original_inputs)
   if type(positive_perturbed_outputs) is not np.ndarray:
      positive_perturbed_outputs = np.array(positive_perturbed_outputs)
   if type(negative_perturbed_outputs) is not np.ndarray:
      negative_perturbed_outputs = np.array(negative_perturbed_outputs)
   if type(positive_perturbed_inputs) is not np.ndarray:
      positive_perturbed_inputs = np.array(positive_perturbed_inputs)
   if type(negative_perturbed_inputs) is not np.ndarray:
      negative_perturbed_inputs = np.array(negative_perturbed_inputs)

   #Calculate the relative sensitivity coefficients based on the 
   #chosen calculation method

   if (sens_calculation_method != 'Forward') and (sens_calculation_method != 'Backward') and (sens_calculation_method != 'Central'):
      raise Exception('Invalid sensitivity coefficient calculation method')

   if sens_calculation_method == 'Forward':
      relative_sens_coefficients = (positive_perturbed_outputs - unperturbed_output)/(positive_perturbed_inputs - original_inputs) * (original_inputs/unperturbed_output)
   elif sens_calculation_method == 'Backward':
      relative_sens_coefficients = (unperturbed_output - negative_perturbed_outputs)/(original_inputs - negative_perturbed_inputs) * (original_inputs/unperturbed_output)
   else:
      relative_sens_coefficients = (positive_perturbed_outputs - negative_perturbed_outputs)/(2*perturbation_coefficient*original_inputs) * (original_inputs/unperturbed_output)
      
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
   plt.show

def calculate_direct_perturbation_uncertainty(
      sens_calculation_method,
      covariance_matrix,
      unperturbed_output,
      original_inputs,
      positive_perturbed_outputs=[],
      negative_perturbed_outputs=[],
      positive_perturbed_inputs=[],
      negative_perturbed_inputs=[],
      perturbation_coefficient=1.0,
):
   
   if (np.shape(covariance_matrix)[0] != np.shape(covariance_matrix)[1]):
      raise Exception('Invalid covariance matrix shape. A square matrix is required.')
   
   if np.shape(covariance_matrix)[0] != len(original_inputs):
      raise Exception('Invalid data shapes. The number of rows/columns in'
      'the covariance matrix must be the same as the length of the unperturbed'
      'inputs array.')
   
   if sens_calculation_method == 'Forward':

      if (len(positive_perturbed_outputs) != len(original_inputs) or
          len(positive_perturbed_inputs) != len(original_inputs)):
         raise Exception('Invalid data shapes. All inputs and outputs arrays' \
         'must have the same length')
      
      absolute_sensitivity_coefficients = (positive_perturbed_outputs - unperturbed_output)/(positive_perturbed_inputs - original_inputs)

   elif sens_calculation_method == 'Backward':

      if (len(negative_perturbed_outputs) != len(original_inputs) or
          len(negative_perturbed_inputs) != len(original_inputs)):
         raise Exception('Invalid data shapes. All inputs and outputs arrays' \
         'must have the same length')
      
      absolute_sensitivity_coefficients = (unperturbed_output - negative_perturbed_outputs)/(original_inputs - negative_perturbed_inputs)
      
   elif sens_calculation_method == 'Central':

      if (len(positive_perturbed_outputs) != len(original_inputs) or
          len(positive_perturbed_inputs) != len(original_inputs) or
          len(negative_perturbed_inputs) != len(original_inputs) or
          len(negative_perturbed_outputs) != len(original_inputs)):
         raise Exception('Invalid data shapes. All inputs and outputs arrays' \
         'must have the same length')
      
      absolute_sensitivity_coefficients = (positive_perturbed_outputs - positive_perturbed_inputs)/(2*perturbation_coefficient*original_inputs)
      
   else:
      raise Exception('Invalid sensitivity coefficient calculation method')
   
   propagated_uncertainty = np.sqrt(absolute_sensitivity_coefficients @ covariance_matrix @ absolute_sensitivity_coefficients.T)

   print('The direct perturbatation uncertainty is: ' + str(propagated_uncertainty))

   return propagated_uncertainty
   
def calculate_random_sampling_uncertainty(
      perturbed_outputs
):
   
   if type(perturbed_outputs) is not np.ndarray:
      perturbed_outputs = np.array(perturbed_outputs)
   
   n = len(perturbed_outputs)

   mean_output = np.mean(perturbed_outputs)

   squared_distances = (perturbed_outputs - mean_output)**2

   propagated_uncertainty = np.sqrt(np.sum(squared_distances)/(n-1))

   print('The random sampling uncertainty is: ' + str(propagated_uncertainty))

   return propagated_uncertainty