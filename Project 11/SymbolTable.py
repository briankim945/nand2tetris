class SymbolTable:
    def __init__(self):
        self.table = []
        self.indices = {
            "static": 0,
            "this": 0,
            "argument": 0,
            "VAR": 0,
            "local": 0,
            "pointer": 0,
        }

    def reset(self):
        self.table = []
        self.indices = {
            "static": 0,
            "this": 0,
            "argument": 0,
            "VAR": 0,
            "local": 0,
            "pointer": 0,
        }

    def define(self, name: str, kind: str, type: str):
        self.table.append((name, kind, type, self.indices[kind]))
        self.indices[kind] += 1

    def varCount(self, type: str) -> int:
        return len([s for s in self.table if s[1] == type])

    def kindOf(self, name: str)-> str:
        for t in self.table:
            if t[0] == name:
                return t[1]
        return "NONE"

    def typeOf(self, name: str) -> str:
        for t in self.table:
            if t[0] == name:
                return t[2]
        return "NONE"

    def indexOf(self, name: str) -> int:
        for t in self.table:
            if t[0] == name:
                return t[3]
        return -1