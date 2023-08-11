from lark.exceptions import UnexpectedInput
from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_DEFINITION,
    TEXT_DOCUMENT_DID_CLOSE,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_SAVE,
    TEXT_DOCUMENT_HOVER,
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionParams,
    DefinitionParams,
    Diagnostic,
    DidCloseTextDocumentParams,
    DidOpenTextDocumentParams,
    DidSaveTextDocumentParams,
    Hover,
    HoverParams,
    LocationLink,
    MarkupContent,
    MarkupKind,
)
from pygls.server import LanguageServer
from rich import print  # type: ignore

from .incomplete import FunctionScope, IncompleteParser, StackScope, UnknownScope
from .lib import lark_exception_to_diagnostic, parse_documentation, position_to_index
from .parser import parser
from .sourceinfo import SourceInfo

PORT = 6001
server = LanguageServer("goboscript-lsp", "0.1.0")
documentation = parse_documentation()


class Document:
    def __init__(self, uri: str, source: str):
        self.uri = uri
        self.parse_err: UnexpectedInput | None = None
        self.update_ast(source)

    def update_ast(self, source: str):
        try:
            self.ast = parser.parse(source)
            self.parse_err = None
            self.source_info = SourceInfo(self.ast)
        except UnexpectedInput as err:
            self.parse_err = err

    def get_diagnostics(self) -> list[Diagnostic]:
        if self.parse_err:
            return [lark_exception_to_diagnostic(self.parse_err)]
        return []


documents: dict[str, Document] = {}


@server.feature(TEXT_DOCUMENT_DID_OPEN)
@server.feature(TEXT_DOCUMENT_DID_SAVE)
def get_diagnostics(
    ls: LanguageServer, params: DidOpenTextDocumentParams | DidSaveTextDocumentParams
):
    source = ls.workspace.get_document(params.text_document.uri).source
    if params.text_document.uri in documents:
        document = documents[params.text_document.uri]
    else:
        document = Document(params.text_document.uri, source)
        documents[params.text_document.uri] = document
    document.update_ast(source)
    ls.publish_diagnostics(params.text_document.uri, document.get_diagnostics())


@server.feature(TEXT_DOCUMENT_DID_CLOSE)
def close_document(ls: LanguageServer, params: DidCloseTextDocumentParams):
    if params.text_document.uri in documents:
        documents.pop(params.text_document.uri)


@server.feature(TEXT_DOCUMENT_HOVER)
def get_hover(ls: LanguageServer, params: HoverParams) -> Hover | None:
    if params.text_document.uri not in documents:
        return
    source = ls.workspace.get_document(params.text_document.uri).source
    document = documents[params.text_document.uri]
    position = position_to_index(source, params.position)
    parser = IncompleteParser(source, position)
    if parser.word:
        if hoverable := (
            document.source_info.functions.get(parser.word)
            or document.source_info.macros.get(parser.word)
            or document.source_info.block_macros.get(parser.word)
            or documentation.statement_blocks.get(parser.word)
            or documentation.reporter_blocks.get(parser.word)
        ):
            return Hover(MarkupContent(MarkupKind.Markdown, hoverable.hover()))


@server.feature(TEXT_DOCUMENT_DEFINITION)
def get_definition(ls: LanguageServer, params: DefinitionParams) -> LocationLink | None:
    if params.text_document.uri not in documents:
        return
    source = ls.workspace.get_document(params.text_document.uri).source
    document = documents[params.text_document.uri]
    position = position_to_index(source, params.position)
    parser = IncompleteParser(source, position)
    if parser.word:
        if definitionable := (
            document.source_info.functions.get(parser.word)
            or document.source_info.macros.get(parser.word)
            or document.source_info.block_macros.get(parser.word)
            or document.source_info.variables.get(parser.word)
            or document.source_info.lists.get(parser.word)
        ):
            return LocationLink(
                document.uri, definitionable.definition(), definitionable.definition()
            )


@server.feature(TEXT_DOCUMENT_COMPLETION)
def get_completion(
    ls: LanguageServer, params: CompletionParams
) -> CompletionList | None:
    if params.text_document.uri not in documents:
        return
    source = ls.workspace.get_document(params.text_document.uri).source
    document = documents[params.text_document.uri]
    position = position_to_index(source, params.position)
    parser = IncompleteParser(source, position - 1)
    completions: list[CompletionItem] = []
    if isinstance(parser.cursor_scope, StackScope):
        for function in document.source_info.functions.values():
            completions.append(
                CompletionItem(function.name, kind=CompletionItemKind.Function)
            )
        for block_macro in document.source_info.block_macros.values():
            completions.append(
                CompletionItem(block_macro.name, kind=CompletionItemKind.Class)
            )
        for statement in documentation.statement_blocks.values():
            completions.append(
                CompletionItem(statement.name, kind=CompletionItemKind.Constructor)
            )
    elif isinstance(parser.cursor_scope, UnknownScope):
        if isinstance(parser.block_scope, FunctionScope):
            function = document.source_info.functions[parser.block_scope.name]
            for argument in function.arguments:
                completions.append(
                    CompletionItem(f"${argument}", kind=CompletionItemKind.Field)
                )
        for macro in document.source_info.macros.values():
            completions.append(
                CompletionItem(macro.name, kind=CompletionItemKind.Function)
            )
        for reporter in documentation.reporter_blocks.values():
            completions.append(
                CompletionItem(reporter.name, kind=CompletionItemKind.Constructor)
            )
    if isinstance(parser.block_scope, FunctionScope):
        function = document.source_info.functions[parser.block_scope.name]
        for local in function.locals.values():
            completions.append(
                CompletionItem(local.name, kind=CompletionItemKind.Variable)
            )
    for variable in document.source_info.variables.values():
        completions.append(
            CompletionItem(variable.name, kind=CompletionItemKind.Variable)
        )
    for lust in document.source_info.lists.values():
        completions.append(CompletionItem(lust.name, kind=CompletionItemKind.Variable))
    return CompletionList(is_incomplete=False, items=completions)


server.start_tcp("127.0.0.1", PORT)
