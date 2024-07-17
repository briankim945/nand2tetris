// Multiples contents of R0 and R1, stores to R2

// Set R2 to 0
    @2
    M=0

// Skips to the end if R1 = 0
(COUNT)
    @1
    D=M
    @200
    D;JEQ

// Loops by adding R0 to R2, subtracting from R1 each time, until R1 = 0
(ADD)
    @0
    D=M
    @2
    M=D+M

(SUBTRACT)
    @1
    D=M
    D=D-A
    M=D
    @COUNT
    0;JMP