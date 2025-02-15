import re
import sys
import glob
import os
from func_pars_vars import *
from func_parse_allocate import *
from collections import OrderedDict

if len(sys.argv) == 1:
    arg = "src/*.f90"
else:
    arg = sys.argv[1]
    arg = os.path.join(arg, "*.f90")

# The first part of the code collects the names of subroutines, functions, and modules
subroutine_names = {}
function_names = []
module_names = []
sub_tokens_beg = ["subroutine", "program"]
sub_tokens_end = ["endsubroutine", "end subroutine", "endprogram", "end program"]
for file in glob.iglob(arg):
    print("Processing file :",file)
    with open(file, errors='ignore') as fp:
        line = fp.readline()
        in_sub = False
        while line:
            exe_portion = line.split("!")[0].strip().lower()
            exe_portion_list = re.split(r"\W+", exe_portion.strip())
            while '' in exe_portion_list:   # This is necessary because sometimes there is a trailing '' in list
                exe_portion_list.remove('')
            if len(exe_portion_list) > 0:
                token = line.split()[0].split("(")[0].lower()
                if token in sub_tokens_beg: 
                    in_sub = True
                    sub_name = exe_portion_list[1]
                    if sub_name.lower() != "date_and_time":
                        subroutine_names.update({(sub_name,file):[]})
                if token in sub_tokens_end: 
                    in_sub = False
                if in_sub:
                    if token == "call":
                        called_sub = exe_portion_list[1].lower()
                        if called_sub != "date_and_time" and called_sub != "exit":
                            if called_sub not in subroutine_names[(sub_name,file)]:
                                subroutine_names[(sub_name,file)].append(called_sub)

            line = fp.readline()
                
# with open("sub_dict.txt", "w") as sb:
#     for x in subroutine_names.keys():
#         print(x, subroutine_names[x])
#         sb.write(str(x) + str(subroutine_names[x]) + "\n")

# Second part of the code creates an odered dictionay representing the call tree.
# This dictionary will later be converted to .dot graph file.  
def get_sub_file_name(sub_name):
    for item in subroutine_names:
        if item[0] == sub_name:
            return item[1]
    return

ordered_sub_dict = OrderedDict()

def reorder_sub_dict(sub,file):
    sub_names = subroutine_names[(sub, file)]
    ordered_sub_dict.update({(sub,file):sub_names})
    for sub in sub_names:
        file = get_sub_file_name(sub)
        reorder_sub_dict(sub, file)
    return

def convert_ordered_dict_to_dot(sub, file, dot_string):
    # advance to the start
    start = False
    for key in ordered_sub_dict.keys(): 
        if key != (sub, file) and start is False:
            continue
        else:
            start = True
            dot_string += key[0] + " -- " + "{"
            for sub in ordered_sub_dict[key]:
                dot_string += " " + sub + " "
            dot_string += "}\n"
    return dot_string
            
reorder_sub_dict("main", "src/main.f90")

with open("ordered_dict.txt", "w") as od:
    for x in ordered_sub_dict.keys():
        print(x, ordered_sub_dict[x])
        od.write(str(x) + str(ordered_sub_dict[x]) + "\n")

dot_string = "graph {\nrankdir=LR\n"
dot_string = convert_ordered_dict_to_dot("main", "src/main.f90", dot_string)
dot_string += "}"
print(dot_string)
with open("swatplus_call_tree.dot", "w") as wp:
    wp.write(dot_string)




 