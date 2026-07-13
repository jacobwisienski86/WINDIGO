# -- Path setup --------------------------------------------------------------

import os
import sys
sys.path.insert(0, os.path.abspath('../../src'))


# -- Project information -----------------------------------------------------

project = 'WINDIGO'
author = 'Jacob Wisienski'
copyright = '2026, The Pennsylvania State University'

version = '0.0.1'
release = '0.0.1-beta'


# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
autosummary_generate = True
exclude_patterns = []

html_theme_options = {
    "sidebar_hide_name": False,
}

html_context = {
    "override_autosummary": True,
}

# -- Options for HTML output -------------------------------------------------

html_theme = 'furo' 
html_static_path = ['_static']

html_css_files = [
    'autosummary_vertical.css',
]

autodoc_mock_imports = [
    "openmc"
]

# -- Intersphinx configuration ----------------------------------------------

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
}


