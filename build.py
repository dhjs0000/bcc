import os
import shutil
import PyInstaller.__main__
import sys

def build_exe():
    # 清理旧的构建文件
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # 检查必要文件是否存在
    required_files = ['main.py', 'lib/bcc/basicDef.bcm', 'lib/bcc/config.json']
    for file in required_files:
        if not os.path.exists(file):
            print(f"错误: 找不到必要文件 {file}")
            sys.exit(1)
    
    # 使用 PyInstaller 打包
    PyInstaller.__main__.run([
        'main.py',                    # 主程序文件
        '--name=bcc',                 # 生成的exe名称
        '--onefile',                  # 打包成单个文件
        '--console',                  # 控制台应用
        # 添加需要包含的数据文件
        '--add-data=lib/bcc;lib/bcc', # 添加基础库文件
        '--clean',                    # 清理临时文件
        '--noconfirm'                 # 不询问确认
    ])
    
    # 创建发布包目录
    release_dir = 'dist/bcc-release'
    os.makedirs(release_dir, exist_ok=True)
    
    print("正在创建发布包...")
    
    # 复制必要的文件到发布包
    shutil.copy('dist/bcc.exe', release_dir)
    shutil.copytree('lib', f'{release_dir}/lib', dirs_exist_ok=True)
    
    # 复制文档文件（如果存在）
    for doc_file in ['README.md', 'LICENSE']:
        if os.path.exists(doc_file):
            shutil.copy(doc_file, release_dir)
    
    # 创建示例目录
    examples_dir = f'{release_dir}/examples'
    os.makedirs(examples_dir, exist_ok=True)
    example_count = 0
    for example in os.listdir('examples'):
        if example.endswith('.bcs'):
            shutil.copy(f'examples/{example}', examples_dir)
            example_count += 1
    print(f"已复制 {example_count} 个示例文件")
    
    # 创建 zip 文件
    print("正在创建压缩包...")
    shutil.make_archive('dist/bcc-windows', 'zip', release_dir)
    
    print(f"\n打包完成！")
    print(f"发布包位置: {os.path.abspath('dist/bcc-windows.zip')}")

if __name__ == '__main__':
    try:
        build_exe()
    except Exception as e:
        print(f"打包过程出错: {str(e)}")
        sys.exit(1) 