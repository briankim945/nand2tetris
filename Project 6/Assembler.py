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


output_string = ""

try:
    with open(args.file) as f:
        for line in f:
            line = line.strip()

            # Getting rid of empty lines and comments
            if len(line) != 0 and line[:2] != "//":
                oLine = ""

                # Handling A-instructions, need to include symbolic references
                if line[0] == '@':
                    oLine += "0"
                    if line[1:].isnumeric():
                        tmp = "{0:b}".format(int(line[1:]))
                        tmp = tmp.zfill(15)
                        oLine += tmp
                    else:
                        oLine += '0' * 15

                # Handling C-Instruction
                else:
                    oLine += "111"
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

                if len(output_string) > 0:
                    output_string += '\n'
                output_string += oLine
    with open('Prog.hack', 'w') as f:
        f.write(output_string)
except FileNotFoundError:
    print("File cannot be found")