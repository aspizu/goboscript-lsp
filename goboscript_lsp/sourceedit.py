from typing import cast
from lark import Token, Tree
from lsprotocol.types import Position, TextEdit
from goboscript_lsp.sourceinfo import SourceInfo
from goboscript_lsp.types import BlockMacro, Macro, token_to_range


def search_token(
    node: Tree[Token] | Token, position: Position, function: Tree[Token] | None = None
) -> tuple[Token, Tree[Token] | None] | None:
    line = position.line + 1
    column = position.character + 1
    if (
        isinstance(node, Token)
        and node.column is not None
        and node.line == line
        and node.column <= column <= node.column + len(node)
    ):
        return node, function
    elif isinstance(node, Tree) and node.meta.line <= line <= node.meta.end_line:
        if node.data in ("declr_function", "declr_function_nowarp"):
            function = node
        for child in node.children:
            if found := search_token(child, position, function):
                return found


class SourceEdit:
    def __init__(self, tree: Tree[Token], source_info: SourceInfo):
        self.source_info = source_info
        self.ast = tree

    def rename_symbol(self, position: Position, new_name: str) -> list[TextEdit]:
        token = search_token(self.ast, position)
        if token is None:
            return []
        token, function = token
        name = None
        if function:
            name = cast(Token, function.children[0])
        edits: list[TextEdit] = []
        if referenceable := (
            self.source_info.variables.get(str(token))
            or self.source_info.lists.get(str(token))
            or self.source_info.functions.get(str(token))
            or self.source_info.block_macros.get(str(token))
            or self.source_info.macros.get(str(token))
        ):
            if isinstance(referenceable, (BlockMacro, Macro)) and new_name[-1] != "!":
                new_name = new_name + "!"
            edits.extend(
                (
                    TextEdit(token_to_range(token), new_name)
                    for token in referenceable.references
                )
            )
            edits.append(TextEdit(token_to_range(referenceable.name), new_name))
        elif function := self.source_info.functions.get(str(name)):
            qualname = str(token)
            if qualname[0] == "$":
                qualname = qualname[1:]
            if argument := function.arguments.get(qualname):
                if new_name[0] != "$":
                    new_name = "$" + new_name
                edits.extend(
                    (
                        TextEdit(token_to_range(token), new_name)
                        for token in argument.references
                    )
                )
                edits.append(TextEdit(token_to_range(argument.name), new_name[1:]))
        return edits
