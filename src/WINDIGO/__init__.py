"""
WINDIGO: Tools for generating and manipulating nuclear data libraries,
including FRENDY ACE generation, SANDY covariance retrieval, and OpenMC
cross-section library construction.

This module exposes the public API for the WINDIGO package.
"""

from .frendy_main_functions import (
    generate_unperturbed_neutron_ace_file,
    generate_direct_perturbation_ace_files,
    generate_random_sampling_ace_files,
)

from .sandy_main_functions import (
    sandy_covariance_retrieval,
)

from .openmc_main_functions import (
    build_perturbed_cross_sections_libraries,
)

__all__ = [
    "generate_unperturbed_neutron_ace_file",
    "generate_direct_perturbation_ace_files",
    "generate_random_sampling_ace_files",
    "sandy_covariance_retrieval",
    "build_perturbed_cross_sections_libraries",
]