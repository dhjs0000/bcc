const {
    createConnection,
    TextDocuments,
    ProposedFeatures,
    CompletionItem,
    CompletionItemKind,
    Diagnostic,
    DiagnosticSeverity,
} = require('vscode-languageserver/node');

const { TextDocument } = require('vscode-languageserver-textdocument');
const { spawn } = require('child_process');
const path = require('path');

// 创建本地连接
const connection = createConnection(ProposedFeatures.all);
const documents = new TextDocuments(TextDocument);

// 初始化
connection.onInitialize(() => ({
    capabilities: {
        completionProvider: {
            triggerCharacters: ['.', ':']  // 触发自动完成的字符
        },
        hoverProvider: true
    }
}));

// 本地代码补全数据
const localCompletions = {
    keywords: ['if', 'for', 'def', 'public', 'private', 'return', 'class'],
    functions: ['print', 'printnln'],
    types: ['BCC.Codeblock'],
    properties: ['lines']
};

// 代码补全处理
connection.onCompletion((params) => {
    const document = documents.get(params.textDocument.uri);
    const text = document.getText();
    const position = params.position;
    const line = document.getText({
        start: { line: position.line, character: 0 },
        end: { line: position.line, character: position.character }
    });

    const items = [];

    // 添加关键字
    localCompletions.keywords.forEach(keyword => {
        items.push({
            label: keyword,
            kind: CompletionItemKind.Keyword
        });
    });

    // 添加函数
    localCompletions.functions.forEach(func => {
        items.push({
            label: func,
            kind: CompletionItemKind.Function,
            insertText: `${func}($0)`
        });
    });

    // BCC.Codeblock 相关补全
    if (line.includes(':')) {
        items.push({
            label: 'BCC.Codeblock',
            kind: CompletionItemKind.Class,
            detail: 'Code block parameter type'
        });
    }

    return items;
});

// 本地文档验证
async function validateDocument(document) {
    const text = document.getText();
    const lines = text.split('\n');
    const diagnostics = [];

    // 简单的本地语法检查
    lines.forEach((line, i) => {
        // 检查未闭合的括号
        const openBraces = (line.match(/{/g) || []).length;
        const closeBraces = (line.match(/}/g) || []).length;
        if (openBraces !== closeBraces) {
            diagnostics.push({
                severity: DiagnosticSeverity.Error,
                range: {
                    start: { line: i, character: 0 },
                    end: { line: i, character: line.length }
                },
                message: '括号不匹配',
                source: 'bcc'
            });
        }
    });

    connection.sendDiagnostics({ uri: document.uri, diagnostics });
}

// 监听文档变化
documents.onDidChangeContent(change => {
    validateDocument(change.document);
});

// 启动服务器
documents.listen(connection);
connection.listen(); 