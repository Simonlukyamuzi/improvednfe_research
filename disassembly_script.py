import pydasm
from os import listdir 
from sys import argv

path_to_benign_folder = "benign" if len(argv) < 2 else argv[1]
dll_disassemble_suf = ".dlldisassemble"
files = listdir(path_to_benign_folder)

def disassemble_dll(file_path):
    f = open(file_path, "rb")
    buff = f.read()
    f.close()
    instructions = []

    offset = 0
    while offset < len(buff):
        i = pydasm.get_instruction(buff[offset:], pydasm.MODE_32)
        if not i:
            break
        instructions.append(pydasm.get_instruction_string(i, pydasm.FORMAT_INTEL, 0))
        offset += i.length
    return instructions

def disassemble_to_file(file_path, new_file_name):
    dis = disassemble_dll(file_path)
    with open(new_file_name, "w") as f:
        for instruction in dis:
            f.write(instruction + "\n")
    return dis


for f in files:
    if f.endswith(".bin"):
        disassemble_to_file(path_to_benign_folder + "/" + f, path_to_benign_folder + "/" + f[:-10] + dll_disassemble_suf)
