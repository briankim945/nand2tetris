// Fill screen with black if pressing key, white otherwise

    @COLOR
    M=0
    @CHECK
    0;JMP

(RESET)
    // Set pixels
    @SCREEN
    D=A
    @8192
    D=D+A
    @PIXEL
    M=D

// Checks for key press
(CHECK)
    @KBD
    D=M
    @LOOP
    D;JEQ
    D=-1

// Fills the screen with alternating black and white
(LOOP)
    // Save current color
    @ARG
    M=D

    // Compare with past color, loop back to check if same
    @COLOR
    D=D-M
    @FILL
    D;JEQ

    // If not equal, set COLOR = ARG
    @ARG
    D=M
    @COLOR
    M=D

// Fills screen
(FILL)
    // Loop through pixels of screen
    @PIXEL
    D=M-1
    M=D
    @SCREEN
    D=D-A
    @RESET
    D;JLT

    // Fill pixel with appropriate color
    @COLOR
    D=M
    @PIXEL // Stores pixel in A, need to pull that into M
    A=M
    M=D
    
    // Restart
    @CHECK
    0;JMP