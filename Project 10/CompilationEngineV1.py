import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString

from JackTokenizer import JackTokenizer
from jack_constants import operators

class CompilationEngine:

    def __init__(self, fileInputStream, fileOutputStream):
        self.fileInputStream = fileInputStream
        self.fileOutputStream = fileOutputStream
        self.jktk = JackTokenizer(self.fileInputStream)
        self.firstLine = True
        self.output = ""
        self.expressions = {
            "=", ";",
            "[", "]",
        }

    def compileClass(self, prefix=""):
        # print("STARTING")
        self.writeLine(prefix + "<class>")
        innerPrefix = prefix + "  "
        while self.jktk.hasMoreTokens():
            self.jktk.advance()
            # print("token", self.jktk.tokenType(), self.jktk.symbol())
            if self.jktk.tokenType() == "SYMBOL":
                self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
            elif self.jktk.tokenType() == "KEYWORD":
                if self.jktk.keyWord() in ["static", "field"]:
                    self.compileClassVarDec(prefix=innerPrefix)
                elif self.jktk.keyWord() in ["method", "function", "constructor"]:
                    self.compileSubroutine(prefix=innerPrefix)
                else:
                    self.writeLine(innerPrefix + f"<keyword> {self.jktk.keyWord()} </keyword>")
            elif self.jktk.tokenType() == "IDENTIFIER":
                self.writeLine(innerPrefix + f"<identifier> {self.jktk.identifier()} </identifier>")
        self.writeLine(prefix + "</class>")

    def compileClassVarDec(self, prefix=""):
        self.writeLine(prefix + "<classVarDec>")
        innerPrefix = prefix + "  "
        while not (self.jktk.tokenType() == "SYMBOL" and self.jktk.symbol(internal=False) == ';'):
            if self.jktk.tokenType() == "SYMBOL":
                self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
            elif self.jktk.tokenType() == "KEYWORD":
                self.writeLine(innerPrefix + f"<keyword> {self.jktk.keyWord()} </keyword>")
            self.jktk.advance()
        self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
        self.writeLine(prefix + "</classVarDec>")

    def compileSubroutine(self, prefix=""):
        self.writeLine(prefix + "<subroutineDec>")
        innerPrefix = prefix + "  "
        while not (self.jktk.tokenType() == "SYMBOL" and self.jktk.symbol(internal=False) == "{"):
            if self.jktk.tokenType() == "SYMBOL":
                self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
                if self.jktk.symbol(internal=False) == "(":
                    self.jktk.advance()
                    self.compileParamaterList(prefix=innerPrefix)
                self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
            elif self.jktk.tokenType() == "KEYWORD":
                self.writeLine(innerPrefix + f"<keyword> {self.jktk.keyWord()} </keyword>")
            elif self.jktk.tokenType() == "IDENTIFIER":
                self.writeLine(innerPrefix + f"<identifier> {self.jktk.identifier()} </identifier>")
            self.jktk.advance()
        self.compileSubroutineBody(prefix=innerPrefix)
        self.writeLine(prefix + "</subroutineDec>")

    def compileParamaterList(self, prefix=""):
        self.writeLine(prefix + "<parameterList>")
        innerPrefix = prefix + "  "
        while not (self.jktk.tokenType() == "SYMBOL" and self.jktk.symbol(internal=False) == ')'):
            if self.jktk.tokenType() == "SYMBOL":
                self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
            elif self.jktk.tokenType() == "KEYWORD":
                self.writeLine(innerPrefix + f"<keyword> {self.jktk.keyWord()} </keyword>")
            elif self.jktk.tokenType() == "IDENTIFIER":
                self.writeLine(innerPrefix + f"<identifier> {self.jktk.identifier()} </identifier>")
            self.jktk.advance()
        self.writeLine(prefix + "</parameterList>")

    def compileSubroutineBody(self, prefix=""):
        self.writeLine(prefix + f"<subroutineBody>")
        innerPrefix = prefix + "  "
        self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
        self.jktk.advance()
        while self.jktk.tokenType() == "KEYWORD" and self.jktk.keyWord() == "var":
            self.compileVarDec(prefix=innerPrefix)
        self.compileStatements(prefix=innerPrefix)
        self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
        self.writeLine(prefix + f"</subroutineBody>")

    def compileVarDec(self, prefix=""):
        self.writeLine(prefix + "<varDec>")
        innerPrefix = prefix + "  "
        while not (self.jktk.tokenType() == "SYMBOL" and self.jktk.symbol(internal=False) == ';'):
            if self.jktk.tokenType() == "SYMBOL":
                self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
            elif self.jktk.tokenType() == "KEYWORD":
                self.writeLine(innerPrefix + f"<keyword> {self.jktk.keyWord()} </keyword>")
            elif self.jktk.tokenType() == "IDENTIFIER":
                self.writeLine(innerPrefix + f"<identifier> {self.jktk.identifier()} </identifier>")
            self.jktk.advance()
        self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
        self.jktk.advance()
        self.writeLine(prefix + "</varDec>")

    def compileStatements(self, prefix=""):
        self.writeLine(prefix + "<statements>")
        innerPrefix = prefix + "  "
        while not (self.jktk.tokenType() == "SYMBOL" and self.jktk.symbol(internal=False) == '}'):
            if self.jktk.tokenType() == "KEYWORD":
                if self.jktk.keyWord() == "let":
                    self.compileLet(prefix=innerPrefix)
                elif self.jktk.keyWord() == "if":
                    self.compileIf(prefix=innerPrefix)
                elif self.jktk.keyWord() == "while":
                    self.compileWhile(prefix=innerPrefix)
                elif self.jktk.keyWord() == "do":
                    self.compileDo(prefix=innerPrefix)
                elif self.jktk.keyWord() == "return":
                    self.compileReturn(prefix=innerPrefix)
        self.writeLine(prefix + "</statements>")

    def compileLet(self, prefix=""):
        self.writeLine(prefix + "<letStatement>")
        innerPrefix = prefix + "  "
        trigger = True
        while not (self.jktk.tokenType() == "SYMBOL" and self.jktk.symbol(internal=False) == ';'):
            trigger = True
            if self.jktk.tokenType() == "SYMBOL":
                self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
                if self.jktk.symbol(internal=False) == "=":
                    self.jktk.advance()
                    self.compileExpression(prefix=innerPrefix, terminator=';')
                    # ;
                    # self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
                    trigger = False
                elif self.jktk.symbol(internal=False) == "[":
                    self.jktk.advance()
                    self.compileExpression(prefix=innerPrefix, terminator=']')
                    # ]
                    self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
                elif self.jktk.symbol(internal=False) == "(":
                    # (
                    self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
                    self.jktk.advance()
                    # Expression list (arguments)
                    self.compileExpressionList(prefix=innerPrefix, terminator=')')
                    #)
                    self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
            elif self.jktk.tokenType() == "KEYWORD":
                self.writeLine(innerPrefix + f"<keyword> {self.jktk.keyWord()} </keyword>")
            elif self.jktk.tokenType() == "IDENTIFIER":
                self.writeLine(innerPrefix + f"<identifier> {self.jktk.identifier()} </identifier>")

            if trigger:
                self.jktk.advance()
        # ;
        self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
        self.jktk.advance()
        self.writeLine(prefix + "</letStatement>")
        # print(self.jktk.keyWord())

    def compileIf(self, prefix=""):
        self.writeLine(prefix + "<ifStatement>")
        innerPrefix = prefix + "  "
        # if
        self.writeLine(innerPrefix + f"<keyword> {self.jktk.keyWord()} </keyword>")
        self.jktk.advance()
        # (
        self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
        self.jktk.advance()
        self.compileExpression(prefix=innerPrefix, terminator=')')
        # )
        self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
        self.jktk.advance()
        # {
        self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
        self.jktk.advance()
        self.compileStatements(prefix=innerPrefix)
        # }
        self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
        self.jktk.advance()
        self.writeLine(prefix + "</ifStatement>")

    def compileWhile(self, prefix=""):
        self.writeLine(prefix + "<whileStatement>")
        innerPrefix = prefix + "  "
        # while
        self.writeLine(innerPrefix + f"<keyword> {self.jktk.keyWord()} </keyword>")
        self.jktk.advance()
        # (
        self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
        self.jktk.advance()
        self.compileExpression(prefix=innerPrefix, terminator=')')
        # )
        self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
        self.jktk.advance()
        # {
        self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
        self.jktk.advance()
        self.compileStatements(prefix=innerPrefix)
        # }
        self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
        self.jktk.advance()
        self.writeLine(prefix + "</whileStatement>")

    def compileDo(self, prefix=""):
        self.writeLine(prefix + "<doStatement>")
        innerPrefix = prefix + "  "
        while not (self.jktk.tokenType() == "SYMBOL" and self.jktk.symbol(internal=False) == ';'):
            if self.jktk.tokenType() == "SYMBOL":
                self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
                if self.jktk.symbol(internal=False) == '(':
                    self.jktk.advance()
                    # Expression list (arguments)
                    self.compileExpressionList(prefix=innerPrefix, terminator=')')
                    # )
                    self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
            elif self.jktk.tokenType() == "KEYWORD":
                self.writeLine(innerPrefix + f"<keyword> {self.jktk.keyWord()} </keyword>")
            elif self.jktk.tokenType() == "IDENTIFIER":
                self.writeLine(innerPrefix + f"<identifier> {self.jktk.identifier()} </identifier>")
            self.jktk.advance()
        # ;
        self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
        self.jktk.advance()
        self.writeLine(prefix + "</doStatement>")

    def compileReturn(self, prefix=""):
        self.writeLine(prefix + "<returnStatement>")
        innerPrefix = prefix + "  "
        while not (self.jktk.tokenType() == "SYMBOL" and self.jktk.symbol(internal=False) == ';'):
            if self.jktk.tokenType() == "SYMBOL":
                self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
            elif self.jktk.tokenType() == "KEYWORD":
                self.writeLine(innerPrefix + f"<keyword> {self.jktk.keyWord()} </keyword>")
            elif self.jktk.tokenType() == "IDENTIFIER":
                self.writeLine(innerPrefix + f"<identifier> {self.jktk.identifier()} </identifier>")
            self.jktk.advance()
        # ;
        self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
        self.jktk.advance()
        self.writeLine(prefix + "</returnStatement>")

    def compileExpression(self, prefix="", terminator=None):
        self.writeLine(prefix + "<expression>")
        innerPrefix = prefix + "  "
        potentialFunction = False
        if terminator is not None:
            while not (self.jktk.tokenType() == "SYMBOL" and self.jktk.symbol(internal=False) == terminator):
                if self.jktk.tokenType() == "SYMBOL":
                    self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
                    if potentialFunction and self.jktk.symbol(internal=False) == "(":
                        # (
                        self.jktk.advance()
                        # Expression list (arguments)
                        self.compileExpressionList(prefix=innerPrefix, terminator=')')
                        #)
                        self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
                else:
                    if self.jktk.tokenType() == "IDENTIFIER":
                        potentialFunction = True
                    else:
                        potentialFunction = False
                    self.compileTerm(prefix=innerPrefix, terminator=terminator)
                    continue
                self.jktk.advance()
        # print(self.jktk.symbol())
        self.writeLine(prefix + "</expression>")

    def compileTerm(self, prefix="", terminator=None):
        # print("TERM:", self.jktk.tokenType(), self.jktk.symbol())
        self.writeLine(prefix + "<term>")
        innerPrefix = prefix + "  "
        potentialFunction = False
        if terminator is not None:
            while not (self.jktk.tokenType() == "SYMBOL" and (self.jktk.symbol(internal=False) == terminator or self.jktk.symbol(internal=False) in operators)): 
                if self.jktk.tokenType() == "IDENTIFIER":
                    self.writeLine(innerPrefix + f"<identifier> {self.jktk.identifier()} </identifier>")
                    potentialFunction = True
                else:
                    if self.jktk.tokenType() == "SYMBOL":
                        self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
                        if potentialFunction and self.jktk.symbol(internal=False) == "(":
                            # (
                            self.jktk.advance()
                            # Expression list (arguments)
                            self.compileExpressionList(prefix=innerPrefix, terminator=')')
                            #)
                            self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
                        elif self.jktk.symbol(internal=False) == "[":
                            self.jktk.advance()
                            self.compileExpression(prefix=innerPrefix, terminator=']')
                            # ]
                            self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
                    elif self.jktk.tokenType() == "INT_CONST":
                        self.writeLine(innerPrefix + f"<integerConstant> {self.jktk.intVal()} </integerConstant>")
                    elif self.jktk.tokenType() == "STRING_CONST":
                        self.writeLine(innerPrefix + f"<stringConstant> {self.jktk.stringVal()} </stringConstant>")
                    potentialFunction = False
                self.jktk.advance()
        self.writeLine(prefix + "</term>")

    def compileExpressionList(self, prefix="", terminator=None) -> int:
        count = 0
        self.writeLine(prefix + "<expressionList>")
        innerPrefix = prefix + "  "
        if terminator is not None:
            while not (self.jktk.tokenType() == "SYMBOL" and self.jktk.symbol(internal=False) == terminator):
                # print(self.jktk.symbol())
                if self.jktk.tokenType() == "SYMBOL":
                    self.writeLine(innerPrefix + f"<symbol> {self.jktk.symbol()} </symbol>")
                    self.jktk.advance()
                else:
                    self.compileExpression(prefix=innerPrefix, terminator=')')
                    count += 1
        self.writeLine(prefix + "</expressionList>")
        return count

    def writeLine(self, line):
        print(line)
        if self.firstLine:
            # self.fileOutputStream.write(line)
            self.output += line
            self.firstLine = False
        else:
            # self.fileOutputStream.write('\n' + line)
            self.output += '\n' + line

    def save(self):
        print(len(self.output) - self.output.count(' '))
        print(self.output[2766])
        print(self.output.replace(" ", "")[2766])
        print(self.output.replace(" ", "").replace('\n', "")[2766])
        print(self.output.replace(" ", "")[2750: 2780])
        # self.output.replace("<", escape("<"))
        # self.output.replace("&", escape("&"))
        # self.output.replace(">", escape(">"))
        # self.output = "<class> </class>"
        # self.output = self.output.replace(";<>&")

        # parser = ET.XMLParser(encoding="utf-8")
        # tree = ET.ElementTree(ET.fromstring(self.output, parser=parser))
        
        parser = ET.XMLParser(encoding="utf-8")
        tree = ET.ElementTree(ET.fromstring(self.output, parser=parser))

        tree.write(self.fileOutputStream)
        
        # dom = xml.dom.minidom.parse(xml_fname) # or xml.dom.minidom.parseString(xml_string)

        # parsed = parseString(self.output)
        # pretty_xml_as_string = '\n'.join([line for line in parsed.toprettyxml(indent=" "*2).split('\n') if line.strip()])

        # print(pretty_xml_as_string)

        # parser = ET.XMLParser(encoding="utf-8")
        # tree = ET.ElementTree(ET.fromstring(pretty_xml_as_string, parser=parser))

        # tree.write(self.fileOutputStream)

        # with open(self.fileOutputStream, 'w') as f:
        #     f.write(self.output)