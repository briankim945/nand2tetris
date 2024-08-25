from collections import deque
import re
from xml.sax.saxutils import escape

from jack_constants import keys, symbols, unary_operators

class JackTokenizer:

    def __init__(self, fileStream):
        self.fileStream = fileStream
        self.token = None
        self.tokens = deque()
        self.nextLine = None
        self.identifierRegex = re.compile(r"[a-zA-Z\_]{1}\w*")

        # Build token queue
        unary_rev = {v: k for k, v in unary_operators.items()}
        multiline_commenting = False
        while l := self.fileStream.readline():
            if not (len(l) > 0 and len(l.split()) == 0):
                new_tokens = []
                string_process = False
                cur_token = ""
                for i, t in enumerate(l):
                    if multiline_commenting:
                        if t == '/' and i > 0 and l[i - 1] == '*':
                            multiline_commenting = False
                    else:
                        if t == '/' and i < len(l) - 1 and l[i + 1] == '/':
                            break
                        elif t == '/' and i < len(l) - 2 and l[i + 1:i + 3] == '**':
                            multiline_commenting = True
                        elif t == '"':
                            if string_process:
                                new_tokens.append(("str", cur_token))
                                cur_token = ""
                                string_process = False
                            else:
                                string_process = True
                        elif string_process:
                            cur_token += t
                        else:
                            if cur_token.isnumeric() and not t.isnumeric():
                                new_tokens.append(cur_token)
                                cur_token = ""

                            if t.isspace():
                                if len(cur_token) > 0:
                                    new_tokens.append(cur_token)
                                    cur_token = ""
                            elif (len(cur_token) == 0 or cur_token.isnumeric()) and t.isnumeric():
                                cur_token += t
                            elif not self.identifierRegex.match(t):
                                if len(cur_token) > 0:
                                    new_tokens.append(cur_token)
                                    cur_token = ""
                                if t in unary_rev and i < len(l) - 1 and (self.identifierRegex.match(l[i + 1]) or l[i + 1].isnumeric() or l[i + 1] == '('):
                                    new_tokens.append(unary_rev[t])
                                else:
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
        elif self.token in symbols or self.token in unary_operators:
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
        if internal and self.token in ['&', '<', '>']: return escape(self.token)
        elif self.token in unary_operators and internal: return unary_operators[self.token]
        return self.token

    def identifier(self) -> str:
        return self.token

    def intVal(self) -> int:
        return int(self.token)

    def stringVal(self) -> str:
        return self.token[1]