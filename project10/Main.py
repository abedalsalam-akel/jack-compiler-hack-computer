# Author: Abedalsalam Akel 
import sys 
import os 
import re

class Compiler():
    # Lists of symbols, operators, keywords, and constants used in the compiler.
    symbols_unary_operators = ['-', '~']
    symbols_binary_operators = ['+', '-', '*', '/', '&', '|', '=', '<', '>']
    keywords = ['class', 'constructor', 'function' , 'method', 'field', 'static', 'var', 'int', 'char', 'boolean',
                'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']
    constants = ['integerConstant' ,'stringConstant' , 'true', 'false', 'null', 'this']

     # Initializes the Compiler class with token list and other variables.
    def __init__(self, tokens):
        self._tokens = tokens
        self._indentation = ''
        self._curr_token = 0
        self._next_token = 1
        self._curr_statement = []
        self._output = []
        self.compileClass()

    # Advances to the next token in the list.
    def advance(self):
        self._curr_token, self._next_token = self._curr_token +1 , self._next_token +1 
    
    # Generates XML for terminal tokens.
    def generate_XMLT(self, token):
        prefix = '<' + token[0] +'> '
        suffix = ' </' + token[0] +'>\n'
        self._output.append(self._indentation + prefix + token[1] + suffix)
        self.advance()

    # Generates XML for non-terminal tokens.
    def generate_XMLnT(self, statement ,start=1):
        if start == 1:
            out_str = self._indentation + '<' + statement + '>\n'
            self._curr_statement.append(statement)
            self._indentation += '  '
            self._output.append(out_str)
        else:
            self._indentation = self._indentation[:-2]
            out_str = self._indentation + '</' + self._curr_statement.pop() + '>\n'
            self._output.append(out_str) 

     # Checks if current token is a statement keyword.
    def check_statement(self):
        return  self._tokens[self._curr_token][1] == 'if'\
            or self._tokens[self._curr_token][1] == 'do'\
            or self._tokens[self._curr_token][1] == 'let'\
            or self._tokens[self._curr_token][1] == 'while'\
            or self._tokens[self._curr_token][1] == 'return'
    
    # Checks if the current token is part of a term.
    def check_term(self):
        return self._tokens[self._curr_token][0] in self.constants\
            or self._tokens[self._curr_token][1] in self.constants\
            or self._tokens[self._curr_token][1] in self.symbols_unary_operators\
            or self._tokens[self._curr_token][0] == 'identifier'\
            or self._tokens[self._curr_token][1] == '('
    
    # Compiles the class structure, including class variable declarations and methods within the class.
    # It generates XML tags for the class declaration, class variable declarations, and methods.
    # It iterates through class variable declarations and methods, calling corresponding compilation methods.
    # Finally, it generates closing tags for the class declaration.
    def compileClass(self):
        methods = ['constructor', 'function', 'method']
        classVars = ['static', 'field']

        self.generate_XMLnT(self._tokens[self._curr_token][1])
        self.generate_XMLT(self._tokens[self._curr_token])
        self.generate_XMLT(self._tokens[self._curr_token])
        self.generate_XMLT(self._tokens[self._curr_token])
        while self._tokens[self._curr_token][1] in classVars: 
            self.compileClassVarDec()
        while self._tokens[self._curr_token][1] in methods:
            self.compileSubroutine()
        self.generate_XMLT(self._tokens[self._curr_token])
        self.generate_XMLnT(self._tokens[0][1], start=0)

    # Compiles a class variable declaration.
    # It generates XML tags for the class variable declaration, including type, variable names, and separators.
    # It iterates through multiple variable declarations separated by commas, generating corresponding XML tags.
    # Finally, it generates a closing tag for the class variable declaration.
    def compileClassVarDec(self):
        self.generate_XMLnT('classVarDec')
        self.generate_XMLT(self._tokens[self._curr_token])
        self.generate_XMLT(self._tokens[self._curr_token])
        self.generate_XMLT(self._tokens[self._curr_token])
        while self._tokens[self._curr_token][1] == ',':
            self.generate_XMLT(self._tokens[self._curr_token])
            self.generate_XMLT(self._tokens[self._curr_token])
        self.generate_XMLT(self._tokens[self._curr_token])
        self.generate_XMLnT('classVarDec', start=0)

    
    # Compiles a subroutine declaration, generating XML tags for its return type, name, parameters, and body.  
    # It invokes compileParameterList for parameter handling and compileSubroutineBody for body handling.
    def compileSubroutine(self):
        self.generate_XMLnT('subroutineDec')
        self.generate_XMLT(self._tokens[self._curr_token])
        self.generate_XMLT(self._tokens[self._curr_token])
        self.generate_XMLT(self._tokens[self._curr_token])
        self.generate_XMLT(self._tokens[self._curr_token])
        self.compileParameterList()
        self.generate_XMLT(self._tokens[self._curr_token])
        self.compileSubroutineBody()
        self.generate_XMLnT('subroutineDec', start=0)

    # Compiles a parameter list, generating XML tags for each parameter until encountering a closing parenthesis.
    # It generates an opening and closing tag for the parameter list.
    def compileParameterList(self):
        self.generate_XMLnT('parameterList')
        while self._tokens[self._curr_token][1] != ')':
            self.generate_XMLT(self._tokens[self._curr_token])
        self.generate_XMLnT('parameterList', start=0)

    
    # Compiles the body of a subroutine, generating XML tags for the subroutine body.
    # It handles variable declarations and statements within the subroutine.
    # It calls compileVarDec for variable declaration handling and compileStatements for statement handling.
    # Finally, it generates opening and closing tags for the subroutine body.
    def compileSubroutineBody(self):
        self.generate_XMLnT('subroutineBody')
        self.generate_XMLT(self._tokens[self._curr_token])
        while self._tokens[self._curr_token][1] == 'var':
            self.compileVarDec()
        self.compileStatements() 
        self.generate_XMLT(self._tokens[self._curr_token])
        self.generate_XMLnT('subroutineBody', start=0)
    
    # Compiles a variable declaration within a subroutine, generating XML tags for the declaration.
    # It handles the type and names of variables until encountering a semicolon.
    # Finally, it generates opening and closing tags for the variable declaration.
    def compileVarDec(self):
        self.generate_XMLnT('varDec')
        self.generate_XMLT(self._tokens[self._curr_token])
        while self._tokens[self._curr_token][1] != ';':
            self.generate_XMLT(self._tokens[self._curr_token])
        self.generate_XMLT(self._tokens[self._curr_token])
        self.generate_XMLnT('varDec', start=0)
    
    # Compiles a series of statements, generating XML tags for each statement.
    # It iterates through the tokens, calling specific methods for each type of statement.
    # It calls compileIf, compileDo, compileLet, compileWhile, or compileReturn based on the current token.
    # Finally, it generates opening and closing tags for the statements block.
    def compileStatements(self):
        self.generate_XMLnT('statements')
        while self.check_statement():
            if self._tokens[self._curr_token][1] == 'if':
                self.compileIf()
            elif self._tokens[self._curr_token][1] == 'do':
                self.compileDo()
            elif self._tokens[self._curr_token][1] == 'let':
                self.compileLet()
            elif self._tokens[self._curr_token][1] == 'while':
                self.compileWhile()
            elif self._tokens[self._curr_token][1] == 'return':
                self.compileReturn()
        self.generate_XMLnT('statements', start=0)

    # Compiles a subroutine call expression, generating XML tags for the call and its arguments.
    # It handles cases where the call is preceded by an object or class name.
    # It generates tags for the object/class name, method name, and argument list.
    def compileSubroutineCall(self):
        self.generate_XMLT(self._tokens[self._curr_token])
        if self._tokens[self._curr_token][1] == '.':
            self.generate_XMLT(self._tokens[self._curr_token])
            self.generate_XMLT(self._tokens[self._curr_token])
        self.generate_XMLT(self._tokens[self._curr_token])
        self.compileExpressionList() 
        self.generate_XMLT(self._tokens[self._curr_token])
    
    # Compiles a 'do' statement, generating XML tags for the statement and its subroutine call.
    # It generates tags for the 'do' keyword, subroutine call, and closing semicolon.
    # Finally, it generates opening and closing tags for the 'do' statement block.
    def compileDo(self):
        self.generate_XMLnT('doStatement')
        self.generate_XMLT(self._tokens[self._curr_token])
        self.compileSubroutineCall()
        self.generate_XMLT(self._tokens[self._curr_token])
        self.generate_XMLnT('doStatement', start=0)
    
    # Compiles a 'let' statement, generating XML tags for the statement and its assignment.
    # It generates tags for the 'let' keyword, variable name, and expression.
    # If the assignment includes an array index, it generates tags for the array index expression.
    # Finally, it generates opening and closing tags for the 'let' statement block.
    def compileLet(self):
        self.generate_XMLnT('letStatement')
        self.generate_XMLT(self._tokens[self._curr_token])
        self.generate_XMLT(self._tokens[self._curr_token])
        if self._tokens[self._curr_token][1] == '[':
            self.generate_XMLT(self._tokens[self._curr_token])
            self.compileExpression()
            self.generate_XMLT(self._tokens[self._curr_token])
        self.generate_XMLT(self._tokens[self._curr_token])
        self.compileExpression()
        self.generate_XMLT(self._tokens[self._curr_token])
        self.generate_XMLnT('letStatement', start=0)
    
    # Compiles an 'if' statement, generating XML tags for the statement, its condition, and its body.
    # It generates tags for the 'if' keyword, condition expression, and opening and closing braces for the body.
    # If an 'else' clause is present, it generates tags for the 'else' keyword and the corresponding body.
    # Finally, it generates opening and closing tags for the 'if' statement block.
    def compileIf(self):
        self.generate_XMLnT('ifStatement')
        self.generate_XMLT(self._tokens[self._curr_token])
        self.generate_XMLT(self._tokens[self._curr_token])
        self.compileExpression()
        self.generate_XMLT(self._tokens[self._curr_token])
        self.generate_XMLT(self._tokens[self._curr_token])
        self.compileStatements()
        self.generate_XMLT(self._tokens[self._curr_token])
        if self._tokens[self._curr_token][1] == 'else':
            self.generate_XMLT(self._tokens[self._curr_token])
            self.generate_XMLT(self._tokens[self._curr_token])
            self.compileStatements()
            self.generate_XMLT(self._tokens[self._curr_token])
        self.generate_XMLnT('ifStatement', start=0)
    
    # Compiles a 'while' statement, generating XML tags for the statement, its condition, and its body.
    # It generates tags for the 'while' keyword, condition expression, and opening and closing braces for the body.
    # Finally, it generates opening and closing tags for the 'while' statement block.
    def compileWhile(self):
        self.generate_XMLnT('whileStatement')
        self.generate_XMLT(self._tokens[self._curr_token])
        self.generate_XMLT(self._tokens[self._curr_token])
        self.compileExpression()
        self.generate_XMLT(self._tokens[self._curr_token])
        self.generate_XMLT(self._tokens[self._curr_token])
        self.compileStatements()
        self.generate_XMLT(self._tokens[self._curr_token])
        self.generate_XMLnT('whileStatement', start=0)
    
    # Compiles a 'return' statement, generating XML tags for the statement and its returned expression.
    # It generates tags for the 'return' keyword and the expression to be returned.
    # If there is no expression to return, it simply generates the 'return' keyword tag.
    # Finally, it generates opening and closing tags for the 'return' statement block.
    def compileReturn(self):
        self.generate_XMLnT('returnStatement')
        self.generate_XMLT(self._tokens[self._curr_token])
        while self.check_term():
            self.compileExpression()
        self.generate_XMLT(self._tokens[self._curr_token])
        self.generate_XMLnT('returnStatement', start=0)
    
    # Compiles an expression, generating XML tags for the expression and its terms.
    # It generates opening and closing tags for the expression.
    # It iterates through terms and binary operators, generating tags for each.
    def compileExpression(self):
        self.generate_XMLnT('expression')
        self.compileTerm()
        while self._tokens[self._curr_token][1] in self.symbols_binary_operators:
            self.generate_XMLT(self._tokens[self._curr_token])
            self.compileTerm()
        self.generate_XMLnT('expression', start=0)

    # Compiles a term, generating XML tags for different types of terms.
    # It generates opening and closing tags for the term.
    # It handles constants, identifiers, expressions within parentheses, subroutine calls, and unary operators.
    def compileTerm(self):
        self.generate_XMLnT('term')
        if self._tokens[self._curr_token][0] in self.constants\
            or self._tokens[self._curr_token][1] in self.constants:
            self.generate_XMLT(self._tokens[self._curr_token])
        elif self._tokens[self._curr_token][0] == 'identifier':
            self.generate_XMLT(self._tokens[self._curr_token])
            if self._tokens[self._curr_token][1] == '[':
                self.generate_XMLT(self._tokens[self._curr_token])
                self.compileExpression()
                self.generate_XMLT(self._tokens[self._curr_token])
            elif self._tokens[self._curr_token][1] == '(':
                self.generate_XMLT(self._tokens[self._curr_token])
                self.compileExpressionList()
                self.generate_XMLT(self._tokens[self._curr_token])
            elif self._tokens[self._curr_token][1] == '.':
                self.generate_XMLT(self._tokens[self._curr_token])
                self.generate_XMLT(self._tokens[self._curr_token])
                self.generate_XMLT(self._tokens[self._curr_token])
                self.compileExpressionList()
                self.generate_XMLT(self._tokens[self._curr_token])
        elif self._tokens[self._curr_token][1] in self.symbols_unary_operators:
            self.generate_XMLT(self._tokens[self._curr_token])
            self.compileTerm()
        elif self._tokens[self._curr_token][1] == '(':
            self.generate_XMLT(self._tokens[self._curr_token])
            self.compileExpression()
            self.generate_XMLT(self._tokens[self._curr_token])
        self.generate_XMLnT('term', start=0)
    
    # Compiles an expression list.
    # Generates XML tags for the expression list.
    # Calls compileExpression to handle the first expression if present.
    # Loops through and generates tags for subsequent expressions separated by commas.
    # Finally, generates opening and closing tags for the expression list. 
    def compileExpressionList(self):
        self.generate_XMLnT('expressionList')
        if self.check_term():
            self.compileExpression()
        while self._tokens[self._curr_token][1] == ',':
            self.generate_XMLT(self._tokens[self._curr_token])
            self.compileExpression()
        self.generate_XMLnT('expressionList', start=0)
    

    @property 
    def getInd(self):
        return self._curr_token
    
    @property
    def getListSize(self):
        return len(self._tokens)
    
    @property
    def getOutput(self):
        return self._output

