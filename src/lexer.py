from .bcc_token import Token, TokenType

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[0] if text else None
        self.tokens = []
        self.line = 1      # 从1开始计数
        self.column = 0    # 当前列号，从0开始

    def advance(self):
        """移动到下一个字符"""
        if self.current_char == '\n':
            self.column = 0
        else:
            self.column += 1
        
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        """跳过所有空白字符"""
        while self.current_char and self.current_char.isspace():
            if self.current_char == '\n':  # 在跳过空白时也要处理换行
                self.line += 1  # 只在这里增加行号
                self.column = 1
            else:
                self.column += 1
            self.advance()

    def number(self):
        result = ''
        while self.current_char and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def identifier(self):
        result = ''
        while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
        
        # 检查是否是关键字
        keywords = {
            'print': TokenType.PRINT,
            'printnln': TokenType.PRINTNLN,
            'if': TokenType.IF,
            'for': TokenType.FOR,
            'while': TokenType.WHILE,
            'def': TokenType.DEF,
            'public': TokenType.PUBLIC,
            'private': TokenType.PRIVATE,
            'return': TokenType.RETURN,
            'nsreturn': TokenType.NSRETURN,
            'expr': TokenType.EXPR,
            'class': TokenType.CLASS,
            'import': TokenType.IMPORT,
            'from': TokenType.FROM,
            'as': TokenType.AS
        }
        
        return Token(keywords.get(result, TokenType.IDENTIFIER), result)

    def string(self):
        """处理字符串字面量"""
        result = ''
        self.advance()  # 跳过开始的引号
        
        while self.current_char and self.current_char != '"':
            result += self.current_char
            self.advance()
        
        if not self.current_char:
            raise Exception("未闭合的字符串")
        
        self.advance()  # 跳过结束的引号
        return result

    def tokenize(self):
        """将源代码转换为token列表"""
        tokens = []
        
        while self.current_char is not None:
            # 跳过空白字符
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            # 跳过注释
            if self.current_char == '/' and self.peek() == '/':
                # 跳过整行
                while self.current_char and self.current_char != '\n':
                    self.advance()
                if self.current_char == '\n':
                    self.advance()
                continue
            
            # 处理数字
            if self.current_char.isdigit():
                tokens.append(Token(TokenType.NUMBER, self.number(), self.line, self.column))
                continue
            
            # 处理标识符和关键字
            if self.current_char.isalpha() or self.current_char == '_':
                token = self.identifier()
                token.line = self.line
                token.column = self.column
                tokens.append(token)
                continue
            
            # 处理字符串
            if self.current_char == '"':
                value = self.string()
                tokens.append(Token(TokenType.STRING, value, self.line, self.column))
                continue
            
            # 处理所有已知的单字符标记
            char_to_token = {
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.MULTIPLY,
                '/': TokenType.DIVIDE,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
                '[': TokenType.LBRACKET,
                ']': TokenType.RBRACKET,
                ',': TokenType.COMMA,
                ';': TokenType.SEMICOLON,
                '.': TokenType.DOT,
                ':': TokenType.COLON,
            }
            
            if self.current_char in char_to_token:
                tokens.append(Token(char_to_token[self.current_char], 
                                  self.current_char, 
                                  self.line, 
                                  self.column))
                self.advance()
                continue
            
            # 处理双字符运算符
            if self.current_char == '=':
                if self.peek() == '=':
                    tokens.append(Token(TokenType.EQ, '==', self.line, self.column))
                    self.advance()
                    self.advance()
                else:
                    tokens.append(Token(TokenType.EQUALS, '=', self.line, self.column))
                    self.advance()
                continue
            
            if self.current_char == '<':
                if self.peek() == '=':
                    tokens.append(Token(TokenType.LE, '<=', self.line, self.column))
                    self.advance()
                    self.advance()
                else:
                    tokens.append(Token(TokenType.LT, '<', self.line, self.column))
                    self.advance()
                continue
            
            if self.current_char == '>':
                if self.peek() == '=':
                    tokens.append(Token(TokenType.GE, '>=', self.line, self.column))
                    self.advance()
                    self.advance()
                else:
                    tokens.append(Token(TokenType.GT, '>', self.line, self.column))
                    self.advance()
                continue
            
            # 如果遇到未知字符，报错并跳过
            print(f"警告: 跳过未知字符 '{self.current_char}' 在第 {self.line+1} 行，第 {self.column+1} 列")
            self.advance()
            
        tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return tokens

    def peek(self):
        """查看下一个字符但不移动指针"""
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        return self.text[peek_pos]