from lark import Token, Tree
from lsprotocol.types import Position, TextEdit
from goboscript_lsp.sourceinfo import SourceInfo
from goboscript_lsp.types import BlockMacro, Macro, token_to_range
from .lib import search_token


class SourceEdit:
    def __init__(self, tree: Tree[Token], source_info: SourceInfo):
        self.source_info = source_info
        self.ast = tree

    def rename_symbol(self, position: Position, new_name: str) -> list[TextEdit]:
        token = search_token(self.ast, position)
        if token is None:
            return []
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
        return edits