# Parses the input Jack file into a list of tokens.
# Processes the file line by line, stripping whitespace and handling comments.
# Uses regular expressions to identify and tokenize keywords, symbols, integers, strings, and identifiers.
# Converts the tokens into a list of tuples representing token type and value.
# Returns the list of tokens.
def ParserTokenizer(filePath):
    fileLines = []
    processingLines = []
    tokens = []
    keywords = ['class', 'constructor', 'function' , 'method', 'field', 'static', 'var', 'int', 'char', 'boolean',
                'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']
    symbols = ['{', '}', '[', ']', '(', ')', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']
    
    keywordsRegex = '(?!\\w)|'.join(keywords) + '(?!\\w)'
    integerRegex = r'\d+'
    stringsRegex = r'"[^"\n]*"'
    symbolsRegex = '[' + re.escape('|'.join(symbols)) + ']'
    identifiersRegex = r'[\w]+'

    TokenPattern = re.compile(keywordsRegex + '|' + symbolsRegex + '|' + integerRegex + '|' + stringsRegex + '|' + identifiersRegex)

    with open(filePath, 'r') as f: 
        fileLines = f.readlines()
    
    for i, line in enumerate(fileLines):
        fileLines[i] = line.strip(' \n\r')

    onComment = False
    for line in fileLines:
        if onComment:
            if line.endswith("*/"): 
                onComment = False
            continue
        if line.startswith("/*") and not line.endswith("*/"):
            onComment = True
            continue
        elif line.startswith("/*") and  line.endswith("*/"):
            continue
        elif line.startswith("//"):
            continue
        else:
            if "//" in line:
                processingLines.append(line.split("//")[0])
            else:
                processingLines.append(line) 

    for line in processingLines:
        tempTokens = TokenPattern.findall(line)
        for token in tempTokens:
            tokens.append(token)

    for i, token in enumerate(tokens):
        if re.match(keywordsRegex, token):
            tokens[i] = ("keyword", token.strip())
        elif re.match(integerRegex, token):
            tokens[i] = ("integerConstant", token.strip())
        elif re.match(stringsRegex, token):
            tokens[i] = ("stringConstant", token.strip('"'))
        elif re.match(symbolsRegex, token):
            tokens[i] = ("symbol", token.strip())
        else:
            tokens[i] = ("identifier", token.strip())

    return tokens

inputPath = sys.argv[1] 
outputPath = None
files = []
fileNames = []
filesList = []

if inputPath.endswith('.jack'):
    ht = os.path.split(inputPath) 
    file_name = ht[1].split('.')[0]
    filesList = [(inputPath, file_name)]
    outputPath = ht[0]
else:
    filesInPath = os.listdir(inputPath)
    for file in filesInPath:
        if file.endswith(".jack"):
            files.append((os.path.join(inputPath, file)))
            fileNames.append(file.split('.')[0])
    filesList = zip(files, fileNames)
    outputPath = inputPath

# Updates the special characters in the given list of strings to their corresponding XML entities.
# Replaces characters '<', '>', '&', and '"' with '&lt;', '&gt;', '&amp;', and '&quot;' respectively.
# Returns the list of strings with updated characters.
def updateCodes(fileLines):
    t = fileLines
    for i,line in enumerate(t):
        if line.find(' < ') != -1:
            t[i] = line.replace(' < ',' &lt; ')
        elif line.find(' > ') != -1:
            t[i] = line.replace(' > ',' &gt; ')
        elif line.find(' & ') != -1:
            t[i] = line.replace(' & ',' &amp; ')
        elif line.find(' " ') != -1:
            t[i] = line.replace(' " ',' &quot;')
    return t

# Determines input and output paths based on the provided input.
# Processes each Jack file found in the input directory.
# Parses each Jack file, compiles it using the Compiler class, and writes the resulting XML code to the output directory.
if __name__ == "__main__":

    tokensList = []
    processingLines = []
    outputList = []

    for file in filesList:
        tokensList = ParserTokenizer(file[0]) 
        compilerOb = Compiler(tokensList)
        processingLines = compilerOb.getOutput 
        outputList = updateCodes(processingLines)
        with open(os.path.join(outputPath, file[1] + '.xml'), 'w') as f:
            f.writelines(outputList)
        
        tokensList.clear()
        processingLines.clear()
        outputList.clear()
