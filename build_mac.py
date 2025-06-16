#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
学生管理系统 - Mac打包脚本
在Mac系统上运行此脚本来生成.app应用
"""

import os
import sys
import subprocess
import shutil

def main():
    print("=" * 50)
    print("学生管理系统 - Mac打包工具")
    print("=" * 50)
    
    # 检查是否在Mac系统上运行
    if sys.platform != 'darwin':
        print("⚠️  警告: 此脚本需要在Mac系统上运行!")
        print("当前系统:", sys.platform)
        return False
    
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
    
    # PyInstaller命令参数 - Mac版本
    cmd = [
        "pyinstaller",
        "--name=学生管理系统",  # 应用程序名称
        "--onefile",  # 打包成单个文件
        "--windowed",  # 不显示控制台窗口
        "--add-data=ui.qml:.",  # Mac使用冒号分隔符
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtWidgets", 
        "--hidden-import=PyQt5.QtQml",
        "--hidden-import=PyQt5.QtQuick",
        "--hidden-import=sqlite3",
        "--hidden-import=json",
        "--hidden-import=datetime",
        "--target-arch=universal2",  # 支持Intel和Apple Silicon
        "student_manager.py"  # 主程序文件
    ]
    
    # 如果有图标文件（Mac使用.icns格式）
    if os.path.exists("icon.icns"):
        cmd.insert(-1, "--icon=icon.icns")
        print("✓ 找到Mac图标文件: icon.icns")
    else:
        print("⚠ 未找到icon.icns文件，将使用默认图标")
    
    print(f"\n开始打包...")
    print(f"执行命令: {' '.join(cmd)}")
    
    try:
        # 执行打包命令
        result = subprocess.run(cmd, check=True)
        print("✓ 打包成功！")
        
        # 检查输出文件
        app_path = os.path.join("dist", "学生管理系统.app")
        if os.path.exists(app_path):
            print(f"✓ Mac应用已生成: {app_path}")
            
            # 获取应用大小
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(app_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    total_size += os.path.getsize(filepath)
            
            app_size = total_size / (1024 * 1024)  # MB
            print(f"✓ 应用大小: {app_size:.1f} MB")
        else:
            print("⚠ 未找到生成的.app文件")
            
    except subprocess.CalledProcessError as e:
        print(f"✗ 打包失败: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("Mac打包完成！")
    print("生成的.app应用位于 dist/ 目录中")
    print("可以直接拖拽到Applications文件夹使用")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    main() 