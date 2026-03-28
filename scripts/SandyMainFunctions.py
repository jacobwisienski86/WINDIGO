'Main functions related to Sandy to be used with WENDIGO'

def SandyCovarianceRetrieval(energy_grid, nuclide, mt_Number, data_library, temperature, relative_Flag = False, plotting_Flag = False):
    """
    Retrieves the covariance data using Sandy and saves it to a CSV file. Optionally produces a plot of the covariance data as well.

    Parameters:
        energy_grid (list or nd_array): Desired energy bounds of the covariance data being retrieved [in eV]

        nuclide (str): Name of the nuclide whose covariance data will be retrieved
        Formatted without hyphens (e.g. He4 instead of He-4)

        mt_Number (int): MT number corresponding to the reaction whose covariance data will be retrieved for the nuclide of interest

        data_library (str): Name of the data library to retrieve covariance data from
        Some options include:
            'endfb_71'
            'endfb_80'
            'endfb_81' (Only with the development version of Sandy as of writing)

        temperature (int): Temperature at which to retrieve the covariance data for the nuclide and reaction of interest.

        relative_Flag (Bool): Flag used to determine if either the relative or absolute covariance data will be retrieved
        Default value: False

        plotting_Flag (Bool): Flag used to determine if a plot of the retrieved covariance data will be produced
        Default value: False

    Results:
        csv_filename (str): Path to the file with the covariance data

        plot_filename (str): Path to the file with the plot of the covariance data
    """

    'Import necessary internal functions'

    from SandyInternalFunctions import (retrieveNuclideInformation, 
                                        retrieveCovarianceData,
                                        plotCovariance,
                                        saveCovarianceFile)

    'Retrieve the number used to specify which nuclide''s covariance data is retrieved using Sandy'

    nuclide_number = retrieveNuclideInformation(nuclide = nuclide)

    'Retrieve the covariance data using Sandy'

    covariance_data, flag_String = retrieveCovarianceData(energy_grid = energy_grid,
                                                          nuclide = nuclide,
                                                          mt_Number = mt_Number,
                                                          data_library = data_library,
                                                          nuclide_number = nuclide_number,
                                                          temperature = temperature,
                                                          relative_Flag = relative_Flag)

    'Create a plot of the covariance data if chosen'

    if plotting_Flag:
        plot_filename = plotCovariance(covariance_data = convariance_data, 
                                       energy_grid = energy_grid, 
                                       nuclide = nuclide, 
                                       mt_Number = mt_Number, 
                                       flag_String = flag_String)

    'Save the covariance data to a file'

    saveCovarianceFile(covariance_data = covariance_data, 
                       energy_grid = energy_grid, 
                       nuclide = nuclide, 
                       mt_Number = mt_Number, 
                       flag_String = flag_String)

    if plotting_Flag:
        return csv_filename, plot_filename
    else:
        return csv_filename

    print('Covariance Retrieval Process Complete')

SandyCovarianceRetrieval(energy_grid = [1E-4, 10, 10000],
                         nuclide = 'Be9',
                         mt_Number = 2,
                         data_library = 'endfb_80',
                         temperature = 294,
                         relative_Flag = False,
                         plotting_Flag = False)



