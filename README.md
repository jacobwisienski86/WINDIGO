# WINDIGO

The Workflow Integrating Nuclear Data InvestiGations into Openmc (WINDIGO) is a Python package with a set of functions to help users propagate uncertainty into OpenMC (Open Monte Carlo) calculations based on uncertainties in nuclear data more efficiently. These functions make use of the Python package SANDY (SAmpler of Nuclear Data and uncertaintY), the software FRENDY (FRom Evaluated Nuclear Data librarY), and OpenMC. WINDIGO doesn't perform any modifications to nuclear data or any simulations using said data on its own, rather it serves as a tool to make performing these tasks more efficient using pre-established codes.

# Installation and Configuration

WINDIGO can easily be installed by first cloning the repository:

```bash
git clone https://github.com/jacobwisienski86/WINDIGO.git
```

Then by navigating to the root directory of the cloned repository:

```bash
cd ./WINDIGO
```

And finally using the Python package manager pip to run:

```bash
pip install .
```

Optionally one can activate a virtual environment to add WINDIGO as a package there instead of within the user's main Python installation.


SANDY, FRENDY, and OpenMC must also be installed by the user to enable their functionality with WINDIGO. 

SANDY can generally be installed using a command line input with a Python package manager similarly to WINDIGO.

```bash 
pip install sandy
```

Additional configuration instructions and more information about SANDY can be found at its respective GitHub repository page: https://github.com/luca-fiorito-11/sandy

FRENDY and OpenMC involve more complicated configurations and specific instructions on their installation can be found within their respective webpages given below.

SANDY Documentation Homepage: https://luca-fiorito-11.github.io/sandy-docs/index.html 

OpenMC Documentation Homepage: https://docs.openmc.org/en/stable/index.html

OpenMC Installation Instructions: https://docs.openmc.org/en/stable/quickinstall.html

FRENDY Documentation Homepage: https://rpg.jaea.go.jp/main/en/program_frendy/

FRENDY Installation Instructions: https://rpg.jaea.go.jp/download/frendy/seminar/03.FRENDY_installation_ver1.5.pdf


To test that everything was installed properly and is functioning correctly, users can navigate to the root directory of the WINDIGO repository and run:
```bash
pytest
```
From the terminal to run WINDIGO's unit tests if the pytest package is installed.

Known neutron cross section libraries that SANDY can retrieve covariance data for within its latest stable release (Version 1.1) include: ENDF/B-VII.1, ENDF/B-VIII.0, JENDL-4.0u, JEFF-3.1.1, JEFF-3.2, JEFF-3.3, and TENDL-2023. Access to additional libraries for covariance retrieval, such as for ENDF/B-VIII.1, require installations of SANDY corresponding to other branches of the SANDY GitHub repository such as the develop branch.

FRENDY should be able to process any nuclear data evaluations that follow the standard ENDF-6 format. Libraries with cross section evaluations that the WINDIGO developers have tested with FRENDY include ENDF/B-VIII.0, ENDF/B-VIII.1, and FENDL-3.2c. 

*It is advised not to modify the names and locations of directories within their installation of FRENDY. Doing so will limit the operational abilities of WINDIGO as it has been written with the default configuration of FRENDY in mind with regards to navigating directories.*

# References

FRENDY:
K. Tada, A. Yamamoto, S. Kunieda, C. Konno, R. Kondo, T. Endo, G. Chiba, M. Ono, M. Tojo, "Development and verification of nuclear data processing code FRENDY version 2," J. Nucl. Sci. Technol., 61, pp.830-839 (2024).
https://www.tandfonline.com/doi/full/10.1080/00223131.2023.2278600

OpenMC:
Paul K. Romano, Nicholas E. Horelik, Bryan R. Herman, Adam G. Nelson, Benoit Forget, and Kord Smith, “OpenMC: A State-of-the-Art Monte Carlo Code for Research and Development,” Ann. Nucl. Energy, 82, 90–97 (2015).
https://www.sciencedirect.com/science/article/pii/S030645491400379X?via%3Dihub

SANDY:
L. Fiorito, G. Žerovnik, A. Stankovskiy, G. Van den Eynde, P.E. Labeau, Nuclear data uncertainty propagation to integral responses using SANDY, Annals of Nuclear Energy, Volume 101, 2017, Pages 359-366, ISSN 0306-4549.
https://www.sciencedirect.com/science/article/pii/S0306454916305278

# Acknowledgements

WINDIGO was originally developed as part of research towards a Master's of Science degree in Nuclear Engineering by Jacob Wisienski under the advisement of Dr. Stefano Terlizzi at The Pennsylvania State University.

# Contacts

[**Jacob Wisienski**](https://github.com/jacobwisienski86)

*  jacobwisienski86@gmail.com