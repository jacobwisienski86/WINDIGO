# WINDIGO

The Workflow Integrating Nuclear Data InvestiGations into Openmc (WINDIGO) is a Python package with a set of functions that are useful for allowing users to propagate uncertainty into OpenMC (Open Monte Carlo) calculations based on uncertainties in nuclear data. These functions make use of the Python package SANDY (SAmpler of Nuclear Data and uncertaintY) and the software FRENDY (FRom Evaluated Nuclear Data librarY). WINDIGO doesn't perform any modifications to nuclear data or any simulations using it on its own, rather it serves as a tool to make performing these functions more efficient using pre-established codes.

# Installation and Configuration

WINDIGO can easily be installed from the command line using a Python package manager such as pip. 

```bash
pip install WINDIGO
```

SANDY, FRENDY, and OpenMC must also be installed by the user to enable their functionality with WINDIGO. 

SANDY can generally be installed using a command line input similarly to WINDIGO.

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

**It is imperative that prospective users of WINDIGO do not modify the names and locations of directories within their installation of FRENDY. Doing so will limit the operational abilities of WINDIGO as it has been written with the default configuration of FRENDY in mind with regards to navigating directories. This is not an issue with SANDY and OpenMC as WINDIGO relies upon their Python API instead of navigating their specific directories.**

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

WINDIGO was originally developed as part of research towards a Master's of Science degree in Nuclear Engineering by Jacob Wisienski under the advisement of Dr. Stefano Terlizzi at the Pennsylvania State University.

## Contacts

[**Jacob Wisienski**](https://github.com/jacobwisienski86)

*  jacobwisienski86@gmail.com