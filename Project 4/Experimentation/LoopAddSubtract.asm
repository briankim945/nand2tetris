// Adds the values at R0 and R1, places at R2, subtracts from R1 and continues until R1 = 0
@0
D=M
@1
D=D+M
@2
M=D
@1
D=M
@1
M=D-A
@200
D;JEQ
@0
D;JMP