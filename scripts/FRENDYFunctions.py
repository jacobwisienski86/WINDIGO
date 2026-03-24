"Set of functions related to the workflow that make use of FRENDY"

def GenerateUnperturbedNeutronACEFile(frendy_Path, endf_Path, temperature, nuclide, upgrade_Flag = False, energy_Grid = [], cleanup_Flag = True):
    """ 

    Generates unperturbed neutron cross section ACE files for use in the workflow.

    Parameters:
        frendy_Path (str): Full path to the directory created by FRENDY during the installation process
            End of path should be '.../frendy_YYYYMMDD' where 'YYYYMMDD' corresponds to the date related to the version of FRENDY installed

        endf_Path (str): Full path to the ENDF evaluation for the nuclide of interest
            End of path should be '.../n-ZZZ_Y_AAA.endf' where ZZZ represents the three-digit Z number of the nuclide, Y the alphabetical name of the nuclide's element, and AAA the mass number of the nuclide
            If having difficulties, inputting as a raw string may assist

        temperature (int): Temperature at which to generate ACE file at
            Only one temperature can be specified per ACE file; creating multi-temperature libraries requires multiple ACE files for each nuclide at each temperature

        upgrade_Flag (Boolean): Flag used to determine whether the ACE file will have additional energy grid points added to increase chances of successful data perturbations
            Default: False

        energy_Grid (list or nd_array): Values of the energy grid used to determine perturbation bounds.
            Should be the same as those corresponding to the retrieval of covariance data
            Default: Empty list ([])

        cleanup_Flag (Boolean): Flag used to determine if automatic file cleanup will occur after completing the ACE file generation.
            Deletes all intermediate files leaving the final ACE file as the only new file created.
            Default: True

    """
    'Import necessary modules'

    import os
    import shutil

    'Create a .dat file to use for the ACE file generation'

    endf_file_original = endf_Path

    endf_file_intermediate = endf_file_original[:-5]

    endf_file_dat = str(endf_file_intermediate) + '.dat'

    shutil.copy2(endf_file_original, endf_file_dat)

    'Generate the input file to be run by FRENDY'

    ace_file_gen_input_filename = str(frendy_Path) + '/frendy/main/' + str(nuclide) + '_acegenerator'

    'Modify input file name based on if upgrades are specified'

    if upgrade_Flag:
        ace_file_gen_input_filename += '_upgrade.dat'
    else:
        ace_file_gen_input_filename += '_normal.dat'

    ace_file_lines = []

    'Line specifying ACE file generation mode'

    file_gen_type_line = 'ace_file_generation_fast_mode\n'

    ace_file_lines.append(file_gen_type_line)

    'Line specifying where to find the nuclear data used to create the file'

    nucl_data_file_line = '    nucl_file_name    ' + str(endf_file_dat) + '\n'

    ace_file_lines.append(nucl_data_file_line)

    'Line specifying the temperature to generate ACE file at'

    temp_line = '    temp    ' + str(temperature) + '\n'

    ace_file_lines.append(temp_line)

    'Line specifying outputted ACE file''s name'

    if upgrade_Flag: 
        ace_file_output_name_line = '    ace_file_name    ' + str(nuclide) + '_upgrade.ace\n'
    else:
        ace_file_output_name_line = '    ace_file_name    ' + str(nuclide) + '.ace\n'

    ace_file_lines.append(ace_file_output_name_line)

    'Section that performs the energy grid upgrade'

    if upgrade_Flag:

        'Generates a list of the extra energy bounds to add to the input file'

        upgrade_energy_bounds = []

        for ii in range(0, len(energy_Grid)):

            if (energy_Grid[ii] < 99.99):

                if ii == 0:

                    upgrade_energy_bounds.append(energy_Grid[ii] + (1E-6))

                elif ii == (len(energy_Grid) - 1):

                    upgrade_energy_bounds.append(energy_Grid[ii] - (1E-6))

                else:

                    upgrade_energy_bounds.append(energy_Grid[ii] - (1E-6))

                    upgrade_energy_bounds.append(energy_Grid[ii] + (1E-6))
            
            elif (energy_Grid[ii] >= 99.99) and (energy_Grid[ii] < 99990):

                if ii == 0:

                    upgrade_energy_bounds.append(energy_Grid[ii] + 0.1)

                elif ii == (len(energy_Grid) - 1):

                    upgrade_energy_bounds.append(energy_Grid[ii] - 0.1)

                else:

                    upgrade_energy_bounds.append(energy_Grid[ii] - 0.1)

                    upgrade_energy_bounds.append(energy_Grid[ii] + 0.1)

            else:

                if ii == 0:

                    upgrade_energy_bounds.append(energy_Grid[ii] + 1000)

                elif ii == (len(energy_Grid) - 1):

                    upgrade_energy_bounds.append(energy_Grid[ii] - 1000)

                else:

                    upgrade_energy_bounds.append(energy_Grid[ii] - 1000)

                    upgrade_energy_bounds.append(energy_Grid[ii] + 1000)

        'Lines that specify the additional energy grid points to add in the ACE file generation'
                
        for jj in range(0, len(upgrade_energy_bounds)):

            if jj == 0:
                
                upgraded_bound_line = '    add_grid_data    (' + str(upgrade_energy_bounds[jj]) + '\n'

                ace_file_lines.append(upgraded_bound_line)
            
            elif jj == (len(upgrade_energy_bounds) - 1):

                upgraded_bound_line = '        ' + str(upgrade_energy_bounds[jj]) + ')\n'

                ace_file_lines.append(upgraded_bound_line)

            else:

                upgraded_bound_line = '        ' + str(upgrade_energy_bounds[jj]) + '\n'

                ace_file_lines.append(upgraded_bound_line)

    
    'Write the ace file generation input'

    with open(ace_file_gen_input_filename, 'w') as file:

        file.writelines(ace_file_lines)

        file.close()

    print('The path to the ace file generation input is: ' + str(ace_file_gen_input_filename) + '\n')

    'Specifies the executable directory and the ACE file generation command'

    executable_directory = frendy_Path + '/frendy/main'

    run_command = './frendy.exe ' + str(ace_file_gen_input_filename)

    'Save the starting directory so that it can be returned to after FRENDY runs'

    starting_directory = os.getcwd()

    'Set the current directory to that of the FRENDY executable, and run the ACE file generation command'

    os.chdir(executable_directory)

    os.system(str(run_command))

    'Return to the starting directory after FRENDY runs'

    os.chdir(starting_directory)

    'First portion of the optional intermediate file cleanup'

    if cleanup_Flag:

        os.remove(endf_file_dat)

        os.remove(ace_file_gen_input_filename)

    'Specify output ACE file''s name for printing later, and perform any remaining file cleanup if need be'

    if upgrade_Flag: 

        output_file_path = executable_directory + '/' + str(nuclide) + '_upgrade.ace'

        if cleanup_Flag:

            os.remove(executable_directory + '/' +str(nuclide) + '_upgrade.ace.ace.dir')

            print('Intermediate Files Removed')

    else:

        output_file_path = executable_directory + '/' + str(nuclide) + '.ace'

        if cleanup_Flag:

            os.remove(executable_directory + '/' + str(nuclide) + '.ace.ace.dir')

            print('Intermediate Files Removed')

    'Check if the ACE file was successfully generated, and output the corresponding path'
    'Otherwise, give an error message'

    if os.path.exists(output_file_path):
        print('\n')
        print("ACE file successfully generated. The path to it is: " + str(output_file_path))
    else:
        print('\n')
        print("ACE file couldn''t generate; consult terminal output for assistance")

    


