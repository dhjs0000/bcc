from .bcc_token import TokenType
from .parser import (
    NumberNode, BinOpNode, PrintNode, PrintlnNode, 
    VariableNode, AssignNode, StringNode, IfNode, 
    ForNode, FunctionNode, CallNode, ReturnNode, 
    CodeBlockNode, CodeBlockParamNode, ImportNode,
    Parser, ArrayAccessNode, DotAccessNode, NsReturnNode,
    ExprNode, WhileNode
)
from .lexer import Lexer
import json

class InterpreterError(Exception):
    """解释器错误，包含错误发生时的Token信息"""
    def __init__(self, message, node=None, token=None):
        self.message = message
        self.node = node
        self.token = token
        if token:
            self.line = token.line
            self.column = token.column
        elif hasattr(node, 'token'):  # 如果节点有token属性
            self.line = node.token.line
            self.column = node.token.column
        else:
            self.line = 0
            self.column = 0
        super().__init__(message)

class ReturnException(Exception):
    """用于处理函数返回值的特殊异常"""
    def __init__(self, value):
        self.value = value

class CodeBlock:
    """代码块类，用于存储和执行代码块"""
    def __init__(self, statements, interpreter):
        self.statements = statements
        self.interpreter = interpreter
        
    def execute(self):
        """执行代码块"""
        result = None
        for stmt in self.statements:
            result = self.interpreter.interpret(stmt)
        return result
        
    @property
    def lines(self):
        """返回代码块的语句列表"""
        return self.statements

class ModuleManager:
    def __init__(self, parent_interpreter=None):
        self.modules = {}
        self.loaded_files = set()
        self.lib_path = "./lib/bcc"
        self.parent_interpreter = parent_interpreter
        # 只有主解释器才加载配置
        if parent_interpreter is None:
            try:
                self.load_config()
            except Exception as e:
                print(f"警告: 加载基础库失败 - {str(e)}")
                import traceback
                print(traceback.format_exc())  # 添加这行来打印详细错误信息
        
    def load_config(self):
        """加载配置文件"""
        try:
            config_path = f"{self.lib_path}/config.json"
            print(f"尝试加载配置文件: {config_path}")  # 添加调试信息
            
            with open(config_path, "r", encoding='utf-8') as f:
                config = json.load(f)
                self.lib_path = config.get("libPath", self.lib_path)
                # 自动加载默认库
                for module in config.get("autoload", []):
                    print(f"自动加载模块: {module}")  # 添加调试信息
                    self.load_module(module)
        except FileNotFoundError:
            print(f"找不到配置文件: {config_path}")  # 添加调试信息
            pass
        except Exception as e:
            print(f"加载配置文件时出错: {str(e)}")  # 添加调试信息
            raise

    def load_module(self, filename):
        """加载模块文件"""
        try:
            # 确定文件路径
            if filename.endswith('.bcm'):
                filepath = f"{self.lib_path}/{filename}"
            else:
                filepath = filename
                
            print(f"尝试加载模块: {filepath}")  # 添加调试信息
            
            # 检查是否已加载
            if filepath in self.loaded_files:
                print(f"模块 {filepath} 已加载，直接返回")
                return self.modules[filepath]
                
            # 使用 UTF-8 编码读取文件
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
                
            print(f"成功读取文件内容: {filepath}")  # 添加调试信息
            
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            
            # 创建新的解释器实例用于模块
            module_interpreter = Interpreter(self)
            module_interpreter.interpret(ast)
            
            self.modules[filepath] = module_interpreter
            self.loaded_files.add(filepath)
            
            print(f"成功加载模块: {filepath}")  # 添加调试信息
            return module_interpreter
            
        except FileNotFoundError:
            print(f"找不到模块文件: {filepath}")  # 添加调试信息
            raise InterpreterError(f"找不到模块: {filename}", None)
        except Exception as e:
            print(f"加载模块时出错: {str(e)}")  # 添加调试信息
            import traceback
            print(traceback.format_exc())
            raise

