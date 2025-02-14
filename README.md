# fortran_call_tree
This project is writen in python and its purposes is to read fortran 90 code and write out a subroutine/function call tree in .dot format.  

To execute the the fctree.py code from the command line:

python fctree.py [starting point in the code] 

For example:

python fctree.py src/main.f90

The fctree.py will assume all the related fortran source files are in the same path or subdirectories to that path.