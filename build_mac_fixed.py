#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Student Management System - Mac Build Script for GitHub Actions
Simplified version to avoid encoding issues
"""

import os
import sys
import subprocess
import shutil

def main():
    print("=" * 50)
    print("Student Management System - Mac Build")
    print("=" * 50)
    
    # Check if running on Mac
    if sys.platform != 'darwin':
        print("Warning: This script should run on Mac system!")
        print("Current system:", sys.platform)
        return False
    
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
    
    # PyInstaller command arguments - Mac version
    cmd = [
        "pyinstaller",
        "--name=StudentManagementSystem",  # Use English name
        "--onedir",  # Use onedir for Mac apps
        "--windowed",  # No console window
        "--add-data=ui.qml:.",  # Mac uses colon separator
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtWidgets", 
        "--hidden-import=PyQt5.QtQml",
        "--hidden-import=PyQt5.QtQuick",
        "--hidden-import=sqlite3",
        "--hidden-import=json",
        "--hidden-import=datetime",
        "student_manager.py"  # Main program file
    ]
    
    # Check for icon file (Mac uses .icns format)
    if os.path.exists("icon.icns"):
        cmd.insert(-1, "--icon=icon.icns")
        print("Found Mac icon file: icon.icns")
    else:
        print("No icon.icns file found, using default icon")
    
    print(f"\nStarting build...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        # Execute build command
        result = subprocess.run(cmd, check=True)
        print("Build successful!")
        
        # Check output file
        app_path = os.path.join("dist", "StudentManagementSystem.app")
        if os.path.exists(app_path):
            print(f"Mac app generated: {app_path}")
            
            # Get app size
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(app_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
            
            app_size = total_size / (1024 * 1024)  # MB
            print(f"App size: {app_size:.1f} MB")
        else:
            print("Warning: .app file not found")
            
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("Mac build completed!")
    print("Generated .app is in dist/ directory")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    main() 