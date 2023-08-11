# goboscript Language Server

This software provides features such as Autocompletion, Go to definition, Documentation preview to code editors for [goboscript](https://github.com/aspizu/goboscript).

### Go to definition and documentation on hover
![](https://media.discordapp.net/attachments/972556399928299661/1139561560340172841/image.png?width=1442&height=500)
### Auto complete
![](https://media.discordapp.net/attachments/972556399928299661/1139561598256689253/image.png?width=1442&height=722)

# Installation

```sh
cd goboscript-lsp
pip install -e .
```

# Supported Editors

All editors who support the Language Server Protocol are supported.

## VS Code

Install the extension from [VSIX Package](/vscode-extension/goboscript-0.1.0.vsix)

## Helix Editor

[Helix](https://helix-editor.com/) is a modal text editor, use the following configuration.

```toml
[some configuration here]
```

# Installation

```sh
python -m pip install -e .
```

# Development

Development is against the VS Code extension.
Open [/vscode-extension/](/vscode-extension/) in VS Code and hit `F5`.

Start the language server before starting VS Code.
```sh
python -m goboscript_lsp --tcp --port 6001
```

# Footnotes

The code in [/vscode-extension/](/vscode-extension/) was adpoted from [lark-language-server](https://github.com/lark-parser/lark-language-server).
