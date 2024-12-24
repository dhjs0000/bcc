from enum import Enum, auto

class TokenType(Enum):
    # 数据类型
    NUMBER = auto()      # 数字
    STRING = auto()      # 字符串
    IDENTIFIER = auto()  # 标识符（变量名）
    
    # 运算符
    PLUS = auto()       # +
    MINUS = auto()      # -
    MULTIPLY = auto()   # *
    DIVIDE = auto()     # /
    EQUALS = auto()     # =
    
    # 比较运算符
    EQ = auto()         # ==
    LT = auto()         # <
    GT = auto()         # >
    LE = auto()         # <=
    GE = auto()         # >=
    
    # 括号和其他符号
    LPAREN = auto()     # (
    RPAREN = auto()     # )
    COLON = auto()      # :
    
    # 关键字
    PRINT = auto()      # print 关键字
    PRINTNLN = auto()   # printnln 关键字（不换行打印）
    IF = auto()         # if 关键字
    FOR = auto()        # for 关键字
    WHILE = auto()      # while 关键字
    RETURN = auto()     # return 关键字
    NSRETURN = auto()   # nsreturn 关键字（不停止的返回）
    EXPR = auto()       # expr 关键字
    
    # 特殊标记
    EOF = auto()        # 文件结束标记
    INDENT = auto()     # 缩进
    DEDENT = auto()     # 取消缩进
    LBRACE = '{'    # 左大括号
    RBRACE = '}'    # 右大括号
    COMMA = auto()      # ,
    SEMICOLON = auto()  # 分号 ;
    
    # 函数相关
    DEF = auto()        # def 关键字
    PUBLIC = auto()     # public 关键字
    PRIVATE = auto()    # private 关键字
    
    # 类相关
    CLASS = auto()      # class 关键字
    
    # 代码块相关
    CODEBLOCK = auto()   # BCC.Codeblock 类型
    DOT = auto()         # . 符号，用于 BCC.Codeblock.lines
    
    # 模块相关
    IMPORT = auto()      # import 关键字
    FROM = auto()        # from 关键字
    AS = auto()         # as 关键字
    BCM = auto()        # .bcm 模块文件
    BCS = auto()        # .bcs 源文件
    
    # 数组相关
    LBRACKET = auto()    # [
    RBRACKET = auto()    # ]

class Token:
    def __init__(self, type, value, line=0, column=0):
        self.type = type      # token 类型
        self.value = value    # token 值
        self.line = line      # 行号
        self.column = column  # 列号

    def __str__(self):
        return f'Token({self.type}, {self.value}, line={self.line}, col={self.column})' 