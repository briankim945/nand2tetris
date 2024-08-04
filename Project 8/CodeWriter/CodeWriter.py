from .code_strings import (
    bool_meta,
    bool_format,
    bootstrap_start,
    call_format,
    comp_meta,
    comp_format, 
    goto_format,
    file_end,
    if_format,
    label_format,
    math_ops,
    not_format,
    pointer_pop_start,
    pointer_push_end,
    pop_end,
    push_begin,
    push_num,
    return_format,
)


class CodeWriter:
    def __init__(self):
        self.comp_iter = 1
        self.outputFile = None
        self.inputFileName = None

    def constructor(self, outputFile, callSysIinit=True):
        self.outputFile = open(outputFile, "w")
        if callSysIinit:
            self.writeClean(bootstrap_start)

    def setFileName(self, fileName: str):
        self.inputFileName = fileName.split('/')[-1][:-3]

    def writeClean(self, lines):
        lines = lines.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 0 and line[0] in ["@", "A", "M", "D", "(", "0"]:
                self.outputFile.write(line + '\n')

    def writeArithmetic(self, command: str):
        newLine = None
        if command in math_ops:
            newLine = math_ops[command]
        elif command in comp_meta:
            self.comp_iter += 1
            newLine = comp_format.format(
                comp_meta[command][0],
                comp_meta[command][1],
                comp_meta[command][2],
                self.comp_iter,
            )
        elif command in bool_meta:
            self.comp_iter += 1
            if len(bool_meta[command]) == 1:
                newLine = bool_format.format(bool_meta[command][0])
            else:
                newLine = not_format
        self.writeClean(newLine)

    def writePushPop(self, command, segment: str, index: int):
        newLine = None
        if command == "C_PUSH":
            newLine = push_begin(segment, index, self.inputFileName) + '\n' + pointer_push_end
        elif command == "C_POP":
            newLine = pointer_pop_start + '\n' + pop_end(segment, index, self.inputFileName)
        self.writeClean(newLine)

    def writeLabel(self, label: str):
        self.writeClean(label_format.format(label))

    def writeGoto(self, label: str):
        self.writeClean(goto_format.format(label))

    def writeIf(self, label: str):
        self.writeClean(if_format.format(label))

    def writeFunction(self, functionName: str, nVars: int):
        newLine = f"({functionName})\n"
        for _ in range(nVars):
            newLine += push_num.format(0) + '\n'
        self.writeClean(newLine)

    def writeCall(self, functionName: str, nArg: int):
        newLine = call_format.format(f"{self.inputFileName}.return.{self.comp_iter}", nArg, functionName)
        self.comp_iter += 1
        self.writeClean(newLine)

    def writeReturn(self):
        newLine = return_format.format(f"{self.inputFileName}.return.{self.comp_iter}")
        self.comp_iter += 1
        self.writeClean(newLine)

    def close(self):
        self.outputFile.close()