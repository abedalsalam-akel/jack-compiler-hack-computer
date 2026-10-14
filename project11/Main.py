import sys

import os
import re
from collections import namedtuple

INDENT = 2
binary_op_actions = {'+': 'add',
                     '-': 'sub',
                     '*': 'call Math.multiply 2',
                     '/': 'call Math.divide 2',
                     '&': 'and',
                     '|': 'or',
                     '<': 'lt',
                     '>': 'gt',
                     '=': 'eq'}

label_count = 0

class CompilationEngine:
    '''A compilation engine for the Jack programming language'''

    def __init__(self, tokenizer, ostream):
        '''Initialize the compilation engine
        @tokenizer the tokenizer from the input code file
        @ostream the output stream to write the code to'''
        self.tokenizer = tokenizer
        self.vm_writer = VMWriter(ostream)

    @staticmethod
    def get_label():
        '''Return a label for use'''
        global label_count

        label = 'L{}'.format(label_count)
        label_count += 1

        return label

    def compile_class(self):
        '''Compile a class block'''
        self.tokenizer.advance() 

        
        class_name = self.tokenizer.advance().value
        jack_class = JackClass(class_name)

        self.tokenizer.advance() 

        self.compile_class_vars(jack_class)
        self.compile_class_subroutines(jack_class)

        self.tokenizer.advance() 

    def compile_class_vars(self, jack_class):
        '''Compile the class variable declarations'''

        token = self.tokenizer.current_token()
        while token is not None and token.type == 'keyword' and \
                token.value in ['static', 'field']:
            # Advance here, to avoid eating the token in the condition above
            # and losing the token when needed afterwards
            self.tokenizer.advance()

            is_static = token.value == 'static'

            var_type = self.tokenizer.advance().value

            still_vars = True
            while still_vars:
                var_name = self.tokenizer.advance().value

                if is_static:
                    jack_class.add_static(var_name, var_type)
                else:
                    jack_class.add_field(var_name, var_type)

                token = self.tokenizer.advance()
                still_vars = token == ('symbol', ',')

            token = self.tokenizer.current_token()

    def compile_class_subroutines(self, jack_class):
        '''Compile the class subroutines'''

        token = self.tokenizer.current_token()
        while token is not None and token.type == 'keyword' \
                and token.value in ['constructor', 'function', 'method']:

            subroutine_type = self.tokenizer.advance().value
            return_type = self.tokenizer.advance().value
            name = self.tokenizer.advance().value

            jack_subroutine = JackSubroutine(
                name, subroutine_type, return_type, jack_class
            )

            self.tokenizer.advance() 

            self.compile_parameter_list(jack_subroutine)

            self.tokenizer.advance() 

            self.compile_subroutine_body(jack_subroutine)

            # load the next token to check
            token = self.tokenizer.current_token()

    def compile_parameter_list(self, jack_subroutine):
        '''Compile a parameter list for a subroutine'''

        token = self.tokenizer.current_token()
        # Check if the next token is a valid variable type
        still_vars = token is not None and token.type in ['keyword', 'identifier']
        while still_vars:
            # param type
            token = self.tokenizer.advance() # Don't advance to avoid eating
            param_type = token.value
            # param name
            param_name = self.tokenizer.advance().value

            jack_subroutine.add_arg(param_name, param_type)

            token = self.tokenizer.current_token()
            # If there are still vars
            if token == ('symbol', ','):
                self.tokenizer.advance() 
                token = self.tokenizer.current_token()
                still_vars = token is not None and token.type in ['keyword', 'identifier']
            else:
                still_vars = False


    def compile_subroutine_body(self, jack_subroutine):
        '''Compile the subroutine body'''

        self.tokenizer.advance() 

        self.compile_subroutine_vars(jack_subroutine)

        self.vm_writer.write_function(jack_subroutine)

        if jack_subroutine.subroutine_type == 'constructor':
            field_count = jack_subroutine.jack_class.field_symbols
            self.vm_writer.write_push('constant', field_count)
            self.vm_writer.write_call('Memory', 'alloc', 1)
            self.vm_writer.write_pop('pointer', 0)
        elif jack_subroutine.subroutine_type == 'method':
            self.vm_writer.write_push('argument', 0)
            self.vm_writer.write_pop('pointer', 0)

        self.compile_statements(jack_subroutine)

        self.tokenizer.advance() 

    def compile_subroutine_vars(self, jack_subroutine):
        '''Compile the variable declerations of a subroutine'''

        token = self.tokenizer.current_token()
        while token is not None and token == ('keyword', 'var'):
            self.tokenizer.advance()
            var_type = self.tokenizer.advance().value
            var_name = self.tokenizer.advance().value

            jack_subroutine.add_var(var_name, var_type)

            # repeat as long as there are parameters, o.w eats the semi-colon
            while self.tokenizer.advance().value == ',':
                var_name = self.tokenizer.advance().value
                jack_subroutine.add_var(var_name, var_type)

            token = self.tokenizer.current_token()

    def compile_statements(self, jack_subroutine):
        '''Compile subroutine statements'''

        check_statements = True
        while check_statements:
            token = self.tokenizer.current_token()

            if token == ('keyword', 'if'):
                self.compile_statement_if(jack_subroutine)
            elif token == ('keyword', 'while'):
                self.compile_statement_while(jack_subroutine)
            elif token == ('keyword', 'let'):
                self.compile_statement_let(jack_subroutine)
            elif token == ('keyword', 'do'):
                self.compile_statement_do(jack_subroutine)
            elif token == ('keyword', 'return'):
                self.compile_statement_return(jack_subroutine)
            else:
                check_statements = False

    def compile_statement_if(self, jack_subroutine):
        '''Compile the if statement'''
        self.tokenizer.advance() 
        self.tokenizer.advance() 

        self.compile_expression(jack_subroutine)

        self.tokenizer.advance() 
        self.tokenizer.advance() 

        false_label = CompilationEngine.get_label()
        end_label = CompilationEngine.get_label()

        self.vm_writer.write_if(false_label)

        self.compile_statements(jack_subroutine)

        self.vm_writer.write_goto(end_label)
        self.vm_writer.write_label(false_label)

        self.tokenizer.advance() 

        token = self.tokenizer.current_token()
        if token == ('keyword', 'else'):
            self.tokenizer.advance() 
            self.tokenizer.advance() 
            self.compile_statements(jack_subroutine)
            self.tokenizer.advance() 

        self.vm_writer.write_label(end_label)

    def compile_statement_while(self, jack_subroutine):
        '''Compile the while statment'''
        self.tokenizer.advance() 
        self.tokenizer.advance() 

        while_label = CompilationEngine.get_label()
        false_label = CompilationEngine.get_label()

        self.vm_writer.write_label(while_label)
        self.compile_expression(jack_subroutine)

        self.tokenizer.advance() 
        self.tokenizer.advance() 

        self.vm_writer.write_if(false_label)

        # Compile inner statements
        self.compile_statements(jack_subroutine)

        self.vm_writer.write_goto(while_label)
        self.vm_writer.write_label(false_label)
        self.tokenizer.advance() 

    def compile_statement_let(self, jack_subroutine):
        '''Compile the let statment'''

        self.tokenizer.advance() 
        var_name = self.tokenizer.advance().value 
        jack_symbol = jack_subroutine.get_symbol(var_name)

        is_array = self.tokenizer.current_token().value == '['
        if is_array:
            self.tokenizer.advance() 
            self.compile_expression(jack_subroutine) # Index
            self.tokenizer.advance() 
            self.tokenizer.advance() 
            self.vm_writer.write_push_symbol(jack_symbol)
            self.vm_writer.write('add')
            self.compile_expression(jack_subroutine) # Expression to assign
            self.vm_writer.write_pop('temp', 0) # Store assigned value in temp
            self.vm_writer.write_pop('pointer', 1) # Restore destination
            self.vm_writer.write_push('temp', 0) # Restore assigned value
            self.vm_writer.write_pop('that', 0) # Store in target
        else:
            self.tokenizer.advance() 
            self.compile_expression(jack_subroutine) # Expression to assign
            self.vm_writer.write_pop_symbol(jack_symbol)

        self.tokenizer.advance() 

    def compile_statement_do(self, jack_subroutine):
        '''Compile the do statment'''
        self.tokenizer.advance() 

        self.compile_term(jack_subroutine) # Do options are a subset of terms
        self.vm_writer.write_pop('temp', 0) # Pop to avoid filling the stack with garbage

        self.tokenizer.advance() 

    def compile_statement_return(self, jack_subroutine):
        '''Compile the return statment'''
        self.tokenizer.advance() 
        token = self.tokenizer.current_token()
        if token != ('symbol', ';'):
            self.compile_expression(jack_subroutine)
        else:
            self.vm_writer.write_int(0)

        self.vm_writer.write_return()
        self.tokenizer.advance() 

    def compile_expression_list(self, jack_subroutine):
        '''Compile a subroutine call expression_list'''
        # Handle expression list, so long as there are expressions
        count = 0 # Count expressions
        token = self.tokenizer.current_token()
        while token != ('symbol', ')'):

            if token == ('symbol', ','):
                self.tokenizer.advance()

            count += 1
            self.compile_expression(jack_subroutine)
            token = self.tokenizer.current_token()

        return count

    def compile_expression(self, jack_subroutine):
        '''Compile an expression'''
        self.compile_term(jack_subroutine)

        token = self.tokenizer.current_token()
        while token.value in '+-*/&|<>=':
            binary_op = self.tokenizer.advance().value

            self.compile_term(jack_subroutine)
            self.vm_writer.write(binary_op_actions[binary_op])

            token = self.tokenizer.current_token()

    def compile_term(self, jack_subroutine):
        '''Compile a term as part of an expression'''

        token = self.tokenizer.advance()
        # In case of unary operator, compile the term after the operator
        if token.value in ['-', '~']:
            self.compile_term(jack_subroutine)
            if token.value == '-':
                self.vm_writer.write('neg')
            elif token.value == '~':
                self.vm_writer.write('not')
        # In case of opening parenthesis for an expression
        elif token.value == '(':
            self.compile_expression(jack_subroutine)
            self.tokenizer.advance() # )
        elif token.type == 'integerConstant':
            self.vm_writer.write_int(token.value)
        elif token.type == 'stringConstant':
            self.vm_writer.write_string(token.value)
        elif token.type == 'keyword':
            if token.value == 'this':
                self.vm_writer.write_push('pointer', 0)
            else:
                self.vm_writer.write_int(0) 
                if token.value == 'true':
                    self.vm_writer.write('not')

        # In case of a function call or variable name
        elif token.type == 'identifier':
            # Save token value as symbol and function in case of both
            token_value = token.value
            token_var = jack_subroutine.get_symbol(token_value)

            token = self.tokenizer.current_token()
            if token.value == '[': 
                self.tokenizer.advance() 
                self.compile_expression(jack_subroutine)
                self.vm_writer.write_push_symbol(token_var)
                self.vm_writer.write('add')
                self.vm_writer.write_pop('pointer', 1)
                self.vm_writer.write_push('that', 0)
                self.tokenizer.advance() # ]
            else:
                # Default class for function calls is this class
                func_name = token_value
                func_class = jack_subroutine.jack_class.name
                # Used to mark whether to use the default call, a method one
                default_call = True
                arg_count = 0

                if token.value == '.':
                    default_call = False
                    self.tokenizer.advance() # .
                    # try to load the object of the method
                    func_obj = jack_subroutine.get_symbol(token_value)
                    func_name = self.tokenizer.advance().value # function name
                    # If this is an object, call as method
                    if func_obj:
                        func_class = token_var.type 
                        arg_count = 1 
                        self.vm_writer.write_push_symbol(token_var) 
                    else:
                        func_class = token_value
                    token = self.tokenizer.current_token()

                # If in-fact a function call
                if token.value == '(':
                    if default_call:
                        arg_count = 1
                        self.vm_writer.write_push('pointer', 0)

                    self.tokenizer.advance() # (
                    arg_count += self.compile_expression_list(jack_subroutine)
                    self.vm_writer.write_call(func_class, func_name, arg_count)
                    self.tokenizer.advance() # )
                elif token_var:
                    self.vm_writer.write_push_symbol(token_var)



