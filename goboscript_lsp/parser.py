import importlib.resources
from lark.lark import Lark
from . import res

parser = Lark(
    (importlib.resources.files(res) / "grammar.lark").open(),
    parser="earley",
    propagate_positions=True,
)
