# Set of internal functions involving Sandy related to the uncertainty
# quantification workflow. Not intended to be called directly when using
# the workflow.

import os
import sandy
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from WINDIGO.z_number_library import nuclide_ZZZs

def retrieve_nuclide_information(nuclide):
    """
    Retrieves the mass number and ZZZ number for a nuclide based on a
    user-input string.

    Parameters:
        nuclide (str): Nuclide whose ZZZ and mass number information will be
        retrieved. Written without hyphens (ex. H1, Mo98, U235).

    Results:
        nuclide_number (int): Number used to specify which nuclide will have
        its covariance data retrieved using Sandy.
    """

    'Grab the nuclide\'s element and mass number from the input'

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

    return nuclide_number


def retrieve_covariance_data(
    energy_grid,
    nuclide,
    mt_Number,
    data_library,
    nuclide_number,
    temperature,
    relative_Flag=False
):
    """
    Retrieves the specified covariance matrix for the nuclide and nuclear
    data of interest.

    Parameters:
        energy_grid (list): Desired energy bounds of the retrieved covariance
        data [in eV].

        nuclide (str): Nuclide whose covariance data will be retrieved.

        mt_Number (int): MT number of the nuclear covariance data to retrieve.

        data_library (str): Name of the data library to retrieve covariance
        data from.

        nuclide_number (int): ZZZAAA number of the nuclide.

        temperature (int): Temperature at which to retrieve covariance data.

        relative_Flag (Boolean): Retrieve relative covariance if True, absolute
        if False.

    Results:
        covariance_data (list or ndarray): Covariance data retrieved.

        flag_String (str): 'Relative' or 'Absolute' for naming conventions.
    """

    'Set the appropriate data type name for use in the final filenames'

    if relative_Flag:
        flag_String = 'Relative'
    else:
        flag_String = 'Absolute'

    'Retrieve the covariance data'

    errorr = sandy.get_endf6_file(
        data_library,
        "xs",
        nuclide_number
    ).get_errorr(
        err=0.1,
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

    'Select the correct MF file based upon the requested MT number'

    'Nu-Related Cov Data'
    if (mt_Number in [452, 455, 456]) is True:
        cov = errorr['errorr31'].get_cov(mts=[mt_Number])

    'Fission Spectrum-Related Cov Data'
    if (mt_Number in [1018]) is True:
        cov = errorr['errorr35'].get_cov()

    'General XS Cov Data'
    if (mt_Number not in [452, 455, 456]) and (mt_Number not in [1018]):
        cov = errorr['errorr33'].get_cov(mts=[mt_Number])

    'Save the covariance data as a separate variable and output the shape'

    covariance_data = cov.data

    print(
        'The shape of the retrieved covariance data is: '
        + str(covariance_data.shape[0])
        + ' by '
        + str(covariance_data.shape[1])
    )

    return covariance_data, flag_String


def plot_covariance(covariance_data, energy_grid, nuclide, mt_Number, flag_String):
    """
    Plots the covariance data.

    Parameters:
        covariance_data (list or ndarray): Covariance data retrieved.

        energy_grid (list): Energy grid used for covariance retrieval.

        nuclide (str): Nuclide whose covariance data was retrieved.

        mt_Number (int): MT number of the reaction.

        flag_String (str): 'Absolute' or 'Relative'.

    Results:
        plot_filename (str): Path to the saved plot.
    """

    fig, ax = plt.subplots(figsize=(8, 8), dpi=100)
    ax.set_aspect("equal")
    sns.heatmap(covariance_data, cmap='bwr')
    fig.tight_layout()

    plot_filename = (
        'covariancePlot_'
        + str(len(energy_grid))
        + 'Groups_'
        + str(nuclide)
        + 'MT'
        + str(mt_Number)
        + '_'
        + str(flag_String)
        + '.png'
    )

    plt.savefig(plot_filename, bbox_inches='tight')

    print("The covariance plot's filename is: " + str(plot_filename))

    return plot_filename


def save_covariance_file(covariance_data, energy_grid, nuclide, mt_Number, flag_String):
    """
    Save the covariance data to an initial CSV, reload to allow for formatting,
    and then save again in the finalized form.

    Parameters:
        covariance_data (ndarray): Covariance data retrieved.

        energy_grid (list): Energy grid used for covariance retrieval.

        nuclide (str): Nuclide whose covariance data was retrieved.

        mt_Number (int): MT number of the reaction.

        flag_String (str): 'Absolute' or 'Relative'.

    Results:
        csv_filename (str): Path to the saved CSV file.
    """

    covariance_data.to_csv('intermediate_dataframe.csv', index=False)

    df = pd.read_csv('intermediate_dataframe.csv', skiprows=2)

    csv_filename = (
        'covarianceMatrix_'
        + str(len(energy_grid))
        + 'Groups_'
        + str(nuclide)
        + '_MT_'
        + str(mt_Number)
        + '_'
        + str(flag_String)
        + '.csv'
    )

    df.to_csv(csv_filename, index=False, header=False)

    'Remove the intermediate CSV file'

    os.remove('intermediate_dataframe.csv')

    'Show differing output messages based on the desired outputs'

    print("The CSV's filename is: " + str(csv_filename))

    return csv_filename
