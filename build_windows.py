#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Student Management System - Windows Build Script for GitHub Actions
Simplified version to avoid encoding issues
"""

import os
import sys
import subprocess
import shutil

def main():
    print("=" * 50)
    print("Student Management System - Windows Build")
    print("=" * 50)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("PyInstaller installed successfully")
    
    # Clean previous build files
    print("\nCleaning old build files...")
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Cleaned directory: {dir_name}")
    
    # Remove old spec files
    spec_files = [f for f in os.listdir('.') if f.endswith('.spec')]
    for spec_file in spec_files:
        os.remove(spec_file)
        print(f"Cleaned file: {spec_file}")
    
    # PyInstaller command arguments
    cmd = [
        "pyinstaller",
        "--name=StudentManagementSystem",  # Use English name to avoid encoding issues
        "--onefile",
        "--windowed",
        "--add-data=ui.qml;.",
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtWidgets", 
        "--hidden-import=PyQt5.QtQml",
        "--hidden-import=PyQt5.QtQuick",
        "--hidden-import=sqlite3",
        "--hidden-import=json",
        "--hidden-import=datetime",
        "student_manager.py"
    ]
    
    # Remove icon parameter if icon file doesn't exist
    if not os.path.exists("icon.ico"):
        print("No icon.ico file found, using default icon")
    
    print(f"\nStarting build...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        # Execute build command
        result = subprocess.run(cmd, check=True)
        print("Build successful!")
        
        # Check output file
        exe_path = os.path.join("dist", "StudentManagementSystem.exe")
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print(f"Executable generated: {exe_path}")
            print(f"File size: {file_size:.1f} MB")
        else:
            print("Warning: exe file not found")
            
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("Build completed!")
    print("Generated files are in dist/ directory")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    main() 