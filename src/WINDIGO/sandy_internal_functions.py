# Internal functions involving SANDY for WINDIGO.
# These functions are not intended to be called directly by users.

import os
import sandy
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from .z_number_library import nuclide_ZZZs


def retrieve_nuclide_information(nuclide):
    """
    Retrieve the mass number and ZZZ number for a nuclide based on a
    user-input string.

    Parameters
    ----------
    nuclide : str
        Nuclide whose ZZZ and mass number information will be retrieved.
        Written without hyphens (e.g., H1, Mo98, U235).

    Returns
    -------
    int
        ZZZAAA-style integer used to specify the nuclide in Sandy.
    """
    # Extract element symbol and mass number from input string
    nuclide_element_name = ''
    nuclide_mass_number = ''

    for character in nuclide:
        if character.isalpha():
            nuclide_element_name += character
        else:
            nuclide_mass_number += character

    nuclide_mass_number = int(nuclide_mass_number)

    # Retrieve ZZZ number from lookup table
    nuclide_ZZZ_number = int(nuclide_ZZZs[nuclide_element_name])

    # Compute ZZZAAA number
    nuclide_number = 10000 * nuclide_ZZZ_number + 10 * nuclide_mass_number

    return nuclide_number


def retrieve_covariance_data(
    energy_grid,
    mt_Number,
    data_library,
    nuclide_number,
    temperature,
    err_tolerance,
    relative_Flag=False
):
    """
    Retrieve the specified covariance matrix for the nuclide and nuclear
    data of interest.

    Parameters
    ----------
    energy_grid : list
        Desired energy bounds of the retrieved covariance data [eV].

    mt_Number : int
        MT number of the nuclear covariance data to retrieve.

    data_library : str
        Name of the data library to retrieve covariance data from.
        Known options for the current stable release of SANDY include:
        endfb_80, endfb_71, irdff_2, jeff_311, jeff_32, jeff_33,
        jendl_40u, and tendl_2023

    nuclide_number : int
        ZZZAAA number of the nuclide.

    temperature : int
        Temperature at which to retrieve covariance data.

    err_tolerance : float
        Tolerance used by NJOY to convert continuous cross section
        data to a tabulated version. Expressed as a fraction (i.e 
        err_tolerance = 0.1 means that converted cross section data
        is considered valid if it falls within 10% of the continuous
        version) Default is 0.1.

    relative_Flag : bool, optional
        Retrieve relative covariance if True, absolute if False.

    Returns
    -------
    covariance_data : ndarray
        Retrieved covariance matrix.

    flag_String : str
        'Relative' or 'Absolute'.
    """
    # Determine covariance type label
    flag_String = 'Relative' if relative_Flag else 'Absolute'

    # Retrieve covariance data from Sandy
    errorr = sandy.get_endf6_file(
        data_library,
        "xs",
        nuclide_number
    ).get_errorr(
        err=err_tolerance,
        temperature=temperature,
        errorr_kws=dict(
            ek=energy_grid,
            nubar=True,
            mubar=True,
            chi=True,
            xs=True,
            relative=relative_Flag
        ),
        groupr_kws=dict(ek=energy_grid)
    )

    # Select correct MF block based on MT number
    if mt_Number in [452, 455, 456]:
        cov = errorr['errorr31'].get_cov(mts=[mt_Number])
    elif mt_Number in [1018]:
        cov = errorr['errorr35'].get_cov()
    else:
        cov = errorr['errorr33'].get_cov(mts=[mt_Number])

    covariance_data = cov.data

    print(
        "The shape of the retrieved covariance data is: "
        f"{covariance_data.shape[0]} by {covariance_data.shape[1]}"
    )

    return covariance_data, flag_String


def plot_covariance(covariance_data, energy_grid, nuclide, mt_Number, flag_String):
    """
    Plot the covariance data.

    Parameters
    ----------
    covariance_data : ndarray
        Covariance data retrieved.

    energy_grid : list
        Energy grid used for covariance retrieval.

    nuclide : str
        Nuclide whose covariance data was retrieved.

    mt_Number : int
        MT number of the reaction.

    flag_String : str
        'Absolute' or 'Relative'.

    Returns
    -------
    str
        Path to the saved plot.
    """
    fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
    ax.set_aspect("equal")
    sns.heatmap(covariance_data, cmap='bwr')
    fig.tight_layout()

    plot_filename = (
        "covariancePlot_"
        f"{len(energy_grid)-1}Groups_"
        f"{nuclide}MT{mt_Number}_"
        f"{flag_String}.png"
    )

    plt.savefig(plot_filename, bbox_inches='tight')

    print(f"The covariance plot's filename is: {plot_filename}")

    return plot_filename


def save_covariance_file(covariance_data, energy_grid, nuclide, mt_Number, flag_String):
    """
    Save the covariance data to an initial CSV, reload it for formatting,
    and then save again in finalized form.

    Parameters
    ----------
    covariance_data : ndarray
        Covariance data retrieved.

    energy_grid : list
        Energy grid used for covariance retrieval.

    nuclide : str
        Nuclide whose covariance data was retrieved.

    mt_Number : int
        MT number of the reaction.

    flag_String : str
        'Absolute' or 'Relative'.

    Returns
    -------
    str
        Path to the saved CSV file.
    """
    covariance_data.to_csv('intermediate_dataframe.csv', index=False)

    df = pd.read_csv('intermediate_dataframe.csv', skiprows=2)

    csv_filename = (
        "covarianceMatrix_"
        f"{len(energy_grid)-1}Groups_"
        f"{nuclide}_MT_{mt_Number}_"
        f"{flag_String}.csv"
    )

    df.to_csv(csv_filename, index=False, header=False)

    # Remove intermediate CSV
    os.remove('intermediate_dataframe.csv')

    print(f"The CSV's filename is: {csv_filename}")

    return csv_filename