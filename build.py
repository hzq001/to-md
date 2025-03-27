#!/usr/bin/env python3
"""
to-md 二进制打包脚本

此脚本用于将to-md项目打包为独立的二进制可执行文件，
支持跨平台打包。
"""
import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path
import argparse
import site
import importlib.util

def print_colored(message, color_code):
    """打印彩色文本"""
    print(f"\033[{color_code}m{message}\033[0m")

def print_info(message):
    """打印信息消息"""
    print_colored(f"[INFO] {message}", "36")

def print_success(message):
    """打印成功消息"""
    print_colored(f"[SUCCESS] {message}", "32")

def print_error(message):
    """打印错误消息"""
    print_colored(f"[ERROR] {message}", "31")

def print_warning(message):
    """打印警告消息"""
    print_colored(f"[WARNING] {message}", "33")

def find_magika_models():
    """查找magika模型文件夹路径"""
    try:
        # 尝试找到magika模块的位置
        magika_spec = importlib.util.find_spec("magika")
        if not magika_spec or not magika_spec.origin:
            print_warning("无法找到magika模块路径")
            return None
        
        magika_path = os.path.dirname(magika_spec.origin)
        print_info(f"找到magika模块路径: {magika_path}")
        
        # 检查常见的模型路径
        models_paths = [
            os.path.join(magika_path, "models"),
            os.path.join(magika_path, "data", "models"),
            os.path.join(os.path.dirname(magika_path), "magika", "models"),
        ]
        
        # 遍历site-packages查找模型
        site_packages = site.getsitepackages()
        for site_pkg in site_packages:
            models_paths.append(os.path.join(site_pkg, "magika", "models"))
        
        for model_path in models_paths:
            if os.path.exists(model_path):
                if os.path.exists(os.path.join(model_path, "standard_v3_2")):
                    print_success(f"找到magika模型目录: {model_path}")
                    return model_path
        
        print_warning("未找到magika模型目录")
        return None
    except Exception as e:
        print_error(f"查找magika模型时出错: {str(e)}")
        return None

