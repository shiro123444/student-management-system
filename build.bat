@echo off
chcp 65001 >nul
echo ================================================
echo 学生管理系统 - 快速打包工具
echo ================================================

echo 正在执行打包...
pyinstaller --name="学生管理系统" --onefile --windowed --add-data="ui.qml;." --hidden-import=PyQt5.QtCore --hidden-import=PyQt5.QtWidgets --hidden-import=PyQt5.QtQml --hidden-import=PyQt5.QtQuick student_manager.py

echo.
echo 打包完成！
echo 生成的exe文件位于 dist\ 目录中
echo.
pause 