JackSymbol = namedtuple('Symbol', ['kind', 'type', 'id'])

class JackClass:
    '''A Jack class representation for the Jack compiler'''

    def __init__(self, name):
        self.name = name
        self.symbols = dict()

        self.static_symbols = 0
        self.field_symbols = 0

    def add_field(self, name, var_type):
        '''Add a field symbol to the class'''
        self.symbols[name] = JackSymbol('field', var_type, self.field_symbols)
        self.field_symbols += 1

    def add_static(self, name, var_type):
        '''Add a static symbol to the class'''
        self.symbols[name] = JackSymbol('static', var_type, self.static_symbols)
        self.static_symbols += 1

    def get_symbol(self, name):
        '''Get a symbol from the class'''
        return self.symbols.get(name)

class JackSubroutine:
    '''A Jack subroutine representation for the Jack compiler'''

    def __init__(self, name, subroutine_type, return_type, jack_class):
        self.name = name
        self.jack_class = jack_class
        self.subroutine_type = subroutine_type
        self.return_type = return_type

        self.symbols = dict()
        self.arg_symbols = 0
        self.var_symbols = 0

        if subroutine_type == 'method':
            self.add_arg('this', self.jack_class.name)

    def add_arg(self, name, var_type):
        '''Add an arg symbol to the class'''
        self.symbols[name] = JackSymbol('arg', var_type, self.arg_symbols)
        self.arg_symbols += 1

    def add_var(self, name, var_type):
        '''Add a var symbol to the class'''
        self.symbols[name] = JackSymbol('var', var_type, self.var_symbols)
        self.var_symbols += 1

    def get_symbol(self, name):
        '''Get a symbol from within the scope of the subroutine'''
        symbol = self.symbols.get(name)
        if symbol is not None:
            return symbol

        return self.jack_class.get_symbol(name)




