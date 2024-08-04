from .parse_constants import parse_map

class Parser:
    def __init__(self):
        self.inputFile = None
        self.nextLine = None
        self.lineParts = None
        self.currentCommand = None

    def constructor(self, inputFile):
        if self.inputFile is not None:
            self.inputFile.close()
        self.inputFile = open(inputFile, "r")
        self.advance()

    def hasMoreLines(self) -> bool:
        return self.nextLine != ""

    def advance(self):
        self.nextLine = self.inputFile.readline()
        while self.nextLine == '\n' or (len(self.nextLine) > 0 and self.nextLine.strip()[0] == '/'):
            self.nextLine = self.inputFile.readline()
        if self.nextLine is not None and len(self.nextLine) > 0:
            self.lineParts = self.nextLine.split()
            self.commandType()

    def commandType(self):
        self.currentCommand = parse_map[self.lineParts[0]]
        return self.currentCommand

    def arg1(self) -> str:
        if self.currentCommand == "C_ARITHMETIC":
            return self.lineParts[0]
        else:
            return self.lineParts[1]

    def arg2(self) -> int:
        return self.lineParts[2]