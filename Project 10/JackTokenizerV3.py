from collections import deque
import re
from xml.sax.saxutils import escape

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
                new_tokens = []
                string_process = False
                cur_token = ""
                for t in l:
                    if t == '"':
                        if string_process:
                            new_tokens.append(("str", cur_token))
                            cur_token = ""
                            string_process = False
                        else:
                            string_process = True
                    elif string_process:
                        cur_token += t
                    elif t.isspace():
                        if len(cur_token) > 0:
                            new_tokens.append(cur_token)
                            cur_token = ""
                    elif not self.identifierRegex.match(t[0]):
                        if len(cur_token) > 0:
                            new_tokens.append(cur_token)
                            cur_token = ""
                        new_tokens.append(t)
                    else:
                        cur_token += t

                self.tokens.extend(new_tokens)

    def hasMoreTokens(self) -> bool:
        return len(self.tokens) > 0

    def advance(self):
        self.token = self.tokens.popleft()

    def tokenType(self) -> str:
        if self.token[0] == "str":
            return "STRING_CONST"
        elif self.token in symbols:
            return "SYMBOL"
        elif self.token.upper() in keys:
            return "KEYWORD"
        elif self.identifierRegex.match(self.token):
            return "IDENTIFIER"
        elif self.token.isdigit():
            return "INT_CONST"

    def keyWord(self) -> str:
        return self.token

    def symbol(self, internal=True) -> str:
        if internal and self.token in ['<', '>']: return escape(self.token)
        return self.token

    def identifier(self) -> str:
        return self.token

    def intVal(self) -> int:
        return int(self.token)

    def stringVal(self) -> str:
        return self.token[1]