import argparse
import os

from CodeWriter.CodeWriter import CodeWriter
from Parser.Parser import Parser

parser = argparse.ArgumentParser(description='Convert VM code to Hack instructions.')
parser.add_argument('source', metavar='file', type=str, help='the file to pull the assembly from')
parser.add_argument('--nsi', help='adding flag means VMTranslator does not add the call to sys.init', action="store_false")
args = parser.parse_args()
print(args)


class VMTranslator:
    def __init__(self):
        self.codeWriter = CodeWriter()
        self.parser = Parser()

    def verifyName(self, filename):
        return len(filename) > 2 and filename[-3:] == ".vm"

    def translate(self, source: str, addInit=True):
        try:
            if self.verifyName(source):
                inputs = [source]
            else:
                inputs = [source + '/' + item for item in os.listdir(source) if self.verifyName(item)]

            print("Input files:", inputs)

            self.codeWriter.constructor("Prog.asm", addInit)

            for filename in inputs:
                self.codeWriter.setFileName(filename)
                self.parser.constructor(filename)

                while self.parser.hasMoreLines():
                    c = self.parser.commandType()
                    if c != "C_RETURN":
                        arg1 = self.parser.arg1()
                        if c in ["C_PUSH", "C_POP", "C_FUNCTION", "C_CALL"]:
                            arg2 = self.parser.arg2()
                            if c == "C_PUSH" or c == "C_POP": self.codeWriter.writePushPop(c, arg1, int(arg2))
                            elif c == "C_FUNCTION": self.codeWriter.writeFunction(arg1, int(arg2))
                            elif c == "C_CALL": self.codeWriter.writeCall(arg1, int(arg2))
                        elif c == "C_ARITHMETIC": self.codeWriter.writeArithmetic(arg1)
                        elif c == "C_LABEL": self.codeWriter.writeLabel(arg1)
                        elif c == "C_GOTO": self.codeWriter.writeGoto(arg1)
                        elif c == "C_IF": self.codeWriter.writeIf(arg1)
                    else:
                        self.codeWriter.writeReturn()
                    self.parser.advance()

            self.codeWriter.close()
        except OSError as e:
            print("Error retrieving files")
            print(e)
        except Exception as e:
            print("Unknown error")
            print(e)


vmt = VMTranslator()
vmt.translate(args.source, args.nsi)
