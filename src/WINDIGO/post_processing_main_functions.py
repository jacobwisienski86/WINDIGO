#Functions adding data post-processing capabilities
#within WINDIGO.

import matplotlib.pyplot as plt
import numpy as np
from .post_processing_internal_functions import (
   check_input_types,
   calculate_forward_coefficients,
   calculate_backward_coefficients,
   calculate_central_coefficients,
   convert_per_lethargy,
   plot_relative_sens,
)

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

   inputs = [energy_grid_MeV,
             original_inputs,
             positive_perturbed_outputs,
             negative_perturbed_outputs,
             positive_perturbed_inputs,
             negative_perturbed_inputs]
   
   modified_inputs = check_input_types(inputs = inputs)

   energy_grid_MeV = modified_inputs[0]
   original_inputs = modified_inputs[1]
   positive_perturbed_outputs = modified_inputs[2]
   negative_perturbed_outputs = modified_inputs[3]
   positive_perturbed_inputs = modified_inputs[4]
   negative_perturbed_inputs = modified_inputs[5]


   #Check that a correct sensitivity coefficient calculation method has been input

   if (sens_calculation_method != 'Forward') and (sens_calculation_method != 'Backward') and (sens_calculation_method != 'Central'):
      raise Exception('Invalid sensitivity coefficient calculation method')
   
   #Calculate the relative sensitivity coefficients

   relative_flag = True

   if sens_calculation_method == 'Forward':
      relative_sens_coefficients = calculate_forward_coefficients(positive_perturbed_outputs = positive_perturbed_outputs,
                                                                  unperturbed_output = unperturbed_output,
                                                                  positive_perturbed_inputs = positive_perturbed_inputs,
                                                                  original_inputs = original_inputs,
                                                                  relative_flag = relative_flag)
   elif sens_calculation_method == 'Backward':
      relative_sens_coefficients = calculate_backward_coefficients(negative_perturbed_outputs=negative_perturbed_outputs,\
                                                                   unperturbed_output=unperturbed_output,
                                                                   negative_perturbed_inputs=negative_perturbed_inputs,
                                                                   original_inputs=original_inputs,
                                                                   relative_flag=relative_flag)

   else:
      relative_sens_coefficients = calculate_central_coefficients(positive_perturbed_outputs=positive_perturbed_outputs,
                                                                  negative_perturbed_outputs=negative_perturbed_outputs,
                                                                  unperturbed_output=unperturbed_output,
                                                                  positive_perturbed_inputs=positive_perturbed_inputs,
                                                                  negative_perturbed_inputs=negative_perturbed_inputs,
                                                                  original_inputs=original_inputs,
                                                                  perturbation_coefficient=perturbation_coefficient,
                                                                  relative_flag=relative_flag)

   relative_sens_per_lethargy = convert_per_lethargy(relative_sens_coefficients=relative_sens_coefficients,
                                                     energy_grid_MeV=energy_grid_MeV)
   
   plot_relative_sens(relative_sens_per_lethargy=relative_sens_per_lethargy,
                      energy_grid_MeV=energy_grid_MeV)



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

scale44_grid_MeV = np.array([
    1.0000E-11, 3.0000E-9, 7.5000E-9, 1.0000E-8, 2.5300E-8,
    3.0000E-8, 4.0000E-8, 5.0000E-8, 7.0000E-8, 1.0000E-7,
    1.5000E-7, 2.0000E-7, 2.2500E-7, 2.5000E-7, 2.7500E-7,
    3.2500E-7, 3.5000E-7, 3.7500E-7, 4.0000E-7, 6.2500E-7,
    1.0000E-6, 1.7700E-6, 3.0000E-6, 4.7500E-6, 6.0000E-6,
    8.1000E-6, 1.0000E-5, 3.0000E-5, 1.0000E-4, 5.5000E-4,
    3.0000E-3, 1.7000E-2, 2.5000E-2, 1.0000E-1, 4.0000E-1,
    9.0000E-1, 1.4000E0, 1.8500E0, 2.3540E0, 2.4790E0,
    3.0000E0, 4.8000E0, 6.4340E0, 8.1873E0, 2.0000E1
])


generate_relative_sensitivity_plot(energy_grid_MeV=scale44_grid_MeV,
                                   unperturbed_output=np.load('examples/Jezebel_BaseKeff_Value.npy'),
                                   sens_calculation_method='Forward',
                                   original_inputs=np.load('examples/Original_Pu239Fission_xs.npy'),
                                   positive_perturbed_outputs=np.load('examples/Jezebel_DirectKeff_Values.npy'),
                                   positive_perturbed_inputs=np.load('examples/Perturbed_Pu239Fission_xs.npy'))

calculate_direct_perturbation_uncertainty(sens_calculation_method='Forward',
                                   unperturbed_output=np.load('examples/Jezebel_BaseKeff_Value.npy'),
                                   original_inputs=np.load('examples/Original_Pu239Fission_xs.npy'),
                                   positive_perturbed_outputs=np.load('examples/Jezebel_DirectKeff_Values.npy'),
                                   positive_perturbed_inputs=np.load('examples/Perturbed_Pu239Fission_xs.npy'),
                                   covariance_matrix=np.loadtxt(open('examples/covarianceMatrix_45Groups_Pu239_MT_18_Absolute.csv', "rb"), delimiter=","))            

calculate_random_sampling_uncertainty(perturbed_outputs=np.load('examples/Jezebel_RandomKeff_Values.npy'))