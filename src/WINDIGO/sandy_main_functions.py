# Main functions related to SANDY to be used with WINDIGO

# Import internal functions
from .sandy_internal_functions import (
    retrieve_nuclide_information,
    retrieve_covariance_data,
    plot_covariance,
    save_covariance_file,
)


def sandy_covariance_retrieval(
    energy_grid,
    nuclide,
    mt_Number,
    data_library,
    temperature,
    err_tolerance = 0.1,
    relative_Flag=False,
    plotting_Flag=False
):
    """
    Retrieve covariance data using Sandy and save it to a CSV file.
    Optionally produce a plot of the covariance data.

    Parameters
    ----------
    energy_grid : list
        Desired energy bounds of the covariance data being retrieved [eV].

    nuclide : str
        Name of the nuclide whose covariance data will be retrieved.
        Written without hyphens (e.g., He4 instead of He-4).

    mt_Number : int
        MT number corresponding to the reaction whose covariance data will
        be retrieved.

    data_library : str
        Name of the nuclear data library to retrieve covariance data from.
        Examples include: 'endfb_71', 'endfb_80', 'endfb_81'.

    temperature : int
        Temperature at which to retrieve covariance data.

    err_tolerance : float
        Tolerance used by NJOY to convert continuous cross section
        data to a tabulated version. Expressed as a fraction (i.e 
        err_tolerance = 0.1 means that converted cross section data
        is considered valid if it falls within 10% of the continuous
        version) 
        Default is 0.1.

    relative_Flag : bool, optional
        Retrieve relative covariance data if True. 
        Default is False.

    plotting_Flag : bool, optional
        Produce a plot of the covariance data if True. 
        Default is False.

    Returns
    -------
    csv_filename : str
        Path to the saved covariance CSV file.

    plot_filename : str, optional
        Path to the saved covariance plot file if plotting_Flag=True.
    """

    # Retrieve the nuclide number used for Sandy covariance retrieval
    nuclide_number = retrieve_nuclide_information(nuclide=nuclide)

    # Retrieve covariance data using Sandy
    covariance_data, flag_String = retrieve_covariance_data(
        energy_grid=energy_grid,
        mt_Number=mt_Number,
        data_library=data_library,
        nuclide_number=nuclide_number,
        temperature=temperature,
        err_tolerance=err_tolerance,
        relative_Flag=relative_Flag
    )

    # Create a plot of the covariance data if requested
    if plotting_Flag:
        plot_filename = plot_covariance(
            covariance_data=covariance_data,
            energy_grid=energy_grid,
            nuclide=nuclide,
            mt_Number=mt_Number,
            flag_String=flag_String
        )

    # Save the covariance data to a CSV file
    csv_filename = save_covariance_file(
        covariance_data=covariance_data,
        energy_grid=energy_grid,
        nuclide=nuclide,
        mt_Number=mt_Number,
        flag_String=flag_String
    )

    print("Covariance Retrieval Process Complete")

    if plotting_Flag:
        return csv_filename, plot_filename

    return csv_filename