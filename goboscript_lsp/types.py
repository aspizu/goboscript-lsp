from dataclasses import dataclass

from lark.lexer import Token
from lsprotocol.types import Position, Range


def token_to_range(token: Token) -> Range:
    # I don't know in what case these would be equal to None
    assert token.line is not None
    assert token.column is not None
    return Range(
        Position(token.line - 1, token.column - 1),
        Position(token.line - 1, token.column + len(token) - 1),
    )


class Hoverable:
    def hover(self) -> str:
        ...


class Definitionable:
    def definition(self) -> Range:
        ...


@dataclass
class Variable(Definitionable):
    name: Token
    references: list[Token]
    doc: Token | None = None

    def definition(self):
        return token_to_range(self.name)


@dataclass
class List(Definitionable):
    name: Token
    references: list[Token]
    doc: Token | None = None

    def definition(self):
        return token_to_range(self.name)


@dataclass
class StatementBlock(Hoverable):
    name: str
    arguments: list[str]
    doc: str

    def hover(self) -> str:
        return (
            "```goboscript\n"
            f"{self.name} {', '.join(self.arguments)};\n"
            "```\n"
            f"{self.doc}\n"
        )


@dataclass
class ReporterBlock(Hoverable):
    name: str
    arguments: list[str]
    doc: str

    def hover(self) -> str:
        return (
            "```goboscript\n"
            f"{self.name}({', '.join(self.arguments)})\n"
            "```\n"
            f"{self.doc}\n"
        )


@dataclass
class Documentation:
    statement_blocks: dict[str, StatementBlock]
    reporter_blocks: dict[str, ReporterBlock]


@dataclass
class Argument(Definitionable):
    name: Token
    references: list[Token]

    def definition(self):
        return token_to_range(self.name)


@dataclass
class Function(Hoverable, Definitionable):
    name: Token
    arguments: dict[str, Argument]
    no_warp: bool
    locals: dict[str, Variable]
    references: list[Token]
    doc: Token | None = None

    def hover(self) -> str:
        return (
            "```goboscript\n" f"def {self.name} {', '.join(self.arguments)}\n" "```\n"
        )

    def definition(self):
        return token_to_range(self.name)


@dataclass
class Macro(Hoverable, Definitionable):
    name: Token
    arguments: list[Token]
    references: list[Token]
    doc: Token | None = None

    def hover(self) -> str:
        return (
            "```goboscript\n"
            f"macro {self.name}({', '.join(self.arguments)})\n"
            "```\n"
        )

    def definition(self):
        return token_to_range(self.name)


@dataclass
class BlockMacro(Hoverable, Definitionable):
    name: Token
    arguments: list[Token]
    references: list[Token]
    doc: Token | None = None

    def hover(self) -> str:
        return (
            "```goboscript\n" f"macro {self.name} {', '.join(self.arguments)}\n" "```\n"
        )

    def definition(self):
        return token_to_range(self.name)