Token = namedtuple('Token',('type', 'value'))

class JackTokenizer:
    '''A tokenizer for the Jack programming language'''

    RE_INTEGER = r'\d+'
    RE_STRING = '"[^"]*"'
    RE_IDENTIFIER = r'[A-z_][A-z_\d]*'
    RE_SYMBOL = r'\{|\}|\(|\)|\[|\]|\.|,|;|\+|-|\*|/|&|\||\<|\>|=|~'
    RE_KEYWORD = '|'.join(keyword for keyword in
                          [
                              'class','method','constructor','function','field','static','var',
                              'int','char','boolean','void','true','false','null','this','let',
                              'do','if','else','while','return'
                          ])

    LEXICAL_TYPES = [
        (RE_KEYWORD, 'keyword'),
        (RE_SYMBOL, 'symbol'),
        (RE_INTEGER, 'integerConstant'),
        (RE_STRING, 'stringConstant'),
        (RE_IDENTIFIER, 'identifier')
    ]

    RE_SPLIT = '(' + '|'.join(expr for expr in [RE_SYMBOL,RE_STRING]) + r')|\s+'

    @staticmethod
    def remove_comments(file):
        '''Remove the comments from a given Jack file'''

        uncommented = re.sub('//.*?\n', '\n', file)
        uncommented = re.sub(r'/\*.*?\*/', '', uncommented, flags=re.DOTALL)
        return uncommented

    def __init__(self, file):
        '''Initialize the tokenizer for a given file, provided as utf-8 encoded
        python string'''
        self.code = JackTokenizer.remove_comments(file)
        self.tokens = self.tokenize()

    def tokenize(self):
        '''Tokenize the given input file without comments'''
        split_code = re.split(self.RE_SPLIT, self.code)
        tokens = []

        for lex in split_code:
            # Skip non-tokens
            if lex is None or re.match(r'^\s*$', lex):
                continue

            # Check all possible lexical types, if
            for expr, lex_type in self.LEXICAL_TYPES:
                if re.match(expr, lex):
                    tokens.append(Token(lex_type, lex))
                    break
            else:
                print('Error: unknown token', lex)
                sys.exit(1)

        return tokens

    def current_token(self):
        '''Return the current token, if not existent return None'''
        return self.tokens[0] if self.tokens else None

    def advance(self):
        '''Advance to the next token, return current token'''
        return self.tokens.pop(0) if self.tokens else None


