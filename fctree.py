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
# for arg in sys.argv[1:]:
for file in glob.iglob(arg):
    print("Processing file :",file)
    ofile = file.split("/")[1]
    opath = "/".join([output_folder, ofile])
    with open(file, errors='ignore') as fp:
        with open(opath, "w") as ofp:
            pf = True
            line_num = 0
            declaration_line = False
            allocatable_line = False
            line = fp.readline()
            intent_vars = []
            function_names = []
            function_args = []
            subroutine_names = []
            subroutine_args = []
            external_func = []
            skip_vars = []
            while line:
                line_num += 1
                more_lines = False
                if ofile in ["ran1.f90"]:
                    ofp.write(line)
                    line = fp.readline()
                    continue
                if len(line.strip()) == 0 or  line.strip()[0] == "!":
                    ofp.write(line)
                    line = fp.readline()
                    continue
                exe_portion = line.split("!")[0]
                exe_portion_list = re.split(r"\W+", exe_portion.strip())
                while '' in exe_portion_list:   # This necessary because sometimes there is a trailing '' in list
                    exe_portion_list.remove('')
                ignore_line = False
                for v in ["function", "subroutine"]:
                    if any(x == v for x in exe_portion_list):
                        ignore_line = False
                        continue
                    else:
                        for token in exclusions:
                            if any(x == token for x in exe_portion_list):
                                ignore_line = True
                if ignore_line:
                    ofp.write(line)
                    line = fp.readline()
                    continue

                # Next handles if there is more than one allocate statement on the same line. It writes
                # one allocate statement per line perserving any comments and proper indentation.
                if exe_portion.strip().startswith("allocate"):
                    cnt_allocate =  exe_portion_list.count("allocate")
                    if cnt_allocate > 0:
                        num_leading_spaces = exe_portion.find("allocate")
                        if "!" in line:
                            comments_in_line = True
                            comments = line.split("!")[1]
                            comment_start_index = line.find("!")
                        else:
                            comments_in_line = False
                        allocate_list = line.split(";")
                        for allocate_statement in allocate_list:
                            for stmnt in parse_allocate(allocate_statement):
                                allocate_exe_portion = num_leading_spaces*" " + "allocate (" + stmnt + ")"
                                if comments_in_line:
                                    ncs = comment_start_index - len(allocate_exe_portion)
                                    new_line = allocate_exe_portion + ncs*" " + "!" + comments 
                                else:
                                    new_line = allocate_exe_portion
                                ofp.write(new_line + "\n")

                        line = fp.readline()
                        continue
                    
                if "allocatable" in exe_portion_list:
                    if "type" == exe_portion_list[0]:
                        if "save" in exe_portion_list:
                            allocatable_types_with_save.add(exe_portion_list[-1])
                        else:
                            allocatable_types.add(exe_portion_list[-1])
                        ofp.write(line)
                        line = fp.readline()
                        continue

                declaration_line = False
                if "intent" in line.split("!")[0]:
                    intent_vars.append(line.split("!")[0].split("::")[1].strip())
                    ofp.write(line)
                    line = fp.readline()
                    continue
                if "function" in line.split("!")[0]:
                    if "end" not in line.split("!")[0]:
                        function_names.append(line.split("!")[0].split()[1].split("(")[0].strip())
                        function_args = line.split("(")[1].split(")")[0].split(",")
                        function_args = [i.strip() for i in function_args]
                        ofp.write(line)
                        line = fp.readline()
                        continue
                if "subroutine" in line.split("!")[0]:
                    if "end subroutine" not in line.split("!")[0]:
                        subroutine_names.append(line.split("!")[0].split()[1].split("(")[0].strip())
                        if len(line.split("(")) > 1:
                            subroutine_args = line.split("(")[1].split(")")[0].split(",")
                            subroutine_args = [i.strip() for i in subroutine_args]
                        ofp.write(line)
                        line = fp.readline()
                        continue
                skip_vars = function_names + function_args + subroutine_names + subroutine_args + \
                            intent_vars + external_func + fortran_intrinsics
print(subroutine_names)
