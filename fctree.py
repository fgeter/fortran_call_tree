# Author fgeter@gmail.com 
# Purpose of this code to is analyze fortran 90 code and produce a call tree in .dot graphviz format

import re
import glob
import os
from collections import OrderedDict
import argparse
# import graphviz

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--source", type=str, nargs='?', const=1, default="./src", 
    help="The relative path to the fortran source code directory. Default value = './src'")

    parser.add_argument("-b", "--beginning_subroutine", type=str, nargs='?', const=1, default="main", 
    help="The starting subroutine to begin the .dot tree from. Default value = 'main'")

    args = parser.parse_args()

    arg = os.path.join(args.source, "*.[fF]9[05]")  # Note: Patterns do not work with iglob, only glob

    # The first part of the code collects the names of subroutines, functions, and modules
    subroutine_names = {}
    function_names = []
    module_names = []
    sub_tokens_beg = ["subroutine", "program"]
    sub_tokens_end = ["endsubroutine", "end subroutine", "endprogram", "end program"]
    exclude_builtin_subroutines = ["exit", "date_and_time", "system"]
    for file in glob.glob(arg):
        # print("Processing file :",file)
        with open(file, errors='ignore') as fp:
            line = fp.readline()
            in_sub = False
            while line:
                exe_portion = line.split("!")[0].strip().lower()
                exe_portion_list = re.split(r"\W+", exe_portion.strip())
                while '' in exe_portion_list:   # This is necessary because sometimes there is a trailing '' in list
                    exe_portion_list.remove('')
                if len(exe_portion_list) > 0:
                    # Add subroutines names and paths
                    token = line.split()[0].split("(")[0].lower()
                    if token in sub_tokens_beg: 
                        in_sub = True
                        sub_name = exe_portion_list[1]
                        if (sub_name, file) not in subroutine_names:
                            subroutine_names.update({(sub_name, file):[]})
                    if token in sub_tokens_end: 
                        in_sub = False
                    if in_sub:
                        if "call" in exe_portion_list:
                            call_index = exe_portion_list.index("call")
                            called_sub = exe_portion_list[call_index + 1].lower()
                            if called_sub not in exclude_builtin_subroutines:
                                if called_sub not in subroutine_names[(sub_name,file)]:
                                    subroutine_names[(sub_name,file)].append(called_sub)
                line = fp.readline()
                    
    with open("sub_dict.txt", "w") as sb:
        for x in subroutine_names.keys():
            # print(x, subroutine_names[x])
            sb.write(str(x) + str(subroutine_names[x]) + "\n")


    # Second part of the code takes the subroutine_names dictionary and
    # creates an odered dictionay representing the call tree starting from
    # an input subroutines. If not input subroutined is provided, the
    # default will be main.  
    # This ordered dictionary will later be converted to .dot graph file.  

    def get_sub_file_name(sub_name):
        for item in subroutine_names:
            if item[0] == sub_name:
                return item[1]
        return

    ordered_sub_dict = OrderedDict()
    unused_subroutines = set()
    seq_list = []

    def reorder_sub_dict(sub,file):
        """ Reorders the subroutines_names to the order in which they are called"""
        sub_names = subroutine_names[(sub, file)]
        ordered_sub_dict.update({(sub,file):sub_names})
        for sub in sub_names:
            file = get_sub_file_name(sub)
            reorder_sub_dict(sub, file)
        return

    def convert_ordered_dict_to_dot(sub, file, dot_string):
        """ Converts the reordered subroutine dictionary to .dot file."""
        # advance to the start
        start = False
        for key in ordered_sub_dict.keys(): 
            if key != (sub, file) and start is False:
                continue
            else:
                start = True
                dot_string += key[0] + " -> " + "{"
                for sub in ordered_sub_dict[key]:
                    dot_string += " " + sub + " "
                dot_string += "};\n"
        return dot_string

    def convert_ordered_dict_to_seq(sub, file, seq_string):
        """ Converts the reordered subroutine dictionary to .dot file."""
        # advance to the start
        # start = False
        # for key in ordered_sub_dict.keys(): 
        #     if key != (sub, file) and start is False:
        #         continue
        #     else:
        #         start = True
        if len(ordered_sub_dict[(sub, file)]) > 0:
            for sub2 in ordered_sub_dict[(sub, file)]:
                seq_string += sub + "->" + sub2 + ":\n"
                print(sub + "->" + sub2 + ":" )
                sub_file_name = get_sub_file_name(sub2)
                if (sub2, sub_name) not in seq_list:
                    seq_list.append((sub2, sub_name))
                    seq_string = convert_ordered_dict_to_seq(sub2, sub_file_name, seq_string)
        return seq_string

    def get_unused_subroutines():
        for sub in subroutine_names:
            if sub not in ordered_sub_dict:
                unused_subroutines.add(sub)
        return 
                
    reorder_sub_dict("main", "./src/main.f90")

    # with open("ordered_dict.txt", "w") as od:
    #     for x in ordered_sub_dict.keys():
    #         print(x, ordered_sub_dict[x])
    #         od.write(str(x) + str(ordered_sub_dict[x]) + "\n")

    # Convert the ordered dictionary to .dot file
    dot_string = "digraph {\nrankdir=LR\n"
    dot_string = convert_ordered_dict_to_dot("main", "./src/main.f90", dot_string)
    dot_string += "}"
    # print(dot_string)
    with open("swatplus_call_tree.dot", "w") as wp:
         wp.write(dot_string)
    # dot = graphviz.Digraph(comment='Swatplus Call Tree')
    # dot.render("swatplus_call_tree.dot", "swatplus_call_tree2.jpg")

    seq_string = "title Swatplus Sequence Diagram\n"
    seq_string = convert_ordered_dict_to_seq("main", "./src/main.f90", seq_string)
    with open("swatplus_call_tree_seq.txt", "w") as wp:
         wp.write(seq_string)

    get_unused_subroutines()
    with open("unused_subroutines.txt", "w") as up:
        for sub in unused_subroutines:
            up.write(f"{sub[0]} {sub[1]}\n")

if __name__ == '__main__':
    main()




 