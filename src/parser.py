from .bcc_token import TokenType

class ASTNode:
    """抽象语法树的基类"""
    def __str__(self):
        return self.__class__.__name__

class NumberNode(ASTNode):
    """数字节点"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"Number({self.value})"

class BinOpNode(ASTNode):
    """二元运算节点"""
    def __init__(self, left, op, right):
        self.left = left    # 左操作数
        self.op = op        # 运算符
        self.right = right  # 右操作数

    def __str__(self):
        return f"BinOp({self.left}, {self.op.type}, {self.right})"

class PrintNode(ASTNode):
    """打印节点"""
    def __init__(self, expr):
        self.expr = expr    # 要打印的表达式

    def __str__(self):
        return f"Print({self.expr})"

class VariableNode(ASTNode):
    """变量节点"""
    def __init__(self, name):
        self.name = name    # 变量名

    def __str__(self):
        return f"Var({self.name})"

class AssignNode(ASTNode):
    """赋值节点"""
    def __init__(self, name, value):
        self.name = name    # 变量名
        self.value = value  # 要赋的值

    def __str__(self):
        return f"Assign({self.name}, {self.value})"

class PrintlnNode(ASTNode):
    """不换行打印节点"""
    def __init__(self, expr):
        self.expr = expr    # 要打印的表达式

    def __str__(self):
        return f"Println({self.expr})"

class StringNode(ASTNode):
    """字符串节点"""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"String('{self.value}')"

class IfNode(ASTNode):
    """if语句节点"""
    def __init__(self, condition, body):
        self.condition = condition  # 条件表达式
        self.body = body           # if体内的语句列表

    def __str__(self):
        return f"If({self.condition}, {self.body})"

class ForNode(ASTNode):
    """for循环节点"""
    def __init__(self, init, condition, update, body):
        self.init = init           # 初始化语句
        self.condition = condition # 条件表达式
        self.update = update       # 更新语句
        self.body = body          # 循环体语句列表

    def __str__(self):
        return f"For({self.init}, {self.condition}, {self.update}, {self.body})"

class WhileNode(ASTNode):
    """while循环节点"""
    def __init__(self, condition, body):
        self.condition = condition  # 条件表达式
        self.body = body           # 循环体语句列表

    def __str__(self):
        return f"While({self.condition}, {self.body})"

class ParserError(Exception):
    """解析错误，包含错误发生时的Token信息"""
    def __init__(self, message, token):
        self.token = token
        super().__init__(message)

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = tokens[0] if tokens else None
        
    def peek_next_token(self, offset=1):
        """查看后面的token但不移动指针
        Args:
            offset: 向前看几个token，默认为1
        Returns:
            Token 或 None
        """
        peek_pos = self.pos + offset
        if peek_pos < len(self.tokens):
            return self.tokens[peek_pos]
        return None
        
    def advance(self):
        """移动到下一个token"""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def parse(self):
        """解析程序入口"""
        statements = []
        while self.current_token and self.current_token.type != TokenType.EOF:
            try:
                stmt = self.statement()
                if stmt:  # 忽略None返回
                    statements.append(stmt)
            except ParserError as e:
                # 重新抛出错误，保持原始行号
                raise ParserError(str(e), e.token)
            except Exception as e:
                # 将普通异常转换为ParserError
                raise ParserError(str(e), self.current_token)
        return statements

    def statement(self):
        """解析单个语句"""
        if not self.current_token:
            raise Exception("意外的文件结束")
        
        token = self.current_token
        
        # 处理缩进和取消缩进
        if token.type in (TokenType.INDENT, TokenType.DEDENT):
            self.advance()
            return None
        
        # 处理 while 语句
        if token.type == TokenType.WHILE:
            self.advance()  # 跳过 while
            if not self.current_token or self.current_token.type != TokenType.LPAREN:
                raise ParserError("while 后需要括号", token)
            self.advance()  # 跳过左括号
            
            condition = self.comparison()  # 解析条件表达式
            
            if not self.current_token or self.current_token.type != TokenType.RPAREN:
                raise ParserError("缺少右括号", self.current_token)
            self.advance()  # 跳过右括号
            
            # 解析循环体
            if not self.current_token or self.current_token.type != TokenType.LBRACE:
                raise ParserError("while 语句体需要用 '{' 开始", self.current_token)
            self.advance()  # 跳过 {
            
            body = []
            while self.current_token and self.current_token.type != TokenType.RBRACE:
                stmt = self.statement()
                if stmt:  # 忽略None返回
                    body.append(stmt)
            
            if not self.current_token or self.current_token.type != TokenType.RBRACE:
                raise ParserError("while 语句体未正确结束，缺少 '}'", self.current_token)
            
            self.advance()  # 跳过 }
            
            return WhileNode(condition, body)
        
        # 处理导入语句
        if token.type == TokenType.IMPORT:
            self.advance()  # 跳过 import
            if self.current_token.type != TokenType.STRING:
                raise ParserError("导入语句需要文件路径", self.current_token)
            module_name = self.current_token.value
            self.advance()  # 跳过文件路径
            return ImportNode(module_name)
        
        # 处理代码块
        if token.type == TokenType.LBRACE:
            self.advance()  # 跳过 {
            statements = []
            while self.current_token and self.current_token.type != TokenType.RBRACE:
                stmt = self.statement()
                if stmt:  # 忽略None返回
                    statements.append(stmt)
            
            if not self.current_token or self.current_token.type != TokenType.RBRACE:
                raise ParserError("代码块未正确结束，缺少 '}'", self.current_token)
            
            self.advance()  # 跳过 }
            return CodeBlockNode(statements)
        
        # 处理函数定义
        if token.type == TokenType.DEF:
            return self.function_definition()
        
        # 处理 if 语句
        if token.type == TokenType.IF:
            return self.if_statement()
        
        # 处理 for 语句
        if token.type == TokenType.FOR:
            return self.for_statement()
        
        # 处理 print 语句
        if token.type == TokenType.PRINT:
            self.advance()  # 跳过 print
            if not self.current_token or self.current_token.type != TokenType.LPAREN:
                raise ParserError("print 后需要括号", token)
            self.advance()  # 跳过左括号
            
            # 处理空括号的情况
            if self.current_token and self.current_token.type == TokenType.RPAREN:
                self.advance()  # 跳过右括号
                return PrintNode(None)
                
            expr = self.expr()
            if not self.current_token or self.current_token.type != TokenType.RPAREN:
                raise ParserError("缺少右括号", self.current_token)
            self.advance()  # 跳过右括号
            return PrintNode(expr)
        
        # 处理 printnln 语句
        if token.type == TokenType.PRINTNLN:
            self.advance()  # 跳过 printnln
            if not self.current_token or self.current_token.type != TokenType.LPAREN:
                raise ParserError("printnln 后需要括号", token)
            self.advance()  # 跳过左括号
            
            # 处理空括号的情况
            if self.current_token and self.current_token.type == TokenType.RPAREN:
                self.advance()  # 跳过右括号
                return PrintlnNode(None)
                
            expr = self.expr()
            if not self.current_token or self.current_token.type != TokenType.RPAREN:
                raise ParserError("缺少右括号", self.current_token)
            self.advance()  # 跳过右括号
            return PrintlnNode(expr)
        
        # 处理 nsreturn 语句
        if token.type == TokenType.NSRETURN:
            self.advance()
            value = self.expr()
            return NsReturnNode(value)
        
        # 处理 return 语句
        if token.type == TokenType.RETURN:
            self.advance()
            value = self.expr()
            return ReturnNode(value)
        
        # 处理点号访问、数组访问或变量赋值
        if token.type == TokenType.IDENTIFIER:
            name = token.value
            name_token = token  # 保存标识符token
            self.advance()
            
            # 如果直接跟着左大括号，说明是代码块调用（比如 forEach { ... }）
            if self.current_token and self.current_token.type == TokenType.LBRACE:
                statements = []
                self.advance()  # 跳过 {
                while self.current_token and self.current_token.type != TokenType.RBRACE:
                    stmt = self.statement()
                    if stmt:  # 忽略None返回
                        statements.append(stmt)
                if not self.current_token or self.current_token.type != TokenType.RBRACE:
                    raise ParserError("代码块未正确结束，缺少 '}'", self.current_token)
                self.advance()  # 跳过 }
                return CallNode(name, [CodeBlockNode(statements)], name_token)
            
            # 处理点号访问（如 BCC.Codeblock）
            if self.current_token and self.current_token.type == TokenType.DOT:
                self.advance()  # 跳过点号
                if not self.current_token or self.current_token.type != TokenType.IDENTIFIER:
                    raise ParserError("点号后需要标识符", self.current_token)
                member = self.current_token.value
                self.advance()
                return DotAccessNode(name, member)
            
            # 处理数组访问（如 lines[i]）
            if self.current_token and self.current_token.type == TokenType.LBRACKET:
                self.advance()  # 跳过 [
                index = self.expr()  # 解析索引表达式
                if not self.current_token or self.current_token.type != TokenType.RBRACKET:
                    raise ParserError("缺少右方括号 ']'", self.current_token)
                self.advance()  # 跳过 ]
                
                # 检查是否是赋值语句
                if self.current_token and self.current_token.type == TokenType.EQUALS:
                    self.advance()  # 跳过 =
                    value = self.expr()
                    return AssignNode(ArrayAccessNode(name, index, name_token), value)
                
                return ArrayAccessNode(name, index, name_token)
            
            # 如果是函数调用
            elif self.current_token and self.current_token.type == TokenType.LPAREN:
                self.advance()  # 跳过左括号
                args = []
                
                # 如果不是右括号，说明有参数
                if self.current_token and self.current_token.type != TokenType.RPAREN:
                    # 解析第一个参数
                    args.append(self.comparison())  # 使用 comparison 而不是 expr
                    
                    # 解析剩余的参数
                    while self.current_token and self.current_token.type == TokenType.COMMA:
                        self.advance()  # 跳过逗号
                        if not self.current_token:
                            raise ParserError("意外的文件结束", None)
                        args.append(self.comparison())  # 使用 comparison 而不是 expr
                
                # 检查右括号
                if not self.current_token or self.current_token.type != TokenType.RPAREN:
                    raise ParserError("缺少右括号", self.current_token)
                self.advance()  # 跳过右括号
                
                # 检查是否有代码块
                if self.current_token and self.current_token.type == TokenType.LBRACE:
                    statements = []
                    self.advance()  # 跳过 {
                    
                    # 收集代码块中的所有语句
                    while self.current_token and self.current_token.type != TokenType.RBRACE:
                        stmt = self.statement()
                        if stmt:  # 忽略None返回
                            statements.append(stmt)
                            
                    # 检查代码块是否正确结束
                    if not self.current_token or self.current_token.type != TokenType.RBRACE:
                        raise ParserError("代码块未正确结束，缺少 '}'", self.current_token)
                    self.advance()  # 跳过 }
                    
                    # 将代码块作为最后一个参数添加
                    args.append(CodeBlockNode(statements))
                
                return CallNode(name, args, name_token)
            
            # 如果是赋值语句
            elif self.current_token and self.current_token.type == TokenType.EQUALS:
                self.advance()
                value = self.expr()
                return AssignNode(name, value)
            
            # 如果是变量引用
            return VariableNode(name)
        
        # 如果是表达式语句
        expr = self.expr()
        return expr

    def expr(self):
        """解析加减表达式"""
        node = self.term()

        while self.current_token and self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            op = self.current_token
            self.advance()
            right = self.term()
            node = BinOpNode(node, op, right)

        return node

    def term(self):
        """解析乘除表达式"""
        node = self.factor()

        while self.current_token and self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            op = self.current_token
            self.advance()
            right = self.factor()
            node = BinOpNode(node, op, right)

        return node

    def factor(self):
        """解析基本因子"""
        token = self.current_token
        
        if not token:
            raise ParserError("意外的文件结束", None)
            
        # 处理表达式
        if token.type == TokenType.EXPR:
            self.advance()  # ��过 expr
            if not self.current_token or self.current_token.type != TokenType.LPAREN:
                raise ParserError("expr 后需要括号", token)
            self.advance()  # 跳过左括号
            
            # 解析内部表达式
            expr = self.comparison()  # 使用 comparison 而不是 expr
            
            if not self.current_token or self.current_token.type != TokenType.RPAREN:
                raise ParserError("缺少右括号", self.current_token)
            self.advance()  # 跳过右括号
            return ExprNode(expr)
            
        if token.type == TokenType.NUMBER:
            self.advance()
            return NumberNode(token.value)
            
        if token.type == TokenType.STRING:
            self.advance()
            return StringNode(token.value)
            
        if token.type == TokenType.IDENTIFIER:
            name = token.value
            name_token = token  # 保存标识符token
            self.advance()
            
            # 处理点号访问（如 BCC.Codeblock）
            if self.current_token and self.current_token.type == TokenType.DOT:
                self.advance()  # 跳过点号
                if not self.current_token or self.current_token.type != TokenType.IDENTIFIER:
                    raise ParserError("点号后需要标识符", self.current_token)
                member = self.current_token.value
                self.advance()
                return DotAccessNode(name, member)
            
            # 处理数组访问（如 lines[i]）
            if self.current_token and self.current_token.type == TokenType.LBRACKET:
                self.advance()  # 跳过 [
                index = self.expr()  # 解析索引表达式
                if not self.current_token or self.current_token.type != TokenType.RBRACKET:
                    raise ParserError("缺少右方括号 ']'", self.current_token)
                self.advance()  # 跳过 ]
                return ArrayAccessNode(name, index, name_token)
            
            # 如果后面跟着左括号，说明是函数调用
            if self.current_token and self.current_token.type == TokenType.LPAREN:
                self.advance()  # 跳过左括号
                args = []
                
                # 处理参数列表
                if self.current_token and self.current_token.type != TokenType.RPAREN:
                    args.append(self.expr())
                    while self.current_token and self.current_token.type == TokenType.COMMA:
                        self.advance()  # 跳过逗号
                        args.append(self.expr())
                
                if not self.current_token or self.current_token.type != TokenType.RPAREN:
                    raise ParserError("缺少右括号", self.current_token)
                self.advance()  # 跳过右括号
                
                return CallNode(name, args, name_token)
            
            return VariableNode(name)
            
        if token.type == TokenType.LPAREN:
            self.advance()
            expr = self.comparison()  # 使用 comparison 而不是 expr
            if not self.current_token or self.current_token.type != TokenType.RPAREN:
                raise ParserError("缺少右括号", self.current_token)
            self.advance()
            return expr
            
        raise ParserError(f"无效的表达式: {token.value}", token)

    def if_statement(self):
        """解析if语句"""
        self.advance()  # 跳过 'if'
        
        # 检查并跳过左括号
        if self.current_token.type != TokenType.LPAREN:
            raise ParserError("if 语句条件需要用括号包裹", self.current_token)
        self.advance()
        
        # 解析条件
        condition = self.comparison()
        
        # 检查并跳过右括号
        if self.current_token.type != TokenType.RPAREN:
            raise ParserError("缺少右括号", self.current_token)
        self.advance()
        
        # 检查并处理代码块
        if self.current_token.type != TokenType.LBRACE:
            raise ParserError("if 语句后需要 '{'", self.current_token)
        self.advance()  # 跳过 '{'
        
        body = []
        while self.current_token and self.current_token.type != TokenType.RBRACE:
            stmt = self.statement()
            if stmt:  # 忽略None返回
                body.append(stmt)
        
        if not self.current_token or self.current_token.type != TokenType.RBRACE:
            raise ParserError("if 语句体未正确结束，缺少 '}'", self.current_token)
        
        self.advance()  # 跳过 '}'
        
        return IfNode(condition, body)

    def comparison(self):
        """解析比较表达式"""
        # 获取左边的表达式
        left = self.expr()
        
        # 如果有比较运算符，处理右边的表达式
        if self.current_token and self.current_token.type in (TokenType.EQ, TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE):
            op = self.current_token
            self.advance()
            right = self.expr()
            return BinOpNode(left, op, right)
        
        return left

    def parse_for_condition(self):
        """解析for循环的条件表达式"""
        if self.current_token.type == TokenType.IDENTIFIER:
            left = VariableNode(self.current_token.value)
            self.advance()
        else:
            left = self.expr()
        
        # 跳过比较运算符
        if self.current_token and self.current_token.type in (TokenType.EQ, TokenType.LT, TokenType.GT, TokenType.LE, TokenType.GE):
            op = self.current_token
            self.advance()
            right = self.expr()
            return BinOpNode(left, op, right)
        
        return left

    def for_statement(self):
        """解析 for 语句"""
        self.advance()  # 跳过 for
        
        if not self.current_token or self.current_token.type != TokenType.LPAREN:
            raise ParserError("for 语句需要括号", self.current_token)
        self.advance()  # 跳过左括号
        
        # 解析初始化语句
        init = None
        if self.current_token and self.current_token.type != TokenType.COMMA:
            init = self.statement()
            
        if not self.current_token or self.current_token.type != TokenType.COMMA:
            raise ParserError("for 语句需要三个参数，用逗号分隔", self.current_token)
        self.advance()  # 跳过第一个逗号
        
        # 解析条件表达式
        condition = None
        if self.current_token and self.current_token.type != TokenType.COMMA:
            condition = self.comparison()
            
        if not self.current_token or self.current_token.type != TokenType.COMMA:
            raise ParserError("for 语句需要三个参数，用逗号分隔", self.current_token)
        self.advance()  # 跳过第二个逗号
        
        # 解析更新语句
        update = None
        if self.current_token and self.current_token.type != TokenType.RPAREN:
            update = self.statement()
            
        if not self.current_token or self.current_token.type != TokenType.RPAREN:
            raise ParserError("缺少右括号", self.current_token)
        self.advance()  # 跳过右括号
        
        # 解析循环体
        if not self.current_token or self.current_token.type != TokenType.LBRACE:
            raise ParserError("for 语句体需要用 '{' 开始", self.current_token)
        self.advance()  # 跳过 {
        
        body = []
        while self.current_token and self.current_token.type != TokenType.RBRACE:
            stmt = self.statement()
            if stmt:
                body.append(stmt)
        
        if not self.current_token or self.current_token.type != TokenType.RBRACE:
            raise ParserError("for 语句体未正确结束，缺少 '}'", self.current_token)
        
        self.advance()  # 跳过 }
        
        return ForNode(init, condition, update, body)

    def function_definition(self):
        """解析函数定义"""
        self.advance()  # 跳过 'def'
        
        # 解析函数类型
        if self.current_token.type not in (TokenType.PUBLIC, TokenType.PRIVATE):
            raise ParserError("函数定义需要指定类型 (public/private)", self.current_token)
        func_type = self.current_token.value
        self.advance()
        
        # 解析函数名
        if self.current_token.type != TokenType.IDENTIFIER:
            raise ParserError("需要函数名", self.current_token)
        func_name = self.current_token.value
        self.advance()
        
        # 解析参数列表
        if self.current_token.type != TokenType.LPAREN:
            raise ParserError("函数定义需要参数列表", self.current_token)
        self.advance()
        
        params = []
        while self.current_token and self.current_token.type != TokenType.RPAREN:
            if self.current_token.type != TokenType.IDENTIFIER:
                raise ParserError("无效的参数名", self.current_token)
            
            param_name = self.current_token.value
            self.advance()
            
            # 检查是否是代码块参数
            if self.current_token and self.current_token.type == TokenType.COLON:
                self.advance()  # 跳过 :
                
                # 解析 BCC.Codeblock
                if (self.current_token and self.current_token.type == TokenType.IDENTIFIER and 
                    self.current_token.value == "BCC"):
                    self.advance()  # 跳过 BCC
                    
                    if not self.current_token or self.current_token.type != TokenType.DOT:
                        raise ParserError("需要点号", self.current_token)
                    self.advance()  # 跳过点号
                    
                    if not self.current_token or self.current_token.type != TokenType.IDENTIFIER or self.current_token.value != "Codeblock":
                        raise ParserError("无效的类型", self.current_token)
                    self.advance()  # 跳过 Codeblock
                    
                    params.append(CodeBlockParamNode(param_name))
                else:
                    raise ParserError("无效的参数类型", self.current_token)
            else:
                params.append(ParamNode(param_name))
            
            if self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()
                continue
            elif self.current_token and self.current_token.type == TokenType.RPAREN:
                break
            else:
                raise ParserError("参数列表语法错误", self.current_token)
        
        if not self.current_token or self.current_token.type != TokenType.RPAREN:
            raise ParserError("缺少右括号", self.current_token)
        self.advance()
        
        # 解析函数体
        if not self.current_token or self.current_token.type != TokenType.LBRACE:
            raise ParserError("函数体需要用 '{' 开始", self.current_token)
        self.advance()
        
        body = []
        while self.current_token and self.current_token.type != TokenType.RBRACE:
            stmt = self.statement()
            if stmt:  # 忽略None返回
                body.append(stmt)
        
        if not self.current_token or self.current_token.type != TokenType.RBRACE:
            raise ParserError("函数体未正确结束，缺少 '}'", self.current_token)
        
        self.advance()  # 跳过 '}'
        
        return FunctionNode(func_type, func_name, params, body)

class FunctionNode(ASTNode):
    """函数定义节点"""
    def __init__(self, type, name, params, body):
        self.type = type      # 函数类型（public/private）
        self.name = name      # 函数名
        self.params = params  # 参数列表
        self.body = body      # 函数体

    def __str__(self):
        return f"Function({self.type}, {self.name}, {self.params}, {self.body})"

class ParamNode(ASTNode):
    """函数参数节点"""
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f"Param({self.name})"

class CallNode(ASTNode):
    """函数调用节点"""
    def __init__(self, name, args, token=None):
        self.name = name    # 函数名
        self.args = args    # 参数列表
        self.token = token  # 保存token以获取位置信息

    def __str__(self):
        return f"Call({self.name}, {self.args})"

class ReturnNode(ASTNode):
    """返回语句节点"""
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return f"Return({self.value})"

class CodeBlockNode(ASTNode):
    """代码块节点"""
    def __init__(self, statements):
        self.statements = statements  # 代码块中的语句列表
        
    def __str__(self):
        return f"CodeBlock({self.statements})"

class CodeBlockParamNode(ParamNode):
    """代码块参数节点"""
    def __init__(self, name):
        super().__init__(name)
        self.is_codeblock = True

    def __str__(self):
        return f"CodeBlockParam({self.name})"

class ImportNode(ASTNode):
    """导入语句节点"""
    def __init__(self, module_name):
        self.module_name = module_name
        
    def __str__(self):
        return f"Import({self.module_name})"

class ArrayAccessNode(ASTNode):
    """数组访问节点"""
    def __init__(self, array, index, token=None):
        self.array = array  # 数组名
        self.index = index  # 索引表达式
        self.token = token  # 保存token以获取位置信息

    def __str__(self):
        return f"ArrayAccess({self.array}[{self.index}])"

class DotAccessNode(ASTNode):
    """点号访问节点，用于处理如 BCC.Codeblock 这样的表达式"""
    def __init__(self, object_name, member_name):
        self.object_name = object_name  # 对象名（如 BCC）
        self.member_name = member_name  # 成员名（如 Codeblock）

    def __str__(self):
        return f"DotAccess({self.object_name}.{self.member_name})"

class NsReturnNode(ASTNode):
    """不停止的返回语句节点"""
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return f"NsReturn({self.value})"

class ExprNode(ASTNode):
    """表达式节点，用于包装表达式以延迟求值"""
    def __init__(self, expr):
        self.expr = expr
        
    def __str__(self):
        return f"Expr({self.expr})"