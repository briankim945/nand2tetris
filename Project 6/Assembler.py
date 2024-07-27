import argparse

parser = argparse.ArgumentParser(description='Convert hack language to machine code.')
parser.add_argument('file', metavar='file', type=str,
                    help='the file to pull the assembly from')

args = parser.parse_args()
print(args.file)

comp0_map = {
    "0":    "101010",
    "1":    "111111",
    "-1":   "111010",
    "D":    "001100",
    "A":    "110000",
    "!D":   "001101",
    "!A":   "110001",
    "-D":   "001111",
    "-A":   "110011",
    "D+1":  "011111",
    "A+1":  "110111",
    "D-1":  "001110",
    "A-1":  "110010",
    "D+A":  "000010",
    "D-A":  "010011",
    "A-D":  "000111",
    "D&A":  "000000",
    "D|A":  "010101",
}
comp1_map = {
    "M":    "110000",
    "!M":   "110001",
    "-M":   "110011",
    "M+1":  "110111",
    "M-1":  "110010",
    "D+M":  "000010",
    "D-M":  "010011",
    "M-D":  "000111",
    "D&M":  "000000",
    "D|M":  "010101",
}

dest_map = {
    "null": "000",
    "M":    "001",
    "D":    "010",
    "DM":   "011",
    "A":    "100",
    "AM":   "101",
    "AD":   "110",
    "ADM":  "111",
}

jump_map = {
    "null": "000",
    "JGT":  "001",
    "JEQ":  "010",
    "JGE":  "011",
    "JLT":  "100",
    "JNE":  "101",
    "JLE":  "110",
    "JMP":  "111",
}

symbol_map = {
    "SP":       0,
    "LCL":      1,
    "ARG":      2,
    "THIS":     3,
    "THAT":     4,
    "SCREEN":   16384,
    "KBD":      24576,
}

for i in range(16):
    symbol_map[f"R{i}"] = i

RAM_open = 16


def check_valid_line(line):
    return len(line) != 0 and line[:2] != "//"

def check_pseudo(line):
    return line[0] == '(' and line[-1] == ')'

def first_pass(file):
    global symbol_map
    # First pass to construct Symbols
    with open(file) as f:
        line_count = 0
        for line in f:
            line = line.strip()
            # Getting rid of empty lines and comments
            if check_valid_line(line):
                if check_pseudo(line):
                    symbol_map[line[1:-1]] = line_count
                else:
                    line_count += 1

def handle_A_string(line):
    global RAM_open
    oLine = "0"

    # Simply numbers
    if line[1:].isnumeric():
        tmp = int(line[1:])
    # Symbolic
    else:
        tmp = line[1:]
        # Handle new symbols
        if tmp not in symbol_map:
            symbol_map[tmp] = RAM_open
            RAM_open += 1
        tmp = symbol_map[tmp]

    tmp = "{0:b}".format(tmp)
    tmp = tmp.zfill(15)
    oLine += tmp

    return oLine

def handle_C_string(line):
    oLine = "111"
    comp = "null"
    dest = "null"
    jump = "null"

    # Split by equals sign for comp and dest
    if "=" in line:
        dest = line.split("=")[0].strip()
        comp = line.split("=")[1].strip()
    else:
        comp = line

    # Split by ; for jump if present
    if ";" in comp:
        jump = comp.split(";")[1].strip()
        comp = comp.split(";")[0].strip()
    
    if "M" in comp:
        oLine += "1" + comp1_map[comp]
    else:
        oLine += "0" + comp0_map[comp]

    # Possible bug in PongL.asm
    if dest == "MD":
        dest = "DM"

    oLine += dest_map[dest]
    oLine += jump_map[jump]

    return oLine

def second_pass(file):
    # Second pass to construct output
    output_string = ""

    with open(args.file) as f:
        for line in f:
            line = line.strip()

            # Getting rid of empty lines and comments
            if check_valid_line(line) and not check_pseudo(line):

                # Handling A-instructions, need to include symbolic references
                if line[0] == '@':
                    oLine = handle_A_string(line)

                # Handling C-Instruction
                else:
                    handle_A_string(line)

                if len(output_string) > 0:
                    output_string += '\n'
                output_string += oLine


try:
    first_pass(args.file)
    output_string = second_pass(args.file)
    with open('Prog.hack', 'w') as f:
        f.write(output_string)
except FileNotFoundError:
    print("File cannot be found")