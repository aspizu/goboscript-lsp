from .parser import parser
from lark import UnexpectedCharacters, UnexpectedEOF, UnexpectedInput, UnexpectedToken
from lsprotocol.types import Diagnostic, Position, Range


def user_repr(e: UnexpectedInput) -> str:
    if isinstance(e, UnexpectedCharacters):
        expected = ", ".join(e.allowed)
        return f"Expected one of: {expected}"
    elif isinstance(e, UnexpectedToken):
        expected = ", ".join(e.expected or e.accepts)
        return f"Expected one of: {expected}"
    elif isinstance(e, UnexpectedEOF):
        return f"Unexpected EOF"
    else:
        return str(e)


def get_diagnostics(doctext: str):
    diagnostics: list[Diagnostic] = []
    try:
        parser.parse(doctext)
    except UnexpectedInput as e:
        diagnostics.append(
            Diagnostic(
                Range(
                    Position(e.line - 1, e.column - 1), Position(e.line - 1, e.column)
                ),
                user_repr(e),
            )
        )
    return diagnostics
