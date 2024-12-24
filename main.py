from src.lexer import Lexer
from src.parser import Parser, ParserError
from src.interpreter import Interpreter, InterpreterError
import sys
import argparse

# 添加颜色常量
class Colors:
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def show_bcc_help():
    """显示 BCC 语言的使用说明"""
    help_text = """
BCC 语言使用说明:

1. 变量和赋值:
   x = 5
   y = "hello"

2. 算术运算:
   加法: a + b
   减法: a - b
   乘法: a * b
   除法: a / b

3. 打印:
   print("Hello")    - 不换行打印
   println("World")  - 换行打印

4. 条件语句:
   if 条件 {
       语句1
       语句2
   }

5. 比较运算:
   等于: ==
   大于: >
   小于: <

示例代码:
x = 5
y = 3
if x > y {
    println("x is greater than y")
}
"""
    print(help_text)

def run_file(filename, show_tokens=False, show_perror=False):
    # 检查文件类型
    if filename.endswith('.bcm'):
        print("错误: .bcm 文件是模块文件，不能直接运行。请使用 .bcs 文件导入它。")
        return
        
    try:
        # 使用 UTF-8 编码读取文件
        with open(filename, 'r', encoding='utf-8') as f:
            source = f.read()
            source_lines = source.splitlines()
        interpreter = Interpreter()
        run(source, interpreter, show_tokens, show_perror, filename, source_lines)
    except UnicodeDecodeError:
        print(f"{Colors.RED}错误:{Colors.END} 文件编码错误，请确保文件使用 UTF-8 编码保存")

def format_error(filename, line, message, token=None, source_lines=None):
    """格式化错误信息，提供更详细的错误上下文"""
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
    
    if source_lines:  # 确保有源代码行
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
        result += "2. 确保已导入包含该函数的模块\n"
        result += "3. 检查函数名的大小写是否正确\n"
    elif "缺少右括号" in message:
        result += "1. 添加缺少的右括号\n"
        result += "2. 检查括号是否匹配\n"
    elif "未定义的变量" in message:
        result += "1. 确保在使用变量前已经声明并赋值\n"
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

def run(source, interpreter, show_tokens=False, show_perror=False, filename="<stdin>", source_lines=None):
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        if show_tokens:
            for token in tokens:
                print(token)
        
        parser = Parser(tokens)
        try:
            ast = parser.parse()
        except ParserError as e:
            # 处理解析错误
            if source_lines is None:
                source_lines = source.splitlines()
            print(format_error(filename, e.token.line if e.token else 1, str(e), e.token, source_lines))
            return
        
        try:
            interpreter.interpret(ast)
        except InterpreterError as e:
            if hasattr(e, 'line'):
                if source_lines is None:
                    source_lines = source.splitlines()
                print(format_error(filename, e.line, e.message, e.token, source_lines))
            else:
                print(f"{Colors.RED}错误:{Colors.END} {e.message}")
            if show_perror:
                raise
    except (SyntaxError, ParserError) as e:
        # 处理语法错误
        if source_lines is None:
            source_lines = source.splitlines()
        if hasattr(e, 'token'):
            print(format_error(filename, e.token.line, str(e), e.token, source_lines))
        else:
            print(format_error(filename, 1, str(e), None, source_lines))
    except Exception as e:  # 处理其他错误
        if show_perror:
            raise
        print(format_error(filename, 1, str(e), None, source_lines))

def repl():
    print("BCC REPL (输入 'exit' 退出, 输入 'bcchelp' 显示帮助)")
    print("支持多行输入，输入空行结束，分号可以代替换行")
    interpreter = Interpreter()
    
    while True:
        try:
            # 收集多行输入
            lines = []
            while True:
                if not lines:
                    line = input('>> ')
                else:
                    line = input('... ')
                
                if line.strip() == 'exit':
                    return
                
                if line.strip() == 'bcchelp':
                    show_bcc_help()
                    lines = []  # 清空当前输入
                    break
                
                lines.append(line)
                
                # 检查是否需要继续输入
                if not line.strip():  # 空行
                    break
                elif line.strip().endswith('{'):  # 以 { 结尾需要继续
                    continue
                elif line.strip().endswith('}'):  # 以 } 结尾可以结束
                    break
                elif ';' in line:  # 包含分号可以结束
                    break
            
            if not lines:  # 如果没有输入，继续下一轮
                continue
                
            # 处理分号：将分号替换为换行符
            text = ' '.join(lines)
            text = text.replace(';', '\n')
            
            if text.strip():  # 如果有实际输入
                run(text, interpreter)
                
        except Exception as e:
            print(f"错误: {str(e)}")

def check_syntax(filename):
    """检查文件语法"""
    try:
        with open(filename, 'r') as f:
            source = f.read()
        
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        parser.parse()
        return True
    except Exception as e:
        print(str(e), file=sys.stderr)
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='BCC语言解释器')
    parser.add_argument('filename', nargs='?', help='要执行的源文件')
    parser.add_argument('--tokens', action='store_true', help='显示词法分析的token')
    parser.add_argument('--bcchelp', action='store_true', help='显示BCC语言的使用说明')
    parser.add_argument('--perror', action='store_true', help='显示Python错误堆栈')
    parser.add_argument('--check-syntax', action='store_true', help='只检查语法')
    
    args = parser.parse_args()
    
    if args.check_syntax:
        sys.exit(0 if check_syntax(args.filename) else 1)
    elif args.bcchelp:
        show_bcc_help()
    elif args.filename:
        run_file(args.filename, args.tokens, args.perror)
    else:
        repl() 