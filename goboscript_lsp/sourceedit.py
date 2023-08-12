from lark import Token, Tree
from lsprotocol.types import Position

from goboscript_lsp.sourceinfo import SourceInfo
from .lib import search_token


class SourceEdit:
    def __init__(self, tree: Tree[Token], source_info: SourceInfo):
        self.source_info = source_info
        self.ast = tree

    def rename_symbol(self, position: Position, new_name: str):
        token = search_token(self.ast, position.line - 1, position.character - 1)
        if token is None:
            return
        if variable := self.source_info.variables.get(str(token)):
            print(variable.references)
