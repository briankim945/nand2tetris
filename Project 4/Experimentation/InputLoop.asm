// Runs an infinite loop that saves key press value to R0

// R0 contains key value
@0
M=0

// Check if key is pressed
@KBD
D=M
@10
D;JEQ
@0
M=D
@12
A;JMP
@0
M=0

// Loop to fill screen with R0
@0
D=M
@1
D=M
@2
D;JMP