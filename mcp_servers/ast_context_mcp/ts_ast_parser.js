import ts from 'typescript';
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

function printUsageAndExit() {
  console.error(`Usage:
  node scripts/ts_ast_parser.js symbols <file_path>
  node scripts/ts_ast_parser.js hash <file_path> [--symbol <symbol_name>]
  node scripts/ts_ast_parser.js skeleton <file_path>
  node scripts/ts_ast_parser.js symbol-block <file_path> <symbol_name>`);
  process.exit(1);
}

const args = process.argv.slice(2);
if (args.length < 2) {
  printUsageAndExit();
}

const action = args[0];
const allowedActions = ['symbols', 'hash', 'skeleton', 'symbol-block'];
if (!allowedActions.includes(action)) {
  console.error(`Error: Unknown action '${action}'`);
  printUsageAndExit();
}

let filePath = null;
let symbolName = null;

if (action === 'hash') {
  for (let i = 1; i < args.length; i++) {
    if (args[i] === '--symbol') {
      if (i + 1 < args.length) {
        symbolName = args[i + 1];
        i++;
      } else {
        console.error('Error: --symbol option requires a value');
        process.exit(1);
      }
    } else if (!args[i].startsWith('-')) {
      filePath = args[i];
    }
  }
} else if (action === 'symbol-block') {
  filePath = args[1];
  symbolName = args[2];
} else {
  filePath = args[1];
}

if (!filePath) {
  console.error('Error: File path is required');
  printUsageAndExit();
}

if (action === 'symbol-block' && !symbolName) {
  console.error('Error: Symbol name is required for symbol-block action');
  printUsageAndExit();
}

const resolvedPath = path.resolve(filePath);
if (!fs.existsSync(resolvedPath)) {
  console.error(`Error: File not found: ${filePath}`);
  process.exit(1);
}

const fileContent = fs.readFileSync(resolvedPath, 'utf8');

const sourceFile = ts.createSourceFile(
  resolvedPath,
  fileContent,
  ts.ScriptTarget.Latest,
  true // setParentNodes
);

function collectAllSymbols(sf, code) {
  const symbols = [];
  const nodesMap = new Map();

  function extractBindingNames(nameNode) {
    const names = [];
    function recurse(node) {
      if (ts.isIdentifier(node)) {
        names.push(node);
      } else if (ts.isObjectBindingPattern(node) || ts.isArrayBindingPattern(node)) {
        for (const element of node.elements) {
          if (ts.isBindingElement(element)) {
            recurse(element.name);
          }
        }
      }
    }
    recurse(nameNode);
    return names;
  }

  function registerSymbol(qualifiedName, type, symbolNode) {
    let startPos = symbolNode.getStart(sf);
    let docNode = symbolNode;

    if (ts.isVariableDeclaration(symbolNode) && symbolNode.parent && symbolNode.parent.parent && ts.isVariableStatement(symbolNode.parent.parent)) {
      docNode = symbolNode.parent.parent;
    }

    const comments = ts.getLeadingCommentRanges(code, docNode.pos);
    if (comments) {
      let jsdoc = null;
      for (let i = comments.length - 1; i >= 0; i--) {
        const commentText = code.substring(comments[i].pos, comments[i].end);
        if (commentText.startsWith('/**')) {
          jsdoc = comments[i];
          break;
        }
      }
      if (jsdoc) {
        startPos = jsdoc.pos;
      }
    }

    const endPos = symbolNode.getEnd();
    const startLine = sf.getLineAndCharacterOfPosition(startPos).line + 1;
    const endLine = sf.getLineAndCharacterOfPosition(endPos).line + 1;

    const nameParts = qualifiedName.split('.');
    const baseName = nameParts[nameParts.length - 1];

    const symbolInfo = {
      name: baseName,
      qname: qualifiedName,
      type: type,
      start_line: startLine,
      end_line: endLine
    };

    symbols.push(symbolInfo);
    nodesMap.set(qualifiedName, { node: symbolNode, startLine, endLine });
  }

  function traverse(node, parentName = '', insideFunctionBody = false) {
    let isSymbol = false;
    let symbolType = '';
    let symbolNameLocal = '';
    let destructuredNames = null;

    if (!insideFunctionBody) {
      if (ts.isClassDeclaration(node)) {
        isSymbol = true;
        symbolType = 'class';
        symbolNameLocal = node.name ? node.name.text : 'default';
      } else if (ts.isInterfaceDeclaration(node)) {
        isSymbol = true;
        symbolType = 'interface';
        symbolNameLocal = node.name.text;
      } else if (ts.isFunctionDeclaration(node)) {
        isSymbol = true;
        symbolType = 'function';
        symbolNameLocal = node.name ? node.name.text : 'default';
      } else if (ts.isMethodDeclaration(node)) {
        isSymbol = true;
        symbolType = 'method';
        symbolNameLocal = node.name.getText(sf);
      } else if (ts.isConstructorDeclaration(node)) {
        isSymbol = true;
        symbolType = 'constructor';
        symbolNameLocal = 'constructor';
      } else if (ts.isGetAccessorDeclaration(node)) {
        isSymbol = true;
        symbolType = 'method';
        symbolNameLocal = node.name.getText(sf);
      } else if (ts.isSetAccessorDeclaration(node)) {
        isSymbol = true;
        symbolType = 'method';
        symbolNameLocal = node.name.getText(sf);
      } else if (ts.isPropertyDeclaration(node)) {
        if (node.initializer && (ts.isFunctionExpression(node.initializer) || ts.isArrowFunction(node.initializer))) {
          isSymbol = true;
          symbolType = 'method';
          symbolNameLocal = node.name.getText(sf);
        }
      } else if (ts.isPropertyAssignment(node)) {
        if (node.initializer && (ts.isFunctionExpression(node.initializer) || ts.isArrowFunction(node.initializer))) {
          isSymbol = true;
          symbolType = 'method';
          symbolNameLocal = node.name.getText(sf);
        }
      } else if (ts.isVariableDeclaration(node)) {
        if (node.parent && node.parent.parent && ts.isVariableStatement(node.parent.parent)) {
          if (ts.isIdentifier(node.name)) {
            isSymbol = true;
            symbolType = 'variable';
            symbolNameLocal = node.name.text;
          } else if (ts.isObjectBindingPattern(node.name) || ts.isArrayBindingPattern(node.name)) {
            destructuredNames = extractBindingNames(node.name);
          }
        }
      } else if (ts.isTypeAliasDeclaration(node)) {
        isSymbol = true;
        symbolType = 'type';
        symbolNameLocal = node.name.text;
      } else if (ts.isEnumDeclaration(node)) {
        isSymbol = true;
        symbolType = 'enum';
        symbolNameLocal = node.name.text;
      } else if (ts.isModuleDeclaration(node)) {
        isSymbol = true;
        symbolType = 'module';
        symbolNameLocal = node.name.text;
      }
    }

    let nextParentName = parentName;
    if (isSymbol) {
      const qualifiedName = parentName ? `${parentName}.${symbolNameLocal}` : symbolNameLocal;
      nextParentName = qualifiedName;
      registerSymbol(qualifiedName, symbolType, node);
    } else if (destructuredNames) {
      for (const idNode of destructuredNames) {
        const localName = idNode.text;
        const qualifiedName = parentName ? `${parentName}.${localName}` : localName;
        registerSymbol(qualifiedName, 'variable', node);
      }
    }

    const isFunctionLike =
      ts.isFunctionDeclaration(node) ||
      ts.isMethodDeclaration(node) ||
      ts.isConstructorDeclaration(node) ||
      ts.isGetAccessorDeclaration(node) ||
      ts.isSetAccessorDeclaration(node) ||
      ts.isArrowFunction(node) ||
      ts.isFunctionExpression(node);

    const nextInsideFunctionBody = insideFunctionBody || isFunctionLike;

    ts.forEachChild(node, child => {
      traverse(child, nextParentName, nextInsideFunctionBody);
    });
  }

  traverse(sf);
  return { symbols, nodesMap };
}

