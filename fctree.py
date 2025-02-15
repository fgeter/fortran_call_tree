import re
import sys
import glob
import os
from func_pars_vars import *
from func_parse_allocate import *

exclusions = ["parameter"]
integer_allocatable_vars = set()
integer_allocatable_vars_with_save = set()
real_allocatable_vars = set()
real_allocatable_vars_with_save = set()
character_allocatable_vars = set()
character_allocatable_vars_with_save = set()
allocatable_types = set()
allocatable_types_with_save = set()
fortran_intrinsics = ["abs", "sqrt", "sin", "sinh", "cos", "cosh", "tan", "tanh", \
                      "asin", "acos", "atan", "atan2", "exp", "log", "log10", \
                      "int", "nint", "floor", "sqrt", "fraction", \
                      "max", "min", "mod", "modulo", "nint", "sign"]

output_folder = "./src_stage1"
try:
    os.makedirs(output_folder, exist_ok = True)
except OSError as error:
    print(f"Directory {output_folder} could not be created.")
    print(error)
if len(sys.argv) == 1:
    arg = "src/*.f90"
else:
    arg = sys.argv[1]
    arg = os.path.join(arg, "*.f90")


# The first part of the code collects the names of subroutines, functions, and modules
subroutine_names = []
function_names = []
module_names = []
for file in glob.iglob(arg):
    print("Processing file :",file)
    # ofile = file.split("/")[1]
    # opath = "/".join([output_folder, ofile])
    with open(file, errors='ignore') as fp:
        # with open(opath, "w") as ofp:
        # pf = True
        # line_num = 0
        line = fp.readline()
        # intent_vars = []
        # function_names = []
        # function_args = []
        # subroutine_names = []
        # subroutine_args = []
        # external_func = []
        # skip_vars = []
        while line:
            exe_portion = line.split("!")[0].strip().lower()
            exe_portion_list = re.split(r"\W+", exe_portion.strip())
            while '' in exe_portion_list:   # This necessary because sometimes there is a trailing '' in list
                exe_portion_list.remove('')
            # ignore_line = False
            # for v in ["function", "subroutine"]:
            #     if any(x == v for x in exe_portion_list):
            #         ignore_line = False
            #         continue
            #     else:
            #         for token in exclusions:
            #             if any(x == token for x in exe_portion_list):
            #                 ignore_line = True
            # if ignore_line:
            #     ofp.write(line)
            #     line = fp.readline()
            #     continue

            # if "function" in line.split("!")[0]:
            if len(exe_portion_list) > 0:
                if "function" == exe_portion_list[0]:
                    # function_names.append(line.split("!")[0].split()[1].split("(")[0].strip())
                    function_names.append((exe_portion_list[1], file))
                    # function_args = line.split("(")[1].split(")")[0].split(",")
                    # function_args = [i.strip() for i in function_args]
                    # ofp.write(line)
                    # line = fp.readline()
                    # continue
                # if "subroutine" in line.split("!")[0]:
                if "subroutine" == exe_portion_list[0]:
                    # subroutine_names.append(line.split("!")[0].split()[1].split("(")[0].strip())
                    subroutine_names.append((exe_portion_list[1],file))
                    # if len(line.split("(")) > 1:
                    #     subroutine_args = line.split("(")[1].split(")")[0].split(",")
                    #     subroutine_args = [i.strip() for i in subroutine_args]
                    # ofp.write(line)
                    # line = fp.readline()
                    # continue
                # if "module" == line.split("!")[0].split()[0].strip().lower():
                if "module" == exe_portion_list[0]:
                    # module_names.append(line.split("!")[0].split()[0].strip().lower())
                    module_names.append((exe_portion_list[1], file))
                    # module_names.append(line.split("!")[0].split()[1].split("(")[0].strip())
                    # if len(line.split("(")) > 1:
                    #     subroutine_args = line.split("(")[1].split(")")[0].split(",")
                    #     subroutine_args = [i.strip() for i in subroutine_args]
                    # ofp.write(line)
                    # line = fp.readline()
                    # continue
                # skip_vars = function_names + function_args + subroutine_names + subroutine_args + \
                #             intent_vars + external_func + fortran_intrinsics

            line = fp.readline()
                
print(subroutine_names)
print()
print()
print(function_names)
print()
print()
print(module_names)
print()
print()

# Second part of the code creates a dictionay representing the call tree.
# This dictionary will later be converted to .dot graph file.  
# The dictionary structure is similar to the hierarchy of .dot file. 
# The starting point is main.f90 in source path.

def recurse_code(file, dot_string):
    # global subroutine_names
    # global function_names
    with open(file, errors='ignore') as fp:
        # first make a pass through the file to collect a subroutine calls
        calls = []
        for line in fp.readlines():
            exe_portion = line.split("!")[0].strip().lower()
            exe_portion_list = re.split(r"\W+", exe_portion.strip())
            if "call" == exe_portion_list[0]:
                calls.append(exe_portion_list[1])
        # add calls to dot_string
        i = 0
        for call in calls:
            i += 1
            if i == 1:
                dot_string += "{"
            dot_string += " " + call + " "
        dot_string += "}\n"
    return dot_string


dot_string = "graph {\nrankdir=LR\nmain -- "
dot_string = recurse_code("src/main.f90", dot_string)
dot_string += "}"
print(dot_string)
with open("swatplus_call_tree.dot", "w") as wp:
    wp.write(dot_string)
                




 