def check_dependencies():
    """检查必要的依赖是否已安装"""
    print_info("检查依赖...")
    
    # 检查PyInstaller是否可在命令行中执行
    try:
        result = subprocess.run(["pyinstaller", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print_info(f"PyInstaller {result.stdout.strip()} 已安装")
        else:
            print_error("PyInstaller 安装有问题，无法正常执行。")
            return False
    except FileNotFoundError:
        print_error("未找到 PyInstaller 命令。请确保已全局安装: pip install pyinstaller")
        return False
    
    try:
        from markitdown import MarkItDown
        print_info("MarkItDown 已安装")
    except ImportError:
        print_warning("未安装 MarkItDown 库。最终的二进制文件将需要用户自行安装 MarkItDown")
        print_info("推荐使用: pip install 'markitdown[all]~=0.1.0a1'")
        answer = input("是否继续打包? (y/n): ")
        if answer.lower() != 'y':
            return False
    
    return True

def clean_build_dir():
    """清理构建目录"""
    print_info("清理旧的构建文件...")
    build_dir = Path("build")
    dist_dir = Path("dist")
    
    if build_dir.exists():
        shutil.rmtree(build_dir)
        print_info("已删除 build 目录")
    
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
        print_info("已删除 dist 目录")

def update_spec_file():
    """更新 spec 文件以包含所有必要的依赖"""
    print_info("更新 to-md.spec 文件...")
    
    # 查找magika模型路径
    magika_models_path = find_magika_models()
    datas_content = ""
    
    if magika_models_path:
        model_dir = os.path.join(magika_models_path, "standard_v3_2")
        if os.path.exists(model_dir):
            # 将模型路径添加到datas中，确保在二进制中包含模型文件
            rel_path = os.path.relpath(magika_models_path)
            datas_content = f"""
    datas=[('{model_dir}', 'magika/models/standard_v3_2')],"""
            print_info(f"已添加magika模型路径: {model_dir}")
        else:
            print_warning(f"magika模型子目录standard_v3_2不存在")
    else:
        print_warning("未找到magika模型目录，可能会导致二进制文件运行失败")
    
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

hidden_imports = [
    'math',
    'multiprocessing',
    'multiprocessing.pool',
    'multiprocessing.managers',
    'multiprocessing.popen_spawn_posix',
    'multiprocessing.popen_fork',
    'multiprocessing.popen_spawn_win32',
    'multiprocessing.popen_forkserver',
    'multiprocessing.synchronize',
    'multiprocessing.heap',
    'multiprocessing.resource_tracker',
    'multiprocessing.spawn',
    'multiprocessing.util',
    'threading',
    'queue',
    'selectors',
    'logging',
    'typing',
    'markitdown',
    'openai',
    'click',
    'colorama',
    'tqdm',
    'docx',
    'docx2txt',
    'pypdf',
    'pptx',
    'openpyxl',
    'xlrd',
    'lxml',
    'html2text',
    'json',
    'csv',
    'zipfile',
    'PIL',
    'bs4',
    'exif',
    'markdown',
    'tempfile',
    'errno',
    'shutil',
    'datetime',
    're',
    'magika',
    'magika.types',
    'magika.models',
]

a = Analysis(
    ['to_md/cli.py'],
    pathex=[],
    binaries=[],{datas_content}
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='to-md',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
"""
    
    with open("to-md.spec", "w") as f:
        f.write(spec_content)
    
    print_info("to-md.spec 文件已更新")

def build_binary(args):
    """构建二进制可执行文件"""
    print_info("开始构建二进制文件...")
    
    # 构建命令
    cmd = ["pyinstaller", "to-md.spec"]
    
    if args.noupx:
        cmd.extend(["--noupx"])
    
    if args.exclude:
        for module in args.exclude.split(','):
            cmd.extend(["--exclude-module", module.strip()])
    
    # 执行打包命令
    print_info("执行命令: " + " ".join(cmd))
    result = subprocess.run(cmd, capture_output=False, text=True)
    
    if result.returncode != 0:
        print_error("构建失败！")
        return False
    
    print_success("构建成功！")
    return True

def copy_binary_to_path(args):
    """复制二进制文件到指定路径"""
    if not args.install:
        return
    
    print_info("复制二进制文件到可执行路径...")
    
    # 确定二进制文件路径
    if platform.system() == "Windows":
        binary_path = os.path.join("dist", "to-md.exe")
        install_path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "to-md")
    else:  # Linux 或 macOS
        binary_path = os.path.join("dist", "to-md")
        install_path = "/usr/local/bin"
    
    # 如果指定了安装路径，则使用指定路径
    if args.install_path:
        install_path = args.install_path
    
    if not os.path.exists(binary_path):
        print_error(f"二进制文件不存在: {binary_path}")
        return False
    
    if not os.path.exists(install_path):
        try:
            os.makedirs(install_path)
            print_info(f"创建目录: {install_path}")
        except Exception as e:
            print_error(f"无法创建目录: {install_path}, 错误: {str(e)}")
            return False
    
    try:
        if platform.system() == "Windows":
            dest_path = os.path.join(install_path, "to-md.exe")
            shutil.copy2(binary_path, dest_path)
        else:
            dest_path = os.path.join(install_path, "to-md")
            shutil.copy2(binary_path, dest_path)
            # 设置可执行权限
            os.chmod(dest_path, 0o755)
        
        print_success(f"已将二进制文件复制到: {dest_path}")
        
        # 在非Windows系统上检查PATH
        if platform.system() != "Windows" and install_path not in os.environ.get("PATH", "").split(":"):
            print_warning(f"安装路径 {install_path} 不在PATH环境变量中")
            print_info("您可能需要将其添加到您的PATH中，或使用绝对路径运行程序")
    
    except Exception as e:
        print_error(f"复制文件失败: {str(e)}")
        return False
    
    return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="to-md 打包工具")
    parser.add_argument("--clean", action="store_true", help="清理构建目录")
    parser.add_argument("--noupx", action="store_true", help="禁用UPX压缩")
    parser.add_argument("--exclude", type=str, help="排除指定模块，以逗号分隔")
    parser.add_argument("--install", action="store_true", help="安装到系统路径")
    parser.add_argument("--install-path", type=str, help="指定安装路径")
    
    args = parser.parse_args()
    
    print_info("=== to-md 二进制打包工具 ===")
    
    if not check_dependencies():
        sys.exit(1)
    
    if args.clean:
        clean_build_dir()
    
    # 更新spec文件
    update_spec_file()
    
    # 构建二进制文件
    if not build_binary(args):
        sys.exit(1)
    
    # 复制二进制文件到指定路径
    if args.install:
        if not copy_binary_to_path(args):
            sys.exit(1)
    
    # 打印使用信息
    binary_name = "to-md.exe" if platform.system() == "Windows" else "to-md"
    print_success(f"打包完成！二进制文件位于: dist/{binary_name}")
    print_info("使用方法: ")
    print_info(f"  dist/{binary_name} /path/to/source /path/to/output")
    print_info("查看帮助: ")
    print_info(f"  dist/{binary_name} --help")

if __name__ == "__main__":
    main() 