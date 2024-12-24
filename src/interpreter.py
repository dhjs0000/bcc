from .bcc_token import TokenType
from .parser import (
    NumberNode, BinOpNode, PrintNode, PrintlnNode, 
    VariableNode, AssignNode, StringNode, IfNode, 
    ForNode, FunctionNode, CallNode, ReturnNode, 
    CodeBlockNode, CodeBlockParamNode, ImportNode,
    Parser, ArrayAccessNode, DotAccessNode, NsReturnNode,
    ExprNode, WhileNode, ClassNode
)
from .lexer import Lexer
import json
import logging

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
        self.debug = parent_interpreter.debug if parent_interpreter else False
        # 只有主解释器才加载配置
        if parent_interpreter is None:
            try:
                self.load_config()
            except Exception as e:
                if self.debug:
                    print(f"警告: 加载基础库失败 - {str(e)}")
                    import traceback
                    print(traceback.format_exc())
        
    def load_config(self):
        """加载配置文件"""
        try:
            config_path = f"{self.lib_path}/config.json"
            if self.debug:
                print(f"尝试加载配置文件: {config_path}")
            
            with open(config_path, "r", encoding='utf-8') as f:
                config = json.load(f)
                self.lib_path = config.get("libPath", self.lib_path)
                # 自动加载默认库
                for module in config.get("autoload", []):
                    if self.debug:
                        print(f"自动加载模块: {module}")
                    self.load_module(module)
        except FileNotFoundError:
            if self.debug:
                print(f"找不到配置文件: {config_path}")
            pass
        except Exception as e:
            if self.debug:
                print(f"加载配置文件时出错: {str(e)}")
            raise

    def load_module(self, filename):
        """加载模块文件"""
        try:
            # 确定文件路径
            if filename.endswith('.bcm'):
                filepath = f"{self.lib_path}/{filename}"
            else:
                filepath = filename
                
            if self.debug:
                print(f"尝试加载模块: {filepath}")
            
            # 检查是否已加载
            if filepath in self.loaded_files:
                if self.debug:
                    print(f"模块 {filepath} 已加载，直接返回")
                return self.modules[filepath]
                
            # 使用 UTF-8 编码读取文件
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
                
            if self.debug:
                print(f"成功读取文件内容: {filepath}")
            
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()
            
            # 创建新的解释器实例用于模块
            module_interpreter = Interpreter(self, self.debug)
            module_interpreter.interpret(ast)
            
            self.modules[filepath] = module_interpreter
            self.loaded_files.add(filepath)
            
            if self.debug:
                print(f"成功加载模块: {filepath}")
            return module_interpreter
            
        except FileNotFoundError:
            if self.debug:
                print(f"找不到模块文件: {filepath}")
            raise InterpreterError(f"找不到模块: {filename}", None)
        except Exception as e:
            if self.debug:
                print(f"加载模块时出错: {str(e)}")
                import traceback
                print(traceback.format_exc())
            raise

class BCCClass:
    """BCC 类的运行时表示"""
    def __init__(self, name, methods, attributes):
        self.name = name
        self.methods = methods
        self.attributes = attributes.copy()

class BCCInstance:
    """BCC 类的实例"""
    def __init__(self, bcc_class):
        self.bcc_class = bcc_class
        self.attributes = bcc_class.attributes.copy()

    def get_method(self, name):
        """获取实例方法"""
        if name in self.bcc_class.methods:
            return self.bcc_class.methods[name]
        raise InterpreterError(f"类 {self.bcc_class.name} 没有方法 {name}")

    def get_attribute(self, name):
        """获取实例属性"""
        if name in self.attributes:
            return self.attributes[name]
        raise InterpreterError(f"实例没有属性 {name}")

    def set_attribute(self, name, value):
        """设置实例属性"""
        self.attributes[name] = value

    def __str__(self):
        """返回实例的字符串表示"""
        attrs = []
        for name, value in self.attributes.items():
            attrs.append(f"{name}={value}")
        return f"{self.bcc_class.name}({', '.join(attrs)})"

    def __repr__(self):
        """返回实例的详细字符串表示"""
        return self.__str__()

