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

        # Build token queue
        while l := self.fileStream.readline():
            if not (len(l) > 0 and len(l.split()) == 0) and not (len(l) > 0 and l[0] == '/'):
                init_tokens = l.split()
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

                self.tokens.extend(new_tokens)
        self.token = self.tokens.popleft()

    def hasMoreTokens(self) -> bool:
        return len(self.tokens) > 0

    def advance(self):
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