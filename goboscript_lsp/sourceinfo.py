from typing import cast

from lark.lexer import Token
from lark.tree import Tree
from lark.visitors import Interpreter, Visitor

from .types import BlockMacro, Function, List, Macro, Variable

__all__ = ["SourceInfo"]


class SourceInfo(Interpreter[Token, None]):
    def __init__(self, tree: Tree[Token]):
        self.variables: dict[str, Variable] = {}
        self.lists: dict[str, List] = {}
        self.functions: dict[str, Function] = {}
        self.macros: dict[str, Macro] = {}
        self.block_macros: dict[str, BlockMacro] = {}
        self.visit_children(tree)

    def declr_function(self, node: Tree[Token], no_warp: bool = False):
        name = cast(Token, node.children[0])
        arguments = cast(list[Token], node.children[1:-1])
        body = cast(Tree[Token], node.children[-1])
        if arguments == [None]:
            arguments = []
        self.functions[str(name)] = Function(name, arguments, no_warp, {})
        SourceInfoVisitor(self, body, function=str(name))

    def declr_on(self, node: Tree[Token]):
        body = cast(Tree[Token], node.children[-1])
        SourceInfoVisitor(self, body)

    def declr_function_nowarp(self, node: Tree[Token]):
        self.declr_function(node, no_warp=True)

    declr_onflag = declr_on
    declr_onkey = declr_on
    declr_onclick = declr_on
    declr_onbackdrop = declr_on
    declr_onloudness = declr_on
    declr_ontimer = declr_on
    declr_onclone = declr_on

    def declr_macro(self, node: Tree[Token]):
        name = cast(Token, node.children[0])
        arguments = cast(list[Token], node.children[1:-1])
        # body = cast(Tree[Token], node.children[-1])
        if arguments == [None]:
            arguments = []
        self.macros[str(name)] = Macro(name, arguments)

    def declr_block_macro(self, node: Tree[Token]):
        name = cast(Token, node.children[0])
        arguments = cast(list[Token], node.children[1:-1])
        # body = cast(Tree[Token], node.children[-1])
        if arguments == [None]:
            arguments = []
        self.block_macros[str(name)] = BlockMacro(name, arguments)


class SourceInfoVisitor(Visitor[Token]):
    def __init__(
        self, source_info: SourceInfo, tree: Tree[Token], function: str | None = None
    ):
        self.source_info = source_info
        self.function = function
        self.visit(tree)

    def varset(self, node: Tree[Token]):
        name = node.children[0]
        if not isinstance(name, Token):
            return
        if str(name) not in self.source_info.variables:
            self.source_info.variables[str(name)] = Variable(name)

    def localvar(self, node: Tree[Token]):
        name = node.children[0]
        if not isinstance(name, Token):
            return
        if self.function:
            self.source_info.functions[self.function].locals[str(name)] = Variable(name)

    def listset(self, node: Tree[Token]):
        name = node.children[0]
        if not isinstance(name, Token):
            return
        if str(name) not in self.source_info.lists:
            self.source_info.lists[str(name)] = List(name)
