from vm_strings import math_calls, math_dict


class VMWriter:
    def __init__(self, outputFile):
        self.comp_iter = 1
        self.outputFile = None
        self.inputFileName = None
        self.outputFile = outputFile
        self.firstLine = True
        self.tab = "    "

    def setFileName(self, fileName: str):
        self.inputFileName = fileName
        self.writeClean(f"// Compiled {fileName}.jack:")

    def writeClean(self, line):
        if self.firstLine:
            self.firstLine = False
            self.outputFile.write(line)
        else:
            self.outputFile.write('\n' + line)

    def writeArithmetic(self, command: str):
        if command in math_dict:
            self.writeClean(f"{self.tab}{math_dict[command]}")
        elif command in math_calls:
            self.writeClean(f"{self.tab}call {math_calls[command][0]} {math_calls[command][1]}")

    def writePush(self, segment: str, index: int):
        # if segment.lower() != "none":
        self.writeClean(self.tab + f"push {segment.lower()} {index}")

    def writePop(self, segment: str, index: int):
        self.writeClean(self.tab + f"pop {segment.lower()} {index}")

    def writeLabel(self, label: str):
        self.writeClean(f"label {label}")

    def writeGoto(self, label: str):
        self.writeClean(self.tab + f"goto {label}")

    def writeIf(self, label: str):
        self.writeClean(self.tab + f"if-goto {label}")

    def writeFunction(self, functionName: str, nVars: int):
        self.writeClean(f"function {self.inputFileName}.{functionName} {nVars}")

    def writeCall(self, functionName: str, nArg: int):
        self.writeClean(self.tab + f"call {functionName} {nArg}")

    def writeReturn(self):
        self.writeClean(self.tab + "return")

    def writeNot(self):
        self.writeClean(self.tab + "not")

    def close(self):
        self.outputFile.close()