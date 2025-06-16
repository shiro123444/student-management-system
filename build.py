#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生管理系统打包脚本
使用PyInstaller将Python程序打包成exe文件
"""

import os
import sys
import subprocess
import shutil

def main():
    print("=" * 50)
    print("学生管理系统 - 自动打包工具")
    print("=" * 50)
    
    # 检查PyInstaller是否安装
    try:
        import PyInstaller
        print(f"✓ PyInstaller版本: {PyInstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✓ PyInstaller安装完成")
    
    # 清理之前的构建文件
    print("\n清理旧的构建文件...")
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✓ 清理目录: {dir_name}")
    
    # 删除旧的spec文件
    spec_files = [f for f in os.listdir('.') if f.endswith('.spec')]
    for spec_file in spec_files:
        os.remove(spec_file)
        print(f"✓ 清理文件: {spec_file}")
    
    # PyInstaller命令参数
    cmd = [
        "pyinstaller",
        "--name=学生管理系统",  # 应用程序名称
        "--onefile",  # 打包成单个文件
        "--windowed",  # 不显示控制台窗口
        "--icon=icon.ico",  # 应用图标（如果有的话）
        "--add-data=ui.qml;.",  # 包含QML文件
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtWidgets", 
        "--hidden-import=PyQt5.QtQml",
        "--hidden-import=PyQt5.QtQuick",
        "--hidden-import=sqlite3",
        "--hidden-import=json",
        "--hidden-import=datetime",
        "student_manager.py"  # 主程序文件
    ]
    
    # 如果没有图标文件，移除图标参数
    if not os.path.exists("icon.ico"):
        cmd = [arg for arg in cmd if not arg.startswith("--icon")]
        print("⚠ 未找到icon.ico文件，将使用默认图标")
    
    print(f"\n开始打包...")
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        # 执行打包命令
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8')
        print("✓ 打包成功！")
        
        # 检查输出文件
        exe_path = os.path.join("dist", "学生管理系统.exe")
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print(f"✓ 可执行文件已生成: {exe_path}")
            print(f"✓ 文件大小: {file_size:.1f} MB")
        else:
            print("⚠ 未找到生成的exe文件")
            
    except subprocess.CalledProcessError as e:
        print(f"✗ 打包失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False
    
    print("\n" + "=" * 50)
    print("打包完成！")
    print("生成的文件位于 dist/ 目录中")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    main() 