class Interpreter:
    def __init__(self, parent_module_manager=None, debug=False):
        # 存储变量的字典
        self.variables = {}
        self.functions = {}  # 存储函数定义
        self.debug = debug  # 添加调试标志
        
        # 如果有父模块管理器，使用它，否则创建新的
        if isinstance(parent_module_manager, ModuleManager):
            self.module_manager = parent_module_manager
        else:
            self.module_manager = ModuleManager(self)
        
        # 添加内置函数
        self.builtin_functions = {
            'len': self.builtin_len,
            'eval': self.builtin_eval,
            'str': self.builtin_str,
            'int': self.builtin_int,
            'float': self.builtin_float,
            'bool': self.builtin_bool,
            'print': self.builtin_print,
            'type': self.builtin_type,
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
    
    def builtin_str(self, args):
        """内置的 str 函数"""
        if len(args) != 1:
            raise InterpreterError("str() 函数需要一个参数")
        return str(args[0])
    
    def builtin_int(self, args):
        """内置的 int 函数"""
        if len(args) != 1:
            raise InterpreterError("int() 函数需要一个参数")
        try:
            return int(args[0])
        except ValueError:
            raise InterpreterError(f"无法将 {args[0]} 转换为整数")
    
    def builtin_float(self, args):
        """内置的 float 函数"""
        if len(args) != 1:
            raise InterpreterError("float() 函数需要一个参数")
        try:
            return float(args[0])
        except ValueError:
            raise InterpreterError(f"无法将 {args[0]} 转换为浮点数")
    
    def builtin_bool(self, args):
        """内置的 bool 函数"""
        if len(args) != 1:
            raise InterpreterError("bool() 函数需要一个参数")
        return bool(args[0])
    
    def builtin_print(self, args):
        """内置的 print 函数"""
        print(*args)
        return None
    
    def builtin_type(self, args):
        """内置的 type 函数"""
        if len(args) != 1:
            raise InterpreterError("type() 函数需要一个参数")
        return type(args[0]).__name__
    
    def evaluate(self, node):
        """计算表达式的值"""
        if isinstance(node, NumberNode):
            return node.value
        
        if isinstance(node, StringNode):
            return node.value
            
        if isinstance(node, ExprNode):
            return self.evaluate(node.expr)
            
        if isinstance(node, VariableNode):
            if node.name not in self.variables:
                raise InterpreterError(f"未定义的变量: {node.name}", node)
            return self.variables[node.name]
            
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
            if isinstance(node.name, str) and node.name in self.builtin_functions:
                args = [self.evaluate(arg) for arg in node.args]
                return self.builtin_functions[node.name](args)
            
            # 处理方法调用
            if isinstance(node.name, DotAccessNode):
                obj = self.evaluate(VariableNode(node.name.object_name))
                if isinstance(obj, BCCInstance):
                    method = obj.get_method(node.name.member_name)
                    args = [self.evaluate(arg) for arg in node.args]
                    # 将实例作为第一个参数（self）传入
                    return self.execute_function(method, [obj] + args)
                raise InterpreterError(f"无法在非对象类型上调用方法", node)
            
            # 处理普通函数调用
            if isinstance(node.name, str):
                if node.name not in self.functions:
                    raise InterpreterError(f"未定义的函数: {node.name}", node, node.token)
                
                func = self.functions[node.name]
                args = [self.evaluate(arg) for arg in node.args]
                return self.execute_function(func, args)
            
            raise InterpreterError(f"无效的函数调用", node)
            
        if isinstance(node, DotAccessNode):
            # 处理对象属性访问
            obj = self.evaluate(VariableNode(node.object_name))
            if isinstance(obj, BCCInstance):
                return obj.get_attribute(node.member_name)
            raise InterpreterError(f"无法访问非对象类型的属性", node)
            
        raise Exception(f"无法计算表��式: {node}")

    def interpret(self, node):
        """解释执行AST节点"""
        if node is None:
            return None
            
        if self.debug:
            print(f"DEBUG: 正在解释节点: {type(node)}")
            
        if isinstance(node, ImportNode):
            self.import_module(node.module_name)
            return None
            
        if isinstance(node, list):
            # 处理语句列表
            if self.debug:
                print("DEBUG: 处理语句列表")
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
            if self.debug:
                print(f"DEBUG: 处理赋值: {node.name} = {node.value}")
            if isinstance(node.name, str):
                # 普通变量赋值
                value = self.interpret(node.value)
                self.variables[node.name] = value
                return value
            elif isinstance(node.name, DotAccessNode):
                # 对象属性赋值
                obj = self.interpret(VariableNode(node.name.object_name))
                if isinstance(obj, BCCInstance):
                    value = self.interpret(node.value)
                    obj.set_attribute(node.name.member_name, value)
                    return value
                raise InterpreterError(f"无法给非对象类型赋值属性", node)
            else:
                raise InterpreterError(f"无效的赋值目标", node)
            
        # 处理二元运算节点
        if isinstance(node, BinOpNode):
            return self.evaluate(node)
            
        # 处理打印节点
        if isinstance(node, PrintNode):
            if self.debug:
                print("DEBUG: 执行打印操作")
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
            if self.debug:
                print(f"DEBUG: 定义函数: {node.name}")
            self.functions[node.name] = node
            return None
            
        if isinstance(node, CallNode):
            if self.debug:
                print(f"DEBUG: 调用函数: {node.name}")
            # 检查是否是内置函数
            if isinstance(node.name, str) and node.name in self.builtin_functions:
                args = [self.interpret(arg) for arg in node.args]
                return self.builtin_functions[node.name](args)
            
            # 处理方法调用
            if isinstance(node.name, DotAccessNode):
                obj = self.interpret(VariableNode(node.name.object_name))
                if isinstance(obj, BCCInstance):
                    method = obj.get_method(node.name.member_name)
                    args = [self.interpret(arg) for arg in node.args]
                    # 将实例作为第一个参数（self）传入
                    return self.execute_function(method, [obj] + args)
                raise InterpreterError(f"无法在非对象类型上调用方法", node)
            
            # 处理普通函数调用或类实例化
            if isinstance(node.name, str):
                # 检查是否是类名
                if node.name in self.variables and isinstance(self.variables[node.name], BCCClass):
                    # 创建类实例
                    bcc_class = self.variables[node.name]
                    instance = BCCInstance(bcc_class)
                    return instance
                
                # 检查是否是函数调用
                if node.name not in self.functions:
                    raise InterpreterError(f"未定义的函数或类: {node.name}", node, node.token)
                
                func = self.functions[node.name]
                args = [self.interpret(arg) for arg in node.args]
                return self.execute_function(func, args)
            
            raise InterpreterError(f"无效的函数调用", node)

        if isinstance(node, ReturnNode):
            raise ReturnException(self.interpret(node.value))

        if isinstance(node, ArrayAccessNode):
            array = self.variables.get(node.array)
            if array is None:
                raise InterpreterError(f"未定义的变量: {node.array}", node)
            if not hasattr(array, 'lines'):
                raise InterpreterError(f"变量 {node.array} 不是数组", node)
            index = self.interpret(node.index)
            if not isinstance(index, int):
                raise InterpreterError("数组索引必须是整数", node)
            if index < 0 or index >= len(array.lines):
                raise InterpreterError("数组索引越界", node)
            return array.lines[index]

        if isinstance(node, NsReturnNode):
            value = self.interpret(node.value)
            if isinstance(value, CodeBlock):
                value.execute()
            return None  # 不中断执行

        if isinstance(node, WhileNode):
            while self.evaluate(node.condition):
                for stmt in node.body:
                    self.interpret(stmt)
            return None

        if isinstance(node, ClassNode):
            if self.debug:
                print(f"DEBUG: 定义类: {node.name}")
            # 处理方法
            methods = {}
            for method in node.methods:
                methods[method.name] = method
            
            # 处理属性的初始值
            attributes = {}
            for name, value_node in node.attributes.items():
                attributes[name] = self.interpret(value_node)
            
            # 创建类对象
            bcc_class = BCCClass(node.name, methods, attributes)
            self.variables[node.name] = bcc_class
            return bcc_class

        raise InterpreterError(f"未知的节点类型: {type(node)}", node)

    def import_module(self, module_name):
        """导入模块"""
        module = self.module_manager.load_module(module_name)
        # 将模块的函数添加到当前作用域
        self.functions.update(module.functions)

    def execute_function(self, func, args):
        """执行函数调用"""
        if len(args) != len(func.params):
            raise InterpreterError(f"函数 {func.name} 需要 {len(func.params)} 个参数，但提供了 {len(args)} 个")
        
        # 保存当前变量环境
        old_vars = self.variables.copy()
        
        try:
            # 设置参数
            for param, arg in zip(func.params, args):
                if isinstance(param, CodeBlockParamNode):
                    # 如果是代码块参数，创建 CodeBlock 对象
                    if isinstance(arg, CodeBlockNode):
                        self.variables[param.name] = CodeBlock(arg.statements, self)
                    else:
                        raise InterpreterError(f"参数 {param.name} 需要代码块")
                else:
                    self.variables[param.name] = arg
            
            # 执行函数体
            result = None
            for stmt in func.body:
                result = self.interpret(stmt)
            return result
            
        except ReturnException as e:
            return e.value
            
        finally:
            # 恢复变量环境
            self.variables = old_vars