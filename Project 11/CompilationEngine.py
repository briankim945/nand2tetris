import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString

from JackTokenizer import JackTokenizer
from SymbolTable import SymbolTable
from VMWriter import VMWriter
from jack_constants import operators, unary_operators

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
        self.classSymbolTable = SymbolTable()
        self.functionSymbolTable = None
        self.vmWriter = None
        self.className = None
        self.fNum = 0
        self.lNum = 0

    def compileClass(self):
        self.jktk.advance()
        self.jktk.advance()
        self.vmWriter = VMWriter(self.fileOutputStream)
        self.className = self.jktk.identifier()
        self.vmWriter.setFileName(self.className)
        self.jktk.advance()
        assert self.jktk.symbol() == "{", "Value is {0}".format(self.jktk.symbol())
        self.classSymbolTable.define("this", "pointer", "pointer")
        while self.jktk.hasMoreTokens():
            if self.jktk.tokenType() == "KEYWORD":
                if self.jktk.keyWord() in ["static", "field"]:
                    self.compileClassVarDec()
                elif self.jktk.keyWord() in ["method", "function", "constructor"]:
                    self.functionSymbolTable = SymbolTable()
                    self.compileSubroutine()
            else:
                self.jktk.advance()

    def compileClassVarDec(self):
        n = None
        k = None
        t = None
        while not (self.jktk.tokenType() == "SYMBOL" and self.jktk.symbol(internal=False) == ';'):
            if self.jktk.keyWord() in ["STATIC", "FIELD", "ARG", "VAR", "static", "field", "argument"]:
                k = self.jktk.keyWord()
                if k == "field":
                    k = "this"
            elif self.jktk.tokenType() == "IDENTIFIER" and t is not None:
                n = self.jktk.identifier()
            elif self.jktk.tokenType() == "SYMBOL" and self.jktk.symbol() == ",":
                n = None
            else:
                t = self.jktk.keyWord()

            if k is not None and n is not None and t is not None and self.classSymbolTable.indexOf(n) == -1:
                self.classSymbolTable.define(n, k, t)
                if k == "this":
                    self.fNum += 1

            self.jktk.advance()
        if k is not None and n is not None and t is not None and self.classSymbolTable.indexOf(n) == -1:
            self.classSymbolTable.define(n, k, t)
            if k == "this":
                self.fNum += 1

    def compileSubroutine(self):
        t = self.jktk.keyWord()
        assert t in ["method", "function", "constructor"], t
        if t == "method":
            self.functionSymbolTable.define("this", "argument", self.className)
        self.jktk.advance()
        self.jktk.advance()
        n = self.jktk.identifier()
        self.jktk.advance()
        assert self.jktk.symbol() == "("
        self.jktk.advance()
        nVars = self.compileParameterList()
        self.jktk.advance()
        assert self.jktk.symbol() == "{"
        self.jktk.advance()
        while self.jktk.tokenType() == "KEYWORD" and self.jktk.keyWord() == "var":
            self.compileVarDec()
            self.jktk.advance()
        if t == "constructor":
            self.vmWriter.writeFunction(n, 0)
            self.vmWriter.writePush("constant", self.fNum)
            self.vmWriter.writeCall("Memory.alloc", 1)
            self.vmWriter.writePop("pointer", 0)
        elif t == "method":
            self.vmWriter.writeFunction(n, self.functionSymbolTable.varCount("local"))
            self.vmWriter.writePush("argument", 0)
            self.vmWriter.writePop("pointer", 0)
        else:
            self.vmWriter.writeFunction(n, self.functionSymbolTable.varCount("local"))
        self.compileSubroutineBody()
        self.jktk.advance()

    def compileParameterList(self) -> int:
        c = 0
        while not (self.jktk.tokenType() == "SYMBOL" and self.jktk.symbol(internal=False) == ')'):
            t = self.jktk.keyWord()
            self.jktk.advance()
            n = self.jktk.identifier()
            self.functionSymbolTable.define(n, "argument", t)
            c += 1
            self.jktk.advance()
            if not (self.jktk.tokenType() == "SYMBOL" and self.jktk.symbol() == ")"):
                self.jktk.advance()
        return c

    def compileSubroutineBody(self):
        self.compileStatements()
        assert self.jktk.symbol() == "}"

    def compileVarDec(self):
        n = None
        k = "local"
        t = None
        while not (self.jktk.tokenType() == "SYMBOL" and self.jktk.symbol(internal=False) == ';'):
            if self.jktk.tokenType() == "IDENTIFIER":
                if t is None:
                    t = self.jktk.identifier()
                else:
                    n = self.jktk.identifier()
            elif self.jktk.tokenType() == "KEYWORD" and self.jktk.keyWord() != "var":
                t = self.jktk.identifier()
            elif self.jktk.tokenType() == "SYMBOL" and self.jktk.symbol(internal=False) == ",":
                n = None

            if n is not None and k is not None and t is not None and self.functionSymbolTable.indexOf(n) == -1:
                self.functionSymbolTable.define(n, k, t)

            self.jktk.advance()
        if n is not None and k is not None and t is not None and self.functionSymbolTable.indexOf(n) == -1:
            self.functionSymbolTable.define(n, k, t)

    def compileStatements(self, terminator=['}']):
        while not (self.jktk.tokenType() == "SYMBOL" and self.jktk.symbol(internal=False) in terminator):
            if self.jktk.tokenType() == "KEYWORD":
                if self.jktk.keyWord() == "let":
                    self.compileLet()
                elif self.jktk.keyWord() == "if":
                    self.compileIf()
                elif self.jktk.keyWord() == "while":
                    self.compileWhile()
                elif self.jktk.keyWord() == "do":
                    self.compileDo()
                elif self.jktk.keyWord() == "return":
                    self.compileReturn()
            if not (self.jktk.tokenType() == "KEYWORD" and self.jktk.keyWord() in ["let", "if", "while", "do", "return"]) and\
                        not (self.jktk.tokenType() == "SYMBOL" and self.jktk.symbol(internal=False) in terminator):
                self.jktk.advance()

    def compileLet(self):
        arrayHandle = False
        assert self.jktk.keyWord() == "let"
        self.jktk.advance()
        varName = self.jktk.identifier()
        if (self.classSymbolTable.indexOf(varName) != -1 and self.classSymbolTable.typeOf(varName) == "Array") \
                    or (self.functionSymbolTable.indexOf(varName) != -1 and self.functionSymbolTable.typeOf(varName) == "Array"):
            arr = self.jktk.keyWord()
            self.jktk.advance()
            if self.jktk.symbol() == "[":
                arrayHandle = True
                self.jktk.advance()
                if self.jktk.tokenType() == "INT_CONST":
                    self.vmWriter.writePush("constant", self.jktk.intVal())
                    self.jktk.advance()
                else:
                    self.compileExpression(terminator=["]"])
                self.vmWriter.writePush(self.getSymbolData(arr)[0], self.getSymbolData(arr)[1])
                self.vmWriter.writeArithmetic("+")
                assert self.jktk.symbol() == "]", self.jktk.symbol()
                self.jktk.advance()
        else:
            self.jktk.advance()
        assert self.jktk.symbol() == "="
        self.jktk.advance()
        self.compileExpression(terminator=[";"])
        assert self.jktk.symbol() == ";", self.jktk.symbol()
        if arrayHandle:
            self.vmWriter.writePop("temp", 0)
            self.vmWriter.writePop("pointer", 1)
            self.vmWriter.writePush("temp", 0)
            self.vmWriter.writePop("that", 0)
        else:
            self.vmWriter.writePop(self.getSymbolData(varName)[0], self.getSymbolData(varName)[1])
        assert self.jktk.symbol() == ";"
        self.jktk.advance()

    def compileIf(self):
        l1 = f"L{self.lNum}"
        self.lNum += 1
        l2 = f"L{self.lNum}"
        self.lNum += 1

        assert self.jktk.keyWord() == "if"
        self.jktk.advance()
        assert self.jktk.symbol() == "("
        self.jktk.advance()
        self.compileExpression(terminator=[")"])
        assert self.jktk.symbol() == ")", self.jktk.symbol()
        self.jktk.advance()
        self.vmWriter.writeNot()
        self.vmWriter.writeIf(l2)
        assert self.jktk.symbol() == "{", self.jktk.symbol()
        self.jktk.advance()
        self.compileStatements(terminator=["}"])
        assert self.jktk.symbol() == "}", self.jktk.symbol()
        self.vmWriter.writeGoto(l1)
        self.jktk.advance()
        else_process = self.jktk.tokenType() == "KEYWORD" and self.jktk.keyWord() == "else"
        if else_process:
            self.jktk.advance()
            assert self.jktk.keyWord() == "{", self.jktk.symbol()
        self.vmWriter.writeLabel(l2)
        if else_process:
            self.jktk.advance()
            self.compileStatements(terminator=["}"])
            assert self.jktk.keyWord() == "}", self.jktk.symbol()
        self.vmWriter.writeLabel(l1)
        if else_process:
            self.jktk.advance()

    def compileWhile(self):
        l1 = f"L{self.lNum}"
        self.lNum += 1
        l2 = f"L{self.lNum}"
        self.lNum += 1

        assert self.jktk.keyWord() == "while"
        self.vmWriter.writeLabel(l1)
        self.jktk.advance()
        assert self.jktk.symbol() == "("
        self.jktk.advance()
        self.compileExpression(terminator=[")"])
        assert self.jktk.symbol() == ")"
        self.jktk.advance()
        self.vmWriter.writeNot()
        self.vmWriter.writeIf(l2)
        assert self.jktk.symbol() == "{", self.jktk.symbol()
        self.jktk.advance()
        self.compileStatements(terminator=["}"])
        assert self.jktk.symbol() == "}"
        self.vmWriter.writeGoto(l1)
        self.vmWriter.writeLabel(l2)
        self.jktk.advance()

    def compileDo(self):
        assert self.jktk.keyWord() == "do"
        self.jktk.advance()
        self.compileExpression(terminator=[";"])
        self.vmWriter.writePop("temp", 0)
        assert self.jktk.symbol() == ";"

    def compileReturn(self):
        assert self.jktk.keyWord() == "return"
        self.jktk.advance()
        if self.jktk.tokenType() != "SYMBOL":
            self.compileExpression(terminator=[";"])
        else:
            self.vmWriter.writePush("constant", 0)
        assert self.jktk.symbol() == ";"
        self.vmWriter.writeReturn()

    def compileExpression(self, terminator=None):
        while not (self.jktk.tokenType() == "SYMBOL" and self.jktk.symbol(internal=False) in terminator):
            self.compileTerm()
            if self.jktk.tokenType() == "SYMBOL" and self.jktk.symbol(internal=False) in terminator:
                break
            elif not (self.jktk.tokenType() == "SYMBOL" and self.jktk.symbol(internal=False) in operators):
                self.jktk.advance()
            if self.jktk.tokenType() == "SYMBOL" and self.jktk.symbol(internal=False) in terminator:
                break
            op = self.jktk.symbol(internal=False)
            assert op in operators, op
            self.jktk.advance()
            self.compileTerm()
            self.vmWriter.writeArithmetic(op)
            if not (self.jktk.tokenType() == "SYMBOL" and self.jktk.symbol(internal=False) in terminator):
                self.jktk.advance()

    def compileTerm(self, terminator=None):
        if self.jktk.symbol() == "(":
            self.jktk.advance()
            self.compileExpression(terminator=[")"])
            assert self.jktk.symbol() == ")", self.jktk.symbol()
            self.jktk.advance()
        elif self.jktk.symbol(internal=False) in unary_operators:
            una = self.jktk.symbol(internal=False)
            self.jktk.advance()
            self.compileTerm()
            self.vmWriter.writeArithmetic(una)
        elif (self.classSymbolTable.indexOf(self.jktk.keyWord()) != -1 and self.classSymbolTable.typeOf(self.jktk.keyWord()) == "Array") \
                    or (self.functionSymbolTable.indexOf(self.jktk.keyWord()) != -1 and self.functionSymbolTable.typeOf(self.jktk.keyWord()) == "Array"):
            arr = self.jktk.keyWord()
            self.jktk.advance()
            if self.jktk.symbol() == "[":
                self.jktk.advance()
                ind = self.jktk.symbol()
                if self.jktk.tokenType() == "INT_CONST":
                    self.vmWriter.writePush("constant", ind)
                    self.jktk.advance()
                else:
                    self.compileExpression(terminator=["]"])
                self.vmWriter.writePush(self.getSymbolData(arr)[0], self.getSymbolData(arr)[1])
                self.vmWriter.writeArithmetic("+")
                assert self.jktk.symbol() == "]", self.jktk.symbol()
                self.vmWriter.writePop("pointer", 1)
                self.vmWriter.writePush("that", 0)
                self.jktk.advance()
            else:
                self.vmWriter.writePush(self.getSymbolData(arr)[0], self.getSymbolData(arr)[1])
        elif self.jktk.tokenType() == "STRING_CONST":
            s = self.jktk.stringVal()
            self.vmWriter.writePush("constant", len(s))
            self.vmWriter.writeCall("String.new", 1)
            for c in s:
                self.vmWriter.writePush("constant", ord(c))
                self.vmWriter.writeCall("String.appendChar", 2)
        elif self.jktk.tokenType() == "INT_CONST":
            self.vmWriter.writePush("constant", self.jktk.intVal())
        elif self.jktk.tokenType() == "KEYWORD" and self.jktk.keyWord() == "null":
            self.vmWriter.writePush("constant", 0)
        elif self.jktk.keyWord() == "true":
            self.vmWriter.writePush("constant", 1)
            self.vmWriter.writeArithmetic("neg")
        elif self.jktk.keyWord() == "false":
            self.vmWriter.writePush("constant", 0)
        else:
            tmp = self.jktk.keyWord()
            token = self.jktk.tokenType()
            self.jktk.advance()
            if self.jktk.symbol() == ".":
                nArgs = 0
                if self.classSymbolTable.indexOf(tmp) != -1 or self.functionSymbolTable.indexOf(tmp) != -1:
                    self.vmWriter.writePush(self.getSymbolData(tmp)[0], self.getSymbolData(tmp)[1])
                    tmp = self.classSymbolTable.typeOf(tmp) if self.classSymbolTable.indexOf(tmp) != -1 else self.functionSymbolTable.typeOf(tmp)
                    nArgs += 1
                tmp += self.jktk.symbol()
                self.jktk.advance()
                tmp += self.jktk.keyWord()
                self.jktk.advance()
                assert self.jktk.symbol() == "("
                nArgs += self.compileExpressionList(terminator=[")"])
                self.vmWriter.writeCall(tmp, nArgs)
                self.jktk.advance()
            elif self.jktk.symbol() == "(":
                nArgs = 1
                self.vmWriter.writePush("pointer", 0)
                nArgs += self.compileExpressionList(terminator=[")"])
                self.vmWriter.writeCall(f"{self.className}.{tmp}", nArgs)
                self.jktk.advance()
            elif token == "INT_CONST":
                self.vmWriter.writePush("constant", int(tmp))
            else:
                self.vmWriter.writePush(self.getSymbolData(tmp)[0], self.getSymbolData(tmp)[1])

    def compileExpressionList(self, terminator=None) -> int:
        count = 0
        if terminator is not None:
            while not (self.jktk.tokenType() == "SYMBOL" and self.jktk.symbol(internal=False) in terminator):
                self.jktk.advance()
                if self.jktk.tokenType() == "SYMBOL" and self.jktk.symbol(internal=False) in terminator:
                    break
                self.compileExpression(terminator=[',', ')'])
                assert self.jktk.symbol(internal=False) in [',', ')'], self.jktk.symbol(internal=False)
                count += 1
        return count

    def getSymbolData(self, varName):
        k = None
        i = None
        if self.classSymbolTable.indexOf(varName) != -1:
            k = self.classSymbolTable.kindOf(varName)
            i = self.classSymbolTable.indexOf(varName)
        else:
            k = self.functionSymbolTable.kindOf(varName)
            i = self.functionSymbolTable.indexOf(varName)
        assert i >= 0, f"{varName} {i} {self.classSymbolTable.table} {self.functionSymbolTable.table}"
        return k, i
