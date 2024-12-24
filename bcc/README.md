# BCC Language Support / BCC 语言支持

VSCode extension for the BCC programming language.
BCC 编程语言的 VSCode 扩展。

## Features / 功能特性

* Syntax highlighting for BCC source files (.bcs, .bcm)
  BCC 源文件的语法高亮（.bcs, .bcm）
* Code completion for / 代码补全支持：
  - Keywords (if, for, while, def, public, private, return, nsreturn, expr)
    关键字 (if, for, while, def, public, private, return, nsreturn, expr)
  - Built-in functions (print, printnln, max, min, concat, forEach)
    内置函数 (print, printnln, max, min, concat, forEach)
  - Operators and expressions
    运算符和表达式
* Code snippets for common patterns
  常用代码片段
* Syntax checking on save
  保存时进行语法检查

## Language Features / 语言特性

### Basic Syntax / 基本语法

### Functions

### Classes

## Code Snippets

* `if` - Creates an if statement
* `for` - Creates a for loop
* `print` - Creates a print statement
* `println` - Creates a println statement

## Example

```bcs
// Comments / 注释
x = 5 // Variable assignment / 变量赋值
// Print statements / 打印��句
print("Hello") // Print without newline / 不换行打印
printnln("World") // Print with newline / 换行打印
// Control structures / 控制结构
if(x > 3) {
print("x is greater than 3")
}
while(x < 10) {
x = x + 1
}
```

### Functions / 函数

```bcs
// Function definition / 函数定义
def public add(x, y) {
return x + y
}
// Private function / 私有函数
def private helper() {
print("This is a helper function")
}
```

### Code Blocks / 代码块

```bcs
// Code block with forEach / 使用 forEach 的代码块
forEach {
print("Inside code block")
}
```
## Code Snippets / 代码片段

* `if` - Creates an if statement / 创建 if 语句
* `for` - Creates a for loop / 创建 for 循环
* `while` - Creates a while loop / 创建 while 循环
* `print` - Creates a print statement / 创建打印语句
* `printnln` - Creates a println statement / 创建换行打印语句
* `def` - Creates a function definition / 创建函数定义

## Installation / 安装

1. Open VSCode / 打开 VSCode
2. Install the BCC extension / 安装 BCC 扩展
3. Create or open a .bcs file / 创建或打开 .bcs 文件
4. Start coding! / 开始编码！

### Windows
1. 下载 bcc-windows.zip
2. 解压到任意目录
3. 将 bcc.exe 所在目录添加到系统环境变量 PATH 中
4. 打开命令提示符，输入 `bcc --help` 验证安装

### 从源码安装
1. Clone 仓库
2. 安装依赖：`pip install -r requirements.txt`
3. 运行：`python main.py your_script.bcs`

## Configuration / 配置

The extension supports the following settings / 扩展支持以下设置：

* `bcc.enableSyntaxValidation`: Enable/disable syntax validation / 启用/禁用语法验证
* `bcc.formatOnSave`: Enable/disable format on save / 启用/禁用保存时格式化

## Support / 支持

For issues and feature requests, please visit:
如有问题或功能建议，请访问：
[GitHub BCC Web](https://dhjs0000.github.io/bcc/index.html)
