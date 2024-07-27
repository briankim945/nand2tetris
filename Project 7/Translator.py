import argparse

parser = argparse.ArgumentParser(description='Convert VM code to Hack instructions.')
parser.add_argument('file', metavar='file', type=str,
                    help='the file to pull the assembly from')
args = parser.parse_args()


filename = args.file.split('/')[-1].split('.')[0]

relatives = {
    "local": "LCL",
    "argument": "ARG",
    "this": "THIS",
    "that": "THAT",
    '0': "THIS",
    '1': "THAT",
}

common_ops = {
    "SP++": """// SP++
    @SP
    M=M+1""",

    "SP--": """// SP--
    @SP
    M=M-1""",
}

adv_ops = {
    # First is in D, second in M
    "pop_two": f"""{common_ops["SP--"]}
    // D = RAM[SP]
    A=M
    D=M
    {common_ops["SP--"]}
    // RAM[SP] = RAM[SP] + D
    A=M""",

    # Popped into D
    "pop_one": f"""{common_ops["SP--"]}
    // D = RAM[SP]
    A=M
    D=M""",
}

math_ops = {
    "add": f"""{adv_ops["pop_two"]}
    M=D+M
    {common_ops["SP++"]}""",

    "sub": f"""{adv_ops["pop_two"]}
    M=M-D
    {common_ops["SP++"]}""",

    "neg": f"""{adv_ops["pop_one"]}
    // RAM[SP] = 0 - D
    @0
    D=A-D
    @SP
    A=M
    M=D
    {common_ops["SP++"]}""",
}

set_true = """@0
    D=A
    @1
    D=D-A"""

comp_meta = {
    "eq": ["JEQ", "JNE", 'M-D'],
    "gt": ["JGT", "JLE", 'M-D'],
    "lt": ["JLT", "JGE", 'M-D'],
}

comp_format = adv_ops["pop_two"] + '\n' + """D={2}
    @JumpT.{3}
    D;{0}
    @JumpF.{3}
    D;{1}
    (JumpT.{3})""" + '\n' + set_true + '\n' + """@JumpEnd.{3}
    0;JMP
    (JumpF.{3})
    @0
    D=A
    @JumpEnd.{3}
    0;JMP
    (JumpEnd.{3})
    @SP
    A=M
    M=D""" + '\n' + common_ops["SP++"]

bool_meta = {
    "and": ['&'],
    "or": ['|'],
    "not": [],
}

bool_format = adv_ops["pop_two"] + '\n' + "M=D{0}M" + '\n' + common_ops["SP++"]

not_format = adv_ops["pop_one"] + '\n' + "M=!M" + '\n' + common_ops["SP++"]

pointer_push_end = f"""// RAM[SP] = D
@SP
A=M
M=D
{common_ops["SP++"]}"""

pointer_pop_start = f"""{common_ops["SP--"]}
// RAM[SP]
@SP
A=M"""

file_end = """(END)
@END
0;JMP"""

comp_iter = 0


def check_line(line):
    return len(line) > 1 and line[:2] != "//"

def identify_command(line):
    items = line.split()
    if items[0] == "push":
        return push_begin(items[1], items[2]) + '\n' + pointer_push_end
    elif items[0] == "pop":
        return pointer_pop_start + '\n' + pop_end(items[1], items[2])
    elif items[0] in math_ops:
        return translate_math(items[0])
    elif items[0] in comp_meta:
        return translate_compare(items[0])
    elif items[0] in bool_meta:
        return translate_bool(items[0])
    else:
        print("FAIL", line)
        
def push_begin(segment, i):
    if segment == "constant":
        begin = f"""// D = {i}
        @{i}
        D=A"""
    elif segment in relatives:
        addr = relatives[segment]
        begin = f"""// D = {i}
        @{i}
        D=A
        // D = {addr}
        @{addr}
        D=D+M
        A=D
        D=M"""
    elif segment == "static":
        begin = f"""// {filename}.{i}
        @{filename}.{i}
        D=M"""
    elif segment == "temp":
        begin = f"""// D = {i}
        @{i}
        D=A
        // D = 5 + {i}
        @5
        D=D+A
        A=D
        D=M"""
    elif segment == "pointer":
        begin = f"""// D = {relatives[i]}
        @{relatives[i]}
        D=M"""
    else:
        begin = ""
    return begin

def pop_end(segment, i):
    begin = """// D = M (RAM[SP]) (pop value)
    D=M"""

    if segment in relatives:
        addr = relatives[segment]
        middle = f"""// D = D + addr
        @{addr}
        D=D+M
        // D = D + i
        @{i}"""
    elif segment == "static":
        middle = f"""// D = D + {filename}.{i}
        @{filename}.{i}"""
    elif segment == "temp":
        middle = f"""// D = D + {i}
        @{i}
        D=D+A
        // D = 5 + {i}
        @5"""
    elif segment == "pointer":
        middle = f"""// D = D + {relatives[i]}
        @{relatives[i]}"""
    else:
        middle = ""

    end = """D=D+A
        // Push RAM[SP] into RAM[addr]
        @SP
        A=M
        // Getting pointer value
        A=M
        A=D-A
        M=D-A"""
    return begin + '\n' + middle + '\n' + end

def translate_math(command):
    if command == "add":
        return math_ops["add"]
    elif command == "sub":
        return math_ops["sub"]
    elif command == "neg":
        return math_ops["neg"]

def translate_compare(command):
    global comp_iter
    comp_iter += 1
    return comp_format.format(
        comp_meta[command][0],
        comp_meta[command][1],
        comp_meta[command][2],
        comp_iter,
    )

def translate_bool(command):
    global comp_iter
    comp_iter += 1
    if len(bool_meta[command]) == 1:
        return bool_format.format(bool_meta[command][0])
    else:
        return not_format

def add_ins(parent, new_line):
    if parent is None:
        parent = new_line
    else:
        parent += '\n' + new_line
    return parent

def translate(f):
    hack_instructions = None
    for line in f:
        line = line.strip()
        if check_line(line):
            new_ins = identify_command(line)
            hack_instructions = add_ins(hack_instructions, new_ins)
    hack_instructions = add_ins(hack_instructions, file_end)
    return hack_instructions

def cleanup(ins):
    clean_ins = None
    for line in ins.split('\n'):
        line = line.strip()
        if line[0] in ["@", "A", "M", "D", "(", "0"]:
            if clean_ins is None:
                clean_ins = line
            else:
                clean_ins += '\n' + line
    return clean_ins

try:
    with open(args.file) as f:
        hack_ins = translate(f)
    with open('Prog.asm', 'w') as f:
        f.write(cleanup(hack_ins))
except FileNotFoundError:
    print("File cannot be found")