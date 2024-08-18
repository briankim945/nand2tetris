from collections import deque
import re

from jack_constants import keys, symbols

class JackTokenizer:

    def __init__(self, fileStream):
        self.fileStream = fileStream
        self.token = None
        self.tokens = deque()
        self.nextLine = None
        self.identifierRegex = re.compile(r"[a-zA-Z\_]{1}\w*")
        self.nextLine = self.fileStream.readline()
        while self.nextLine == '\n' or (len(self.nextLine) > 0 and self.nextLine[0] == '/'):
            self.nextLine = self.fileStream.readline()

    def hasMoreTokens(self) -> bool:
        return len(self.tokens) > 0 or len(self.nextLine) > 0

    def advance(self):
        if len(self.tokens) == 0:
            init_tokens = self.nextLine.split()
            print(self.nextLine, init_tokens)
            new_tokens = []
            for t in init_tokens:
                if len(t) == 1:
                    new_tokens.append(t)
                    continue
                if not self.identifierRegex.match(t[0]):
                    new_tokens.append(t[0])
                    t = t[1:]
                if len(t) == 1:
                    new_tokens.append(t)
                    continue
                if not self.identifierRegex.match(t[-1]):
                    new_tokens.append(t[:-1])
                    new_tokens.append(t[-1])
                else:
                    new_tokens.append(t)

            self.tokens.extend(self.nextLine.split())
            print("tokens", self.tokens)
            self.nextLine = self.fileStream.readline()
            while (len(self.nextLine) > 0 and len(self.nextLine.split()) == 0) or (len(self.nextLine) > 0 and self.nextLine[0] == '/'):
                self.nextLine = self.fileStream.readline()
        self.token = self.tokens.popleft()

    def tokenType(self) -> str:
        if self.token[0] in symbols:
            return "SYMBOL"
        elif self.token.upper() in keys:
            return "KEYWORD"
        elif self.identifierRegex.match(self.token):
            return "IDENTIFIER"
        elif self.token.isdigit():
            return "INT_CONST"
        elif self.token[0] == '"' and self.token[-1] == '"':
            return "STRING_CONST"

    def keyWord(self) -> str:
        return self.token

    def symbol(self) -> str:
        return self.token

    def identifier(self) -> str:
        return self.token

    def intVal(self) -> int:
        return int(self.token)

    def stringVal(self) -> str:
        return self.token