kind_to_segment = {'static': 'static',
                   'field': 'this',
                   'arg': 'argument',
                   'var': 'local'}

class VMWriter:
    '''A jack to VM writer, used by the compiler to output the code matching
    to the analyzed code'''

    def __init__(self, ostream):
        '''Initialize the VMWriter with a given output stream'''
        self.ostream = ostream
        self.label_count = 0

    def write_if(self, label):
        '''Write an if-goto used in while/if.
        used to jump to label if the condition *doesn't* hold'''
        self.ostream.write('not\n') 
        self.ostream.write('if-goto {}\n'.format(label))

    def write_goto(self, label):
        '''Write a goto for the VM'''
        self.ostream.write('goto {}\n'.format(label))

    def write_label(self, label):
        '''Write a label in VM'''
        self.ostream.write('label {}\n'.format(label))

    def write_function(self, jack_subroutine):
        '''Write a function header for a Jack subroutine'''
        class_name = jack_subroutine.jack_class.name
        name = jack_subroutine.name
        local_vars = jack_subroutine.var_symbols
        subroutine_type = jack_subroutine.subroutine_type

        self.ostream.write('function {}.{} {}\n'.format(class_name, name, local_vars))

    def write_return(self):
        '''Write the return statement'''
        self.ostream.write('return\n')

    def write_call(self, class_name, func_name, arg_count):
        '''Write a call to a function with n-args'''
        self.ostream.write('call {0}.{1} {2}\n'.format(
            class_name, func_name, arg_count
        ))

    def write_pop_symbol(self, jack_symbol):
        '''Pop the value in the top of the stack to the supplied symbol'''
        kind = jack_symbol.kind
        offset = jack_symbol.id 

        segment = kind_to_segment[kind]
        self.write_pop(segment, offset)

    def write_push_symbol(self, jack_symbol):
        '''Push the value from the symbol to the stack'''
        kind = jack_symbol.kind
        offset = jack_symbol.id 

        segment = kind_to_segment[kind]
        self.write_push(segment, offset)

    def write_pop(self, segment, offset):
        '''Pop the value in the top of the stack to segment:offset'''
        self.ostream.write('pop {0} {1}\n'.format(segment, offset))

    def write_push(self, segment, offset):
        '''Push the value to the stack from segment:offset'''
        self.ostream.write('push {0} {1}\n'.format(segment, offset))

    def write(self, action):
        '''Write something'''
        self.ostream.write('{}\n'.format(action))

    def write_int(self, n):
        '''Write an int'''
        self.write_push('constant', n)

    def write_string(self, s):
        '''Allocates a new string, and appends all the chars one-by-one'''
        s = s[1:-1]
        self.write_int(len(s))
        self.write_call('String', 'new', 1)
        for c in s:
            self.write_int(ord(c))
            self.write_call('String','appendChar', 2)