class Interpreter:
    def __init__(self, parent_module_manager=None):
        # 存储变量的字典
        self.variables = {}
        self.functions = {}  # 存储函数定义
        # 如果有父模块管理器，使用它，否则创建新的
        if isinstance(parent_module_manager, ModuleManager):
            self.module_manager = parent_module_manager
        else:
            self.module_manager = ModuleManager(self)
        
        # 添加内置函数
        self.builtin_functions = {
            'len': self.builtin_len,
            'eval': self.builtin_eval,
            # 可以添加其他内置函数...
        }
    
    def builtin_len(self, args):
        """内置的 len 函数"""
        if len(args) != 1:
            raise InterpreterError("len() 函数需要一个参数")
        
        # args 已经是计算后的值，不需要再次 evaluate
        value = args[0]
        
        if isinstance(value, list):
            return len(value)
        if isinstance(value, CodeBlock):
            return len(value.lines)
        if isinstance(value, str):
            return len(value)
            
        raise InterpreterError(f"len() 函数不支持类型: {type(value)}")
    
    def builtin_eval(self, args):
        """内置的 eval 函数，用于求值表达式"""
        if len(args) != 1:
            raise InterpreterError("eval() 函数需要一个参数")
        
        expr = args[0]
        if not isinstance(expr, ExprNode):
            raise InterpreterError("eval() 函数需要一个表达式参数")
            
        return self.evaluate(expr.expr)
    
    def evaluate(self, node):
        """计算表达式的值"""
        if isinstance(node, NumberNode):
            return node.value
        
        if isinstance(node, StringNode):
            return node.value
        
        if isinstance(node, ExprNode):
            return self.evaluate(node.expr)  # 递归求值内部表达式
        
        if isinstance(node, VariableNode):
            if node.name not in self.variables:
                raise Exception(f"未定义的变量: {node.name}")
            value = self.variables[node.name]
            if isinstance(value, CodeBlock):
                return value.execute()
            return value
            
        if isinstance(node, BinOpNode):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            
            if node.op.type == TokenType.PLUS:
                return left + right
            elif node.op.type == TokenType.MINUS:
                return left - right
            elif node.op.type == TokenType.MULTIPLY:
                return left * right
            elif node.op.type == TokenType.DIVIDE:
                return left / right
            elif node.op.type == TokenType.EQ:
                return left == right
            elif node.op.type == TokenType.LT:
                return left < right
            elif node.op.type == TokenType.GT:
                return left > right
            elif node.op.type == TokenType.LE:
                return left <= right
            elif node.op.type == TokenType.GE:
                return left >= right
                
        if isinstance(node, CallNode):
            # 检查是否是内置函数
            if node.name in self.builtin_functions:
                # 计算所有参数的值
                args = [self.evaluate(arg) for arg in node.args]
                return self.builtin_functions[node.name](args)
            
            # 检查是否是用户定义的函数
            if node.name not in self.functions:
                raise InterpreterError(f"未定义的函数: {node.name}", node, node.token)
            
            # 执行用户定义的函数
            func = self.functions[node.name]
            if len(node.args) != len(func.params):
                raise InterpreterError(f"函数 {node.name} 需要 {len(func.params)} 个参数，但提供了 {len(node.args)} 个", node)
            
            # 保存当前变量环境
            old_vars = self.variables.copy()
            
            # 设置参数
            for param, arg in zip(func.params, node.args):
                if isinstance(param, CodeBlockParamNode):
                    # 如果是代码块参数，创建 CodeBlock 对象
                    if isinstance(arg, CodeBlockNode):
                        self.variables[param.name] = CodeBlock(arg.statements, self)
                    else:
                        raise InterpreterError(f"参数 {param.name} 需要代码块", node)
                else:
                    self.variables[param.name] = self.evaluate(arg)
            
            # 执行函数体
            result = None
            try:
                for stmt in func.body:
                    result = self.interpret(stmt)
            except ReturnException as e:
                result = e.value
            
            # 恢复变量环境
            self.variables = old_vars
            
            return result
            
        raise Exception(f"无法计算表达式: {node}")

    def interpret(self, node):
        """解释执行AST节点"""
        if node is None:
            return None
            
        if isinstance(node, ImportNode):
            self.import_module(node.module_name)
            return None
            
        if isinstance(node, list):
            # 处理语句列表
            for statement in node:
                self.interpret(statement)
            return None
            
        # 处理数字节点
        if isinstance(node, NumberNode):
            return node.value
        
        # 处理字符串节点
        if isinstance(node, StringNode):
            return node.value
        
        # 处理变量节点    
        if isinstance(node, VariableNode):
            if node.name not in self.variables:
                raise InterpreterError(f"未定义的变量: {node.name}", node)
            return self.variables[node.name]
            
        # 处理赋值节点
        if isinstance(node, AssignNode):
            value = self.interpret(node.value)
            self.variables[node.name] = value
            return value
            
        # 处理二元运算节点
        if isinstance(node, BinOpNode):
            return self.evaluate(node)
            
        # 处理打印节点
        if isinstance(node, PrintNode):
            result = self.interpret(node.expr)
            print(result)
            return None

        # 处理不换行打印节点
        if isinstance(node, PrintlnNode):
            result = self.interpret(node.expr)
            print(result, end='')
            return None 

        if isinstance(node, IfNode):
            condition_value = self.evaluate(node.condition)
            if condition_value:
                for statement in node.body:
                    self.interpret(statement)
            return None

        if isinstance(node, ForNode):
            # 执行初始化语句
            self.interpret(node.init)
            
            # 循环执行
            while True:
                # 检查条件
                if not self.evaluate(node.condition):
                    break
                
                # 执行循环体
                for stmt in node.body:
                    self.interpret(stmt)
                
                # 执行更新语句
                self.interpret(node.update)
            
            return None

        if isinstance(node, FunctionNode):
            # 存储函数定义
            self.functions[node.name] = node
            return None
            
        if isinstance(node, CallNode):
            # 检查是否是内置函数
            if node.name in self.builtin_functions:
                args = [self.evaluate(arg) for arg in node.args]
                return self.builtin_functions[node.name](args)
            
            # 检查是否是用户定义的函数
            if node.name not in self.functions:
                raise InterpreterError(f"未定义的函数: {node.name}", node, node.token)
            
            func = self.functions[node.name]
            if len(node.args) != len(func.params):
                raise InterpreterError(f"函数 {node.name} 需要 {len(func.params)} 个参数，但提供了 {len(node.args)} 个", node)
            
            # 保存当前变量环境
            old_vars = self.variables.copy()
            
            # 设置参数
            for param, arg in zip(func.params, node.args):
                if isinstance(param, CodeBlockParamNode):
                    # 如果是代码块参数，创建 CodeBlock 对象
                    if isinstance(arg, CodeBlockNode):
                        self.variables[param.name] = CodeBlock(arg.statements, self)
                    else:
                        raise InterpreterError(f"参数 {param.name} 需要代码块", node)
                else:
                    self.variables[param.name] = self.evaluate(arg)
            
            # 执行函数体
            result = None
            try:
                for stmt in func.body:
                    result = self.interpret(stmt)
            except ReturnException as e:
                result = e.value
            finally:
                # 恢复变量环境
                self.variables = old_vars
            
            return result

        if isinstance(node, ReturnNode):
            raise ReturnException(self.evaluate(node.value))

        if isinstance(node, ArrayAccessNode):
            array = self.variables.get(node.array)
            if array is None:
                raise InterpreterError(f"未定义的变量: {node.array}", node)
            if not hasattr(array, 'lines'):
                raise InterpreterError(f"变量 {node.array} 不是数组", node)
            index = self.evaluate(node.index)
            if not isinstance(index, int):
                raise InterpreterError("数组索引必须是整数", node)
            if index < 0 or index >= len(array.lines):
                raise InterpreterError("数组索引越界", node)
            return array.lines[index]

        if isinstance(node, DotAccessNode):
            # 处理特殊的 BCC.Codeblock 类型
            if node.object_name == "BCC" and node.member_name == "Codeblock":
                return "BCC.Codeblock"  # 返回类型标识符
            
            # 处理代码块的 lines 属性
            obj = self.variables.get(node.object_name)
            if obj is None:
                raise InterpreterError(f"未定义的变量: {node.object_name}", node)
            
            if isinstance(obj, CodeBlock):
                if node.member_name == "lines":
                    return obj.lines
                raise InterpreterError(f"代码块对象没有属性: {node.member_name}", node)
            
            raise InterpreterError(f"未知的点号访问: {node.object_name}.{node.member_name}", node)

        if isinstance(node, NsReturnNode):
            value = self.evaluate(node.value)
            if isinstance(value, CodeBlock):
                value.execute()
            return None  # 不中断执行

        if isinstance(node, WhileNode):
            while self.evaluate(node.condition):
                for stmt in node.body:
                    self.interpret(stmt)
            return None

    def import_module(self, module_name):
        """导入模块"""
        module = self.module_manager.load_module(module_name)
        # 将模块的函数添加到当前作用域
        self.functions.update(module.functions)