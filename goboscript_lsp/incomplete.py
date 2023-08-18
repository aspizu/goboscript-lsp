import string

__all__ = [
    "IncompleteParser",
    "StackScope",
    "UnknownScope",
    "FunctionScope",
    "BlockMacroScope",
    "DeclarationScope",
]

IDENTIFIER_CHARS = string.ascii_letters + string.digits + "_!$"
from dataclasses import dataclass


class CursorScope:
    ...


@dataclass
class StackScope(CursorScope):
    ...


@dataclass
class UnknownScope(CursorScope):
    ...


class BlockScope:
    ...


@dataclass
class FunctionScope(BlockScope):
    name: str


@dataclass
class BlockMacroScope(BlockScope):
    name: str


@dataclass
class DeclarationScope(BlockScope):
    ...


@dataclass
class Token:
    value: str
    line: int
    col: int


def lexer(source: str, pos_line: int, pos_col: int):
    comment = False
    quote = False
    line = 0
    col = 0
    i = 0
    tokens: list[Token] = []
    token: Token = Token("", line, col)
    while i < len(source):
        if source[i] == "\n":
            line += 1
            col = 0
        if comment:
            if source[i] == "*" and source[i + 1] == "/":
                token.value += "*/"
                col += 1
                i += 1
                comment = False
                tokens.append(token)
                token = Token("", line, col)
            elif source[i] == "\n":
                line += 1
                col = 0
            else:
                token.value += source[i]
        else:
            if quote:
                if source[i] == '"':
                    quote = False
                    token.value += '"'
                    tokens.append(token)
                    token = Token("", line, col)
                elif source[i] == "\n":
                    line += 1
                    col = 0
                else:
                    token.value += source[i]
            else:
                if source[i] == "/" and source[i + 1] == "*":
                    comment = True
                    token = Token("/*", line, col)
                    col += 1
                    i += 1
                elif source[i] == '"':
                    quote = True
                    token = Token('"', line, col)
                elif source[i] in " ()[]":
                    if token.value != "":
                        tokens.append(token)
                    token = Token("", line, col)

                elif source[i] == "\n":
                    if token.value != "":
                        tokens.append(token)
                    line += 1
                    col = 0
                    token = Token("", line, col)
                else:
                    token.value += source[i]
        col += 1
        i += 1


@dataclass
class IncompleteParser:
    word_position: int
    word: str | None
    cursor_scope: CursorScope
    block_scope: BlockScope

    def __init__(self, source: str, position: int):
        word_start_found = False
        cursor_scope_found = False
        function_found = False
        self.word_position = 0
        self.word = None
        brackets = 0
        i = position
        while i >= 0:
            if word_start_found:
                if cursor_scope_found:
                    if function_found:
                        if not hasattr(self, "block_scope"):
                            self.block_scope = DeclarationScope()
                    else:
                        if source[i] in "{}":
                            brackets += 1
                        if source[i : i + 3] == "def":
                            function_found = True
                            j = i + 3
                            while source[j] in " \n":
                                j += 1
                            function = j
                            while source[j] in IDENTIFIER_CHARS:
                                j += 1
                            if function != j and brackets % 2 != 0:
                                self.block_scope = FunctionScope(source[function:j])
                        if source[i : i + 5] == "macro":
                            function_found = True
                            j = i + 5
                            while source[j] in " \n":
                                j += 1
                            function = j
                            while source[j] in IDENTIFIER_CHARS:
                                j += 1
                            if function != j and brackets % 2 != 0:
                                self.block_scope = BlockMacroScope(source[function:j])
                else:
                    if not source[i] in " \n":
                        cursor_scope_found = True

                        if source[i] in "};":
                            self.cursor_scope = StackScope()
                        else:
                            self.cursor_scope = UnknownScope()
            else:
                if source[i] in IDENTIFIER_CHARS:
                    self.word_position = i
                else:
                    word_start_found = True
            i -= 1
        i = position
        if self.word_position != -1:
            while source[i + 1] in IDENTIFIER_CHARS:
                i += 1
            self.word = source[self.word_position : i + 1]
