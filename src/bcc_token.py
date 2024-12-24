from enum import Enum

class TokenType(Enum):
    # 数据类型
    NUMBER = 1      # 数字
    STRING = 2      # 字符串
    IDENTIFIER = 3  # 标识符（变量名）
    
    # 运算符
    PLUS = 4       # +
    MINUS = 5      # -
    MULTIPLY = 6   # *
    DIVIDE = 7     # /
    EQUALS = 8     # =
    
    # 比较运算符
    EQ = 9         # ==
    LT = 10        # <
    GT = 11        # >
    LE = 12        # <=
    GE = 13        # >=
    
    # 括号和其他符号
    LPAREN = 14     # (
    RPAREN = 15     # )
    COLON = 16      # :
    
    # 关键字
    PRINT = 17      # print 关键字
    PRINTNLN = 18   # printnln 关键字（不换行打印）
    IF = 19         # if 关键字
    FOR = 20        # for 关键字
    WHILE = 21      # while 关键字
    RETURN = 22     # return 关键字
    NSRETURN = 23   # nsreturn 关键字（不停止的返回）
    EXPR = 24       # expr 关键字
    
    # 特殊标记
    EOF = 25        # 文件结束标记
    INDENT = 26     # 缩进
    DEDENT = 27     # 取消缩进
    LBRACE = 28     # 左大括号
    RBRACE = 29     # 右大括号
    COMMA = 30      # ,
    SEMICOLON = 31  # 分号 ;
    
    # 函数相关
    DEF = 32        # def 关键字
    PUBLIC = 33     # public 关键字
    PRIVATE = 34    # private 关键字
    
    # 类相关
    CLASS = 35      # class 关键字
    
    # 代码块相关
    CODEBLOCK = 36   # BCC.Codeblock 类型
    DOT = 37         # . 符号，用于 BCC.Codeblock.lines
    
    # 模块相关
    IMPORT = 38      # import 关键字
    FROM = 39        # from 关键字
    AS = 40          # as 关键字
    BCM = 41         # .bcm 模块文件
    BCS = 42         # .bcs 源文件
    
    # 数组相关
    LBRACKET = 43    # [
    RBRACKET = 44    # ]

class Token:
    def __init__(self, type, value, line=0, column=0):
        self.type = type      # token 类型
        self.value = value    # token 值
        self.line = line      # 行号
        self.column = column  # 列号

    def __str__(self):
        return f'Token({self.type}, {self.value}, line={self.line}, col={self.column})' 