def compile_file(file_path):
    '''Compile a file by its path, save the result to a file
    with the same name and a vm suffix'''

    with open(file_path, 'r') as ifile:
        file_name = os.path.basename(file_path)
        file_path_no_ext, _ = os.path.splitext(file_path)
        file_name_no_ext, _ = os.path.splitext(file_name)

        ofile_path = file_path_no_ext+'.vm'
        with open(ofile_path, 'w') as ofile:
            tokenizer = JackTokenizer(ifile.read())
            compiler = CompilationEngine(tokenizer, ofile)
            compiler.compile_class()

def compile_dir(dir_path):
    '''Compile all Jack files in a directory'''
    for file in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file)
        _, file_ext = os.path.splitext(file_path)
        if os.path.isfile(file_path) and file_ext.lower()=='.jack':
            compile_file(file_path)

def main():
    """The main program, loading the file/files and calling the translator"""
    if len(sys.argv) < 2:
        print('usage: JackCompiler (file|dir)'.format(sys.argv[0]))
        sys.exit(1)

    input_path = sys.argv[1]

    if os.path.isdir(input_path):
        compile_dir(input_path)
    elif os.path.isfile(input_path):
        compile_file(input_path)
    else:
        print("Invalid file/directory, compilation failed")
        sys.exit(1)


if __name__=="__main__":
    main()