if (action === 'symbols') {
  const { symbols } = collectAllSymbols(sourceFile, fileContent);
  console.log(JSON.stringify(symbols));
  process.exit(0);
}

function normalizeWhitespace(text) {
  return text.trim();
}

if (action === 'hash') {
  const printer = ts.createPrinter({ removeComments: true });
  let textToHash = '';
  let matchKey = null;

  if (symbolName) {
    const { nodesMap } = collectAllSymbols(sourceFile, fileContent);
    let match = nodesMap.get(symbolName);
    matchKey = symbolName;

    if (!match) {
      const entry = [...nodesMap.entries()].find(([k]) => k.endsWith('.' + symbolName));
      if (entry) {
        matchKey = entry[0];
        match = entry[1];
      }
    }

    if (!match) {
      console.error(`Error: Symbol '${symbolName}' not found`);
      process.exit(1);
    }

    textToHash = printer.printNode(ts.EmitHint.Unspecified, match.node, sourceFile);
  } else {
    textToHash = printer.printFile(sourceFile);
  }

  const normalizedText = normalizeWhitespace(textToHash);
  const hash = crypto.createHash('sha256').update(normalizedText).digest('hex');

  const output = {
    file: filePath,
    symbol: symbolName ? matchKey : null,
    hash: hash,
    algorithm: "sha256"
  };
  console.log(JSON.stringify(output));
  process.exit(0);
}

if (action === 'skeleton') {
  const replacements = [];

  function findReplacements(node, insideReplaceableBody = false) {
    let isReplaceable = false;
    if (
      ts.isFunctionDeclaration(node) ||
      ts.isMethodDeclaration(node) ||
      ts.isConstructorDeclaration(node) ||
      ts.isGetAccessorDeclaration(node) ||
      ts.isSetAccessorDeclaration(node) ||
      ts.isFunctionExpression(node) ||
      ts.isArrowFunction(node)
    ) {
      if (node.body) {
        isReplaceable = true;
        if (!insideReplaceableBody) {
          const isBlock = ts.isBlock(node.body);
          replacements.push({
            start: node.body.getStart(sourceFile),
            end: node.body.getEnd(),
            replacement: isBlock ? '{ /* ... */ }' : '/* ... */'
          });
        }
      }
    }

    ts.forEachChild(node, child => {
      findReplacements(child, insideReplaceableBody || isReplaceable);
    });
  }

  findReplacements(sourceFile);
  replacements.sort((a, b) => b.start - a.start);

  let skeletonContent = fileContent;
  for (const { start, end, replacement } of replacements) {
    skeletonContent = skeletonContent.substring(0, start) + replacement + skeletonContent.substring(end);
  }

  console.log(skeletonContent);
  process.exit(0);
}

if (action === 'symbol-block') {
  const { nodesMap } = collectAllSymbols(sourceFile, fileContent);
  let match = nodesMap.get(symbolName);

  if (!match) {
    const entry = [...nodesMap.entries()].find(([k]) => k.endsWith('.' + symbolName));
    if (entry) {
      match = entry[1];
    }
  }

  if (!match) {
    console.error(`Error: Symbol '${symbolName}' not found`);
    process.exit(1);
  }

  const lines = fileContent.split(/\r?\n/);
  const extractedLines = lines.slice(match.startLine - 1, match.endLine);

  console.log(extractedLines.join('\n'));
  process.exit(0);
}
