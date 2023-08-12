from lark.exceptions import (
    UnexpectedCharacters,
    UnexpectedEOF,
    UnexpectedInput,
    UnexpectedToken,
)
from lark import Tree, Token
from lsprotocol.types import Diagnostic, DiagnosticSeverity, Position, Range

from .types import Documentation

__all__ = ["position_to_index", "lark_exception_to_diagnostic"]


def parse_documentation() -> Documentation:
    return Documentation({}, {})


def position_to_index(source: str, position: Position) -> int:
    length = 0
    for i, line in enumerate(source.splitlines()):
        if i == position.line:
            return length + position.character
        # Add 1 for newline removed by splitlines
        length += len(line) + 1
    return 0


def lark_exception_to_diagnostic(err: UnexpectedInput) -> Diagnostic:
    # Lark uses 1-indexed line and column numbers
    range = Range(
        Position(err.line - 1, err.column - 1), Position(err.line - 1, err.column - 1)
    )
    if isinstance(err, UnexpectedCharacters):
        expected = ", ".join(err.allowed)
        return Diagnostic(
            range,
            f"Expected one of: {expected}",
            DiagnosticSeverity.Error,
            "UnexpectedCharacters",
        )
    elif isinstance(err, UnexpectedToken):
        print(err.token.value)
        expected = ", ".join(err.expected or err.accepts)
        return Diagnostic(
            range,
            f"Expected one of: {expected}",
            DiagnosticSeverity.Error,
            "UnexpectedToken",
        )
    elif isinstance(err, UnexpectedEOF):
        return Diagnostic(
            range, f"Unexpected end of file.", DiagnosticSeverity.Error, "UnexpectedEOF"
        )
    else:
        raise ValueError(err)
