"Set of functions involving Sandy related to the uncertainty quantification workflow"

def CovarianceRetrieval(energy_grid, nuclide, mt_Number, data_library, temperature = 294, rel_Flag = False, plotting_Flag = False):
    """
    Retrieves the specified covariance matrix for the nuclide and nuclear data of interest.

    Parameters:

        energy_grid (list or nd_array): Desired energy bounds of the retrieved covariance data [in eV]

        nuclide (str): Nuclide whose covariance data will be retrieved
            Written without using hyphens (ex. H1, Mo98, U235, etc.)

        mt_Number (list or nd_array): MT number of the nuclear covariance data to be retrieved

        data_library (str): Name of the data library to retrieve covariance data from
            Some options include:
                'endfb_71'
                'endfb_80'
                'endfb_81' (Only with the development version of Sandy as of writing)
        
        rel_Flag (Boolean): Flag used to determine what type of covariance data will be retrieved.
            'True' will retrieve relative covariance data, and 'False' will retrieve absolute covariance data
            Default: False

        plotting_Flag (Boolean): Flag used to determine if a plot of the covariance data will be produced as part of the data retrieval process.
            Default: False

    Returns:

        csv_filename (str): Name of the file where the retrieved covariance data has been saved

        plot_filename (str): Name of the file where the plotted covariance data has been saved
            Optional: Depends on if plot creation was chosen

    """
    'Import needed modules regardless of specific functionality chosen'

    import numpy as np
    import pandas as pd
    import os
    import sandy
    from ZNumberLibrary import (nuclide_ZZZs,)


    'Ensure that the energy grid and mt number are formatted as Numpy arrays'

    if type(energy_grid) != 'nd_array':
        energy_grid = np.array(energy_grid)

    if type(mt_Number) != 'nd_array':
        mt_Number = np.array(mt_Number)

    'Set the appropriate data type name for use in the final filenames'

    if rel_Flag:
        flag_String = 'Relative'
    else:
        flag_String = 'Absolute'

    'Grab the nuclide''s element and mass number from the input'
    nuclide_element_name = ''
    nuclide_mass_number = ''

    for character in nuclide:
        if character.isalpha():
            nuclide_element_name += character
        else:
            nuclide_mass_number += character
    
    nuclide_mass_number = int(nuclide_mass_number)

    'Grab the ZZZ number of the nuclide using a pregenerated library'

    nuclide_ZZZ_number = nuclide_ZZZs[nuclide_element_name]

    nuclide_ZZZ_number = int(nuclide_ZZZ_number)

    'Compute the nuclide number input to be used in the covariance retrieval'

    nuclide_number = 10000 * nuclide_ZZZ_number + 10 * nuclide_mass_number

    'Retrieve the covariance data'

    errorr = sandy.get_endf6_file(data_library, 
                                "xs", 
                                nuclide_number).get_errorr(ek = energy_grid,
                                                           temperature = temperature,
                                                           errorr_kws = dict(err = 0.1, 
                                                           nubar = True,
                                                           mubar = True,
                                                           chi = True,
                                                           xs = True,
                                                           relative = rel_Flag),
                                                           groupr_kws = dict(ef = energy_grid))

    'Select the correct MF file based upon the requested MT number'
    'Currently not configured to retrieve mubar (angular distribution) data'
    
    'Nu-Related Cov Data'
    if (mt_Number in [452, 455, 456]) == True:
        cov = errorr['errorr31'].get_cov(mts = mtNumber)

    'Fission Spectrum-Related Cov Data'
    if (mt_Number in [1018]) == True:
        cov = errorr['errorr35'].get_cov(mts = mtNumber)

    'General XS Cov Data'
    if (mt_Number not in [452, 455, 456]) and (mt_Number not in [1018]):
        cov = errorr['errorr33'].get_cov(mts = mtNumber)

    'Save the covariance data as a separate variable and output the data''s shape to assist with debugging'

    covariance_data = cov.data_library

    print('The shape of the retrieved covariance data is: ' + str(covariance_data.shape[0]) + ' by ' +str(convariance_data.shape[1]))

    'Plot the covariance data and save image to a file'

    if plotting_Flag:
        import matplotlib.pyplot as plt 
        import seaborn as sns

        fig, ax = plt.subplots(figsize = (8,8), dpi = 100)
        ax.set_aspect("equal")
        sns.heatmap(covariance_data, cmap = 'bwr')
        fig.tight_layout()
        
        plot_filename = 'covariancePlot_' + str(len(energy_grid)) + 'Groups_' + str(nuclide) + 'MT' + str(mt_Number[0]) + '_' + str(flag_String) + '.png'

        plt.savefig(plot_filename, bbox_inches = 'tight')

    'Save the covariance data to an initial CSV, reload to allow for formatting, and then save again in the finalized form'

    covariance_data.to_csv('intermediate_dataframe.csv', index = False)

    df = pd.read_csv('intermediate_dataframe.csv', skiprows = 2)

    csv_filename = 'covarianceMatrix_' + str(len(energy_grid)) + 'Groups_' + str(nuclide) + 'MT' + str(mt_Number[0]) + '_' + str(flag_String) + '.csv'

    df.to_csv(csv_filename, index= False, header = False)

    'Remove the intermediate CSV file'

    os.remove('intermediate_dataframe.csv')
    
    'Show differing output messages based on the desired outputs'

    if plotting_Flag:

        return "The CSV's filename is: " + str(csv_filename) + " And the plot's filename is: " + str(plot_filename)

    return "The CSV's filename is: " + str(csv_filename)