from src.lexer import Lexer
from src.parser import Parser, ParserError
from src.interpreter import Interpreter, InterpreterError
import sys
import argparse
import logging
import time
import json
import os
import cProfile
import pstats
from datetime import datetime

# 添加颜色常量
class Colors:
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    END = '\033[0m'

# 配置类
class Config:
    def __init__(self):
        self.config_file = "bcc_config.json"
        self.default_config = {
            "debug_mode": False,
            "log_file": "bcc.log",
            "max_recursion_depth": 1000,
            "show_performance_stats": False,
            "auto_save_history": True,
            "history_file": ".bcc_history",
            "theme": {
                "prompt": ">> ",
                "continuation_prompt": "... "
            }
        }
        self.settings = self.load_config()

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return {**self.default_config, **json.load(f)}
            return self.default_config
        except Exception as e:
            logging.warning(f"加载配置文件失败: {e}")
            return self.default_config

    def save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logging.error(f"保存配置文件失败: {e}")

# 初始化配置
config = Config()

# 设置日志系统
def setup_logging(debug_mode=False):
    if not debug_mode:
        # 非调试模式下禁用所有日志
        logging.getLogger().setLevel(logging.CRITICAL + 1)
        return
        
    # 调试模式下启用所有日志
    logging.basicConfig(
        filename=config.settings["log_file"],
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 同时输出到控制台
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(formatter)
    
    # 移除所有现有的处理器
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # 添加新的处理器
    root_logger.addHandler(console_handler)
    
    # 如果需要文件日志
    if config.settings["log_file"]:
        file_handler = logging.FileHandler(config.settings["log_file"], encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        root_logger.addHandler(file_handler)

# 性能分析装饰器
def profile_performance(func):
    def wrapper(*args, **kwargs):
        if config.settings["show_performance_stats"]:
            profiler = cProfile.Profile()
            result = profiler.runcall(func, *args, **kwargs)
            stats = pstats.Stats(profiler)
            stats.sort_stats('cumulative')
            print(f"\n{Colors.BLUE}性能统计:{Colors.END}")
            stats.print_stats(20)  # 显示前20个最耗时的操作
            return result
        return func(*args, **kwargs)
    return wrapper

def show_bcc_help():
    """显示 BCC 语言的使用说明"""
    help_text = f"""
-------------------
BCC语言使用说明 / BCC Language Guide
-------------------
该文档仅提供简略的语法说明，详细语法请参考官方文档https://dhjs0000.github.io/bccWeb/。
This document provides a brief syntax guide. For detailed syntax, please refer to the official documentation at https://dhjs0000.github.io/bccWeb/.

1. 变量和赋值 / Variables and Assignment:
    BCC使用动态类型，变量类型在运行时确定。
    BCC uses dynamic typing, and variable types are determined at runtime.
    变量名必须以字母开头，可以包含字母、数字和下划线。
    Variable names must start with a letter and can contain letters, numbers, and underscores.
    变量名区分大小写。
    Variable names are case-sensitive.
    变量名不能与BCC关键字相同。
    Variable names cannot be the same as BCC keywords.

    示例 / Example:
    x = 5
    y = "hello"

2. 基本运算 / Basic Operations
    A. 算术运算 / Arithmetic Operations
    加法: a + b / Addition: a + b
    减法: a - b / Subtraction: a - b
    乘法: a * b / Multiplication: a * b
    除法: a / b / Division: a / b

    B. 比较运算 / Comparison Operations
    等于: == / Equal to: ==
    大于: > / Greater than: >
    小于: < / Less than: <

3. 关键字 / Keywords
    BCC语言有以下关键字 / BCC language has the following keywords: 
    NUMBER      数字 / Number
    STRING      字符串 / String
    IDENTIFIER  标识符（变量名）/ Identifier (variable name)
        
    运算符 / Operators
    PLUS        + / Plus
    MINUS       - / Minus
    MULTIPLY    * / Multiply
    DIVIDE      / / Divide
    EQUALS      = / Equals
        
    比较运算符 / Comparison Operators
    EQ          == / Equal
    LT          < / Less than
    GT          > / Greater than
    LE          <= / Less than or equal to
    GE          >= / Greater than or equal to
        
    括号和其他符号 / Parentheses and Other Symbols
    LPAREN       ( / Left parenthesis
    RPAREN       ) / Right parenthesis
    COLON        : / Colon
        
    关键字 / Keywords
    PRINT       print 关键字 / print keyword
    PRINTNLN    printnln 关键字（不换行打印）/ printnln keyword (print without newline)
    IF          if 关键字 / if keyword
    FOR         for 关键字 / for keyword
    WHILE       while 关键字 / while keyword
    RETURN      return 关键字 / return keyword
    NSRETURN    nsreturn 关键字（不停止的返回）/ nsreturn keyword (non-stopping return)
    EXPR        expr 关键字 / expr keyword
        
    特殊标记 / Special Tokens
    EOF         文件结束标记 / End of file marker
    INDENT      缩进 / Indent
    DEDENT      取消缩进 / Dedent
    LBRACE      左大括号 / Left brace
    RBRACE      右大括号 / Right brace
    COMMA       逗号 / Comma
    SEMICOLON   分号 ; / Semicolon ;
        
    函数相关 / Function Related
    DEF         def 关键字 / def keyword
    PUBLIC      public 关键字 / public keyword
    PRIVATE     private 关键字 / private keyword
        
    类相关 / Class Related
    CLASS       class 关键字 / class keyword
        
    代码块相关 / Code Block Related
    CODEBLOCK   BCC.Codeblock 类型 / BCC.Codeblock type
    DOT         . 符号，用于 BCC.Codeblock.lines / Dot symbol, used for BCC.Codeblock.lines
        
    模块相关 / Module Related
    IMPORT      import 关键字 / import keyword
    FROM        from 关键字 / from keyword
    AS          as 关键字 / as keyword
    BCM         .bcm 模块文件 / .bcm module file
    BCS         .bcs 源文件 / .bcs source file
        
    数组相关 / Array Related
    LBRACKET    [ / Left bracket
    RBRACKET    ] / Right bracket

4. 注释 / Comments
    BCC支持单行注释。/ BCC supports single-line comments.
    // 这是一个单行注释 / // This is a single-line comment
"""
    print(help_text)

@profile_performance
def run_file(filename, show_tokens=False, show_perror=False, debug=False):
    start_time = time.time()
    logging.info(f"开始执行文件: {filename}")
    
    # 检查文件类型
    if filename.endswith('.bcm'):
        logging.error("尝试直接运行模块文件")
        print(f"{Colors.RED}错误:{Colors.END} .bcm 文件是模块文件，不能直接运行。请使用 .bcs 文件导入它。")
        return
        
    try:
        # 使用 UTF-8 编码读取文件
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
            source_lines = source.splitlines()
        interpreter = Interpreter(debug=debug)  # 传递调试标志
        run(source, interpreter, show_tokens, show_perror, filename, source_lines)
        
        end_time = time.time()
        execution_time = end_time - start_time
        logging.info(f"文件执行完成，耗时: {execution_time:.2f}秒")
        
    except UnicodeDecodeError:
        logging.error(f"文件编码错误: {filename}")
        print(f"{Colors.RED}错误:{Colors.END} 文件编码错误，请确保文件使用 UTF-8 编码保存")
    except Exception as e:
        logging.error(f"执行文件时发生错误: {str(e)}", exc_info=True)
        raise

def format_error(filename, line, message, token=None, source_lines=None):
    """格式化错误信息，提供更详细的错误上下文"""
    logging.debug(f"格式化错误信息: {message}")
    # 基本错误信息
    result = f"\n{Colors.RED}错误:{Colors.END} 在文件 {Colors.YELLOW}{filename}{Colors.END} 中\n"
    
    # 添加错误类型和描述
    if "未定义的函数" in message:
        result += f"{Colors.RED}类型: 未定义的标识符{Colors.END}\n"
        result += f"{Colors.BLUE}描述:{Colors.END} 尝试调用未定义的函数\n"
    elif "缺少右括号" in message:
        result += f"{Colors.RED}类型: 语法错误{Colors.END}\n"
        result += f"{Colors.BLUE}描述:{Colors.END} 括号不匹配\n"
    elif "未定义的变量" in message:
        result += f"{Colors.RED}类型: 未定义的标识符{Colors.END}\n"
        result += f"{Colors.BLUE}描述:{Colors.END} 使用了未声明的变量\n"
    elif "无效的表达式" in message:
        result += f"{Colors.RED}类型: 语法错误{Colors.END}\n"
        result += f"{Colors.BLUE}描述:{Colors.END} 表达式语法不正确\n"
    else:
        result += f"{Colors.RED}类型: 一般错误{Colors.END}\n"
        result += f"{Colors.BLUE}描述:{Colors.END} {message}\n"

    # 显示错误位置
    result += f"{Colors.BLUE}位置:{Colors.END} 第 {line} 行"
    if token:
        result += f", 第 {token.column} 列"
    result += "\n"
    
    if source_lines:  # 确保有代码行
        # 显示更多的上下文行（最多显示5行）
        start_line = max(1, line - 2)
        end_line = min(len(source_lines), line + 2)
        
        # 添加代码块标记
        result += f"\n{Colors.YELLOW}相关代码:{Colors.END}\n"
        
        # 显示行号的宽度
        line_num_width = len(str(end_line))
        
        # 显示上下文代码
        for i in range(start_line - 1, end_line):
            line_content = source_lines[i].rstrip()
            line_num = str(i + 1).rjust(line_num_width)
            
            if i + 1 == line:  # 错误行
                result += f"{Colors.RED}>{Colors.END} {line_num} │ {line_content}\n"
                # 添加错误标记
                if token:
                    marker = " " * (len(line_num) + 2) + "│ " + " " * (token.column - 1)
                    marker += f"{Colors.RED}^{Colors.END}" * len(str(token.value))
                    result += marker + "\n"
            else:
                result += f"  {line_num} │ {line_content}\n"
    
    # 添加可能的修复建议
    result += f"\n{Colors.YELLOW}可能的解决方案:{Colors.END}\n"
    if "未定义的函数" in message:
        result += "1. 检查函数名是否拼写正确\n"
        result += "2. 确保已导入包该函的模块\n"
        result += "3. 检查函数名的大小写是否正确\n"
    elif "缺少右括号" in message:
        result += "1. 添加缺少的右括号\n"
        result += "2. 检查括号是否匹配\n"
    elif "未定义的变量" in message:
        result += "1. 确保使用变量前已经声明并赋值\n"
        result += "2. 检查变量名的拼写是否正确\n"
        result += "3. 检查变量名的大小写是否正确\n"
    elif "无效的表达式" in message:
        result += "1. 检查表达式的语法是否正确\n"
        result += "2. 确保所有运算符使用正确\n"
        result += "3. 检查表达式是否完整\n"
    else:
        result += "1. 仔细阅读错误信息\n"
        result += "2. 检查相关代码的语法\n"
    
    return result

@profile_performance
def run(source, interpreter, show_tokens=False, show_perror=False, filename="<stdin>", source_lines=None):
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        if show_tokens:
            logging.debug("显示词法分析tokens")
            for token in tokens:
                print(token)
        
        parser = Parser(tokens)
        try:
            ast = parser.parse()
            logging.debug("语法分析完成")
        except ParserError as e:
            logging.error(f"解析错误: {str(e)}")
            if source_lines is None:
                source_lines = source.splitlines()
            print(format_error(filename, e.token.line if e.token else 1, str(e), e.token, source_lines))
            return
        
        try:
            interpreter.interpret(ast)
            logging.debug("代码执行完成")
        except InterpreterError as e:
            logging.error(f"解释器错误: {str(e)}")
            if hasattr(e, 'line'):
                if source_lines is None:
                    source_lines = source.splitlines()
                print(format_error(filename, e.line, e.message, e.token, source_lines))
            else:
                print(f"{Colors.RED}错误:{Colors.END} {e.message}")
            if show_perror:
                raise
    except Exception as e:
        logging.error(f"执行过程中发生错误: {str(e)}", exc_info=True)
        if show_perror:
            raise
        print(format_error(filename, 1, str(e), None, source_lines))

class REPL:
    def __init__(self):
        self.interpreter = Interpreter()
        self.history = []
        self.load_history()

    def load_history(self):
        if config.settings["auto_save_history"]:
            try:
                history_file = config.settings["history_file"]
                if os.path.exists(history_file):
                    with open(history_file, 'r', encoding='utf-8') as f:
                        self.history = f.readlines()
            except Exception as e:
                logging.warning(f"加载历史记录失败: {e}")

    def save_history(self):
        if config.settings["auto_save_history"]:
            try:
                with open(config.settings["history_file"], 'w', encoding='utf-8') as f:
                    f.writelines(self.history)
            except Exception as e:
                logging.warning(f"保存历史记录失败: {e}")

    def add_to_history(self, command):
        if command.strip() and (not self.history or command != self.history[-1]):
            self.history.append(command + '\n')
            self.save_history()

    def handle_command(self, command):
        """处理特殊命令"""
        command = command.strip().lower()
        if command == 'exit':
            print(f"{Colors.GREEN}再见！{Colors.END}")
            return True, True  # (退出, 是特殊命令)
        elif command == 'clear':
            os.system('cls' if os.name == 'nt' else 'clear')
            return False, True  # (不退出, 是特殊命令)
        elif command in ('help', 'bcchelp'):
            show_bcc_help()
            return False, True  # (不退出, 是特殊命令)
        return False, False  # (不退出, 不是特殊命令)

    def needs_more_input(self, text):
        """判断是否需要更多输入"""
        # 去除注释后的文本
        code_lines = []
        for line in text.split('\n'):
            comment_pos = line.find('//')
            if comment_pos != -1:
                line = line[:comment_pos]
            if line.strip():
                code_lines.append(line.strip())
        
        if not code_lines:
            return False
            
        # 检查是否有未闭合的括号
        brackets = {'(': ')', '{': '}', '[': ']'}
        stack = []
        
        for line in code_lines:
            for char in line:
                if char in brackets:
                    stack.append(char)
                elif char in brackets.values():
                    if not stack or brackets[stack.pop()] != char:
                        return False  # 括号不匹配，可能是语法错误
            
            # 检查以下特殊情况需要继续输入
            last_line = line.strip()
            if (last_line.endswith('{') or  # 类定义或函数定义
                last_line.endswith('\\') or  # 显式续行
                stack):  # 还有未闭合的括号
                return True
                
        return False

    def run(self):
        print(f"{Colors.GREEN}BCC 语言解释器{Colors.END}")
        print("命令:")
        print("  help    - 显示帮助信息")
        print("  clear   - 清屏")
        print("  exit    - 退出")
        print("\n支持多行输入，输入空行结束，分号可以代替换行\n")
        
        while True:
            try:
                # 收集输入
                lines = []
                first_line = True
                
                while True:
                    if first_line:
                        line = input(config.settings["theme"]["prompt"])
                        first_line = False
                        
                        # 处理特殊命令
                        should_exit, is_command = self.handle_command(line)
                        if is_command:
                            if should_exit:
                                return
                            first_line = True
                            continue
                            
                    else:
                        line = input(config.settings["theme"]["continuation_prompt"])
                    
                    lines.append(line)
                    
                    # 判断是否需要继续输入
                    current_text = '\n'.join(lines)
                    if not line.strip() or not self.needs_more_input(current_text):
                        break
                
                if not lines:  # 如果没有输入，继续下一轮
                    first_line = True
                    continue
                    
                # 处理分号：将分号替换为换行符
                text = '\n'.join(lines)
                text = text.replace(';', '\n')
                
                if text.strip():  # 如果有实际输入
                    self.add_to_history(text)
                    run(text, self.interpreter)
                    
            except KeyboardInterrupt:
                print("\n键盘中断，输入 'exit' 退出")
                first_line = True
            except Exception as e:
                logging.error(f"REPL执行错误: {str(e)}", exc_info=True)
                print(f"{Colors.RED}错误:{Colors.END} {str(e)}")
                first_line = True

def check_syntax(filename):
    """检查文件语法"""
    logging.info(f"开始语法检查: {filename}")
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        parser.parse()
        logging.info("语法检查通过")
        print(f"{Colors.GREEN}语法检查通过{Colors.END}")
        return True
    except Exception as e:
        logging.error(f"语法检查失败: {str(e)}")
        print(f"{Colors.RED}语法错误:{Colors.END} {str(e)}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description='BCC语言解释器')
    parser.add_argument('file', nargs='?', help='要执行的源代码文件')
    parser.add_argument('-t', '--show-tokens', action='store_true', help='显示词法分析结果')
    parser.add_argument('-p', '--show-perror', action='store_true', help='显示详细的解析错误信息')
    parser.add_argument('-d', '--debug', action='store_true', help='启用调试模式，显示详细的执行信息')
    parser.add_argument('--help-bcc', action='store_true', help='显示BCC语言使用说明')
    
    args = parser.parse_args()
    
    if args.help_bcc:
        show_bcc_help()
        return
        
    # 设置日志级别
    setup_logging(args.debug)
    
    if args.file:
        run_file(args.file, args.show_tokens, args.show_perror, args.debug)
    else:
        # REPL模式
        repl = REPL()
        repl.interpreter = Interpreter(debug=args.debug)  # 使用带调试标志的解释器
        repl.run()

if __name__ == '__main__':
    main() 