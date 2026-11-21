WINDIGO Python API
==================

WINDIGO is composed of two types of functions: main and internal. 

Main functions are designed to be called directly by users when utilizing WINDIGO. 

Internal functions are called within the main functions to perform subsections of the overall 
tasks performed by the main functions. Internal functions are not intended to be called 
directly by users.

The types of functions are sorted based on either their general utility (i.e. post-processing) and 
the codes they interface with.

.. toctree::
   :maxdepth: 2

   main/index
   internal/index