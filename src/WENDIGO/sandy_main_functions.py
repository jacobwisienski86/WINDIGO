# Main functions related to Sandy to be used with WENDIGO

def sandy_covariance_retrieval(
    energy_grid,
    nuclide,
    mt_Number,
    data_library,
    temperature,
    relative_Flag=False,
    plotting_Flag=False
):
    """
    Retrieves the covariance data using Sandy and saves it to a CSV file.
    Optionally produces a plot of the covariance data as well.

    Parameters:
        energy_grid (list): Desired energy bounds of the covariance data
        being retrieved [in eV].

        nuclide (str): Name of the nuclide whose covariance data will be
        retrieved. Formatted without hyphens (e.g. He4 instead of He-4).

        mt_Number (int): MT number corresponding to the reaction whose
        covariance data will be retrieved.

        data_library (str): Name of the data library to retrieve covariance
        data from. Some options include:
            'endfb_71'
            'endfb_80'
            'endfb_81' (development version only)

        temperature (int): Temperature at which to retrieve the covariance
        data.

        relative_Flag (Bool): Retrieve relative covariance data if True.
        Default: False.

        plotting_Flag (Bool): Produce a plot of the covariance data if True.
        Default: False.

    Results:
        csv_filename (str): Path to the file with the covariance data.

        plot_filename (str): Path to the file with the plot of the covariance
        data.
    """

    'Import necessary internal functions'

    from .sandy_internal_functions import (
        retrieve_nuclide_information,
        retrieve_covariance_data,
        plot_covariance,
        save_covariance_file
    )

    (
        "Retrieve the number used to specify which nuclide's covariance "
        "data is retrieved using Sandy"
    )

    nuclide_number = retrieve_nuclide_information(nuclide=nuclide)

    'Retrieve the covariance data using Sandy'

    covariance_data, flag_String = retrieve_covariance_data(
        energy_grid=energy_grid,
        nuclide=nuclide,
        mt_Number=mt_Number,
        data_library=data_library,
        nuclide_number=nuclide_number,
        temperature=temperature,
        relative_Flag=relative_Flag
    )

    'Create a plot of the covariance data if chosen'

    if plotting_Flag:
        plot_filename = plot_covariance(
            covariance_data=covariance_data,
            energy_grid=energy_grid,
            nuclide=nuclide,
            mt_Number=mt_Number,
            flag_String=flag_String
        )

    'Save the covariance data to a file'

    csv_filename = save_covariance_file(
        covariance_data=covariance_data,
        energy_grid=energy_grid,
        nuclide=nuclide,
        mt_Number=mt_Number,
        flag_String=flag_String
    )

    if plotting_Flag:
        return csv_filename, plot_filename
    else:
        return csv_filename

    print('Covariance Retrieval Process Complete')

sandy_covariance_retrieval(
    energy_grid = [1E-4, 20, 30000],
    nuclide = 'He4',
    mt_Number = 1,
    data_library = 'endfb_80' ,
    temperature = 300,
    relative_Flag=False,
    plotting_Flag=False
)