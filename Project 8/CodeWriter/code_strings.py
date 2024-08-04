relatives = {
    "local": "LCL",
    "argument": "ARG",
    "this": "THIS",
    "that": "THAT",
    0: "THIS",
    1: "THAT",
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

label_format = "({0})"

goto_format = """@{0}
0;JMP"""

if_format = f"""{adv_ops["pop_one"]}\n""" + """@{0}
D;JNE"""

file_end = """(END)
@END
0;JMP"""


def push_begin(segment, i, filename="null"):
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

def pop_end(segment, i, filename="null"):
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


push_num = push_begin("constant", "{0}") + '\n' + pointer_push_end

call_format = f"""// push return address label
@retAddr.{{0}}
D=A
{pointer_push_end}
// push LCL
@LCL
D=M
{pointer_push_end}
// push ARG
@ARG
D=M
{pointer_push_end}
// push THIS
@THIS
D=M
{pointer_push_end}
//push THAT
@THAT
D=M
{pointer_push_end}
// ARG = SP - 5 - nArgs
@5
D=A
@{{1}}
D=D+A
@SP
D=M-D
@ARG
M=D
// LCL = SP
@SP
D=M
@LCL
M=D
// goto function name
@{{2}}
0;JMP
// return address label
(retAddr.{{0}})"""

return_format = f"""// endFrame = LCL
@LCL
D=M
@endFrame.{{0}}
M=D
// retAddr = *(endFrame - 5)
@endFrame.{{0}}
D=M
@5
D=D-A
A=D
D=M
@retAddr.{{0}}
M=D
// *ARG = pop()
{adv_ops["pop_one"]}
@ARG
A=M
M=D
// SP = ARG + 1
@1
D=A
@ARG
D=D+M
@SP
M=D
// THAT = *(endFrame - 1)
@endFrame.{{0}}
D=M
@1
D=D-A
A=D
D=M
@THAT
M=D
// THIS = *(endFrame - 2)
@endFrame.{{0}}
D=M
@2
D=D-A
A=D
D=M
@THIS
M=D
// ARG = *(endFrame - 3)
@endFrame.{{0}}
D=M
@3
D=D-A
A=D
D=M
@ARG
M=D
// LCL = *(endFrame - 4)
@endFrame.{{0}}
D=M
@4
D=D-A
A=D
D=M
@LCL
M=D
// goto retAddr
@retAddr.{{0}}
A=M
0;JMP"""

bootstrap_start = f"""// SP = 256
@256
D=A
@SP
M=D
// call Sys.init
{call_format.format(f"Sys.return.{0}", 0, "Sys.init")}"""