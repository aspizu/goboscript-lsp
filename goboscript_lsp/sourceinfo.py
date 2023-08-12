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
        for child in tree.children:
            if isinstance(child, Tree) and child.data in (
                "declr_function",
                "declr_function_nowarp",
            ):
                name = child.children[0]
                SourceInfoVisitor(self, child, function=self.functions.get(str(name)))
            elif isinstance(child, Tree):
                SourceInfoVisitor(self, child)

    def declr_function(self, node: Tree[Token], no_warp: bool = False):
        name = cast(Token, node.children[0])
        arguments = cast(list[Token], node.children[1:-1])
        # body = cast(Tree[Token], node.children[-1])
        if arguments == [None]:
            arguments = []
        function = Function(name, arguments, no_warp, {}, [])
        self.functions[str(name)] = function

    def declr_function_nowarp(self, node: Tree[Token]):
        self.declr_function(node, no_warp=True)

    def declr_macro(self, node: Tree[Token]):
        name = cast(Token, node.children[0])
        arguments = cast(list[Token], node.children[1:-1])
        # body = cast(Tree[Token], node.children[-1])
        if arguments == [None]:
            arguments = []
        self.macros[str(name)] = Macro(name, arguments, [])

    def declr_block_macro(self, node: Tree[Token]):
        name = cast(Token, node.children[0])
        arguments = cast(list[Token], node.children[1:-1])
        # body = cast(Tree[Token], node.children[-1])
        if arguments == [None]:
            arguments = []
        self.block_macros[str(name)] = BlockMacro(name, arguments, [])


class SourceInfoVisitor(Visitor[Token]):
    def __init__(
        self,
        source_info: SourceInfo,
        tree: Tree[Token],
        function: Function | None = None,
    ):
        self.source_info = source_info
        self.function = function
        self.visit(tree)

    def varset(self, node: Tree[Token]):
        name = node.children[0]
        if not isinstance(name, Token):
            return
        if self.function:
            if variable := self.function.locals.get(str(name)):
                variable.references.append(name)
                return
        if variable := self.source_info.variables.get(str(name)):
            variable.references.append(name)
            return
        self.source_info.variables[str(name)] = Variable(name, [])

    def localvar(self, node: Tree[Token]):
        name = node.children[0]
        if not isinstance(name, Token):
            return
        if self.function:
            if variable := self.function.locals.get(str(name)):
                variable.references.append(name)
                return
            self.function.locals[str(name)] = Variable(name, [])

    def listset(self, node: Tree[Token]):
        name = node.children[0]
        if not isinstance(name, Token):
            return
        if list_ := self.source_info.lists.get(str(name)):
            list_.references.append(name)
            return
        self.source_info.lists[str(name)] = List(name, [])

    def block(self, node: Tree[Token]):
        name = node.children[0]
        if not isinstance(name, Token):
            return
        if function := self.source_info.functions.get(str(name)):
            function.references.append(name)

    def block_macro(self, node: Tree[Token]):
        name = node.children[0]
        if not isinstance(name, Token):
            return
        if block_macro := self.source_info.block_macros.get(str(name)):
            block_macro.references.append(name)

    def macro(self, node: Tree[Token]):
        name = node.children[0]
        if not isinstance(name, Token):
            return
        if macro := self.source_info.macros.get(str(name)):
            macro.references.append(name)

    def var(self, node: Tree[Token]):
        name = node.children[0]
        if not isinstance(name, Token):
            return
        if self.function:
            if variable := self.function.locals.get(str(name)):
                variable.references.append(name)
                return
        if variable := self.source_info.variables.get(str(name)):
            variable.references.append(name)

    varchange = var
    varsub = var
    varmul = var
    vardiv = var
    varmod = var
    varjoin = var

    def listdelete(self, node: Tree[Token]):
        name = node.children[0]
        if not isinstance(name, Token):
            return
        if list_ := self.source_info.lists.get(str(name)):
            list_.references.append(name)

    listinsert = listdelete
    listreplace = listdelete
    listreplaceadd = listdelete
    listreplacesub = listdelete
    listreplacemul = listdelete
    listreplacediv = listdelete
    listreplacemod = listdelete
    listreplacejoin = listdelete
    listshow = listdelete
    listhide = listdelete
    listitem = listdelete
    listindex = listdelete
    listcontains = listdelete
    listlength = listdelete
