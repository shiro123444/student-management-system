#!/bin/bash
# 学生管理系统 - Mac打包脚本

echo "================================================"
echo "学生管理系统 - Mac快速打包工具"
echo "================================================"

# 检查是否在Mac系统上运行
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "⚠️  警告: 此脚本需要在Mac系统上运行!"
    exit 1
fi

echo "正在执行Mac打包..."

# 执行打包命令
pyinstaller \
    --name="学生管理系统" \
    --onefile \
    --windowed \
    --add-data="ui.qml:." \
    --hidden-import=PyQt5.QtCore \
    --hidden-import=PyQt5.QtWidgets \
    --hidden-import=PyQt5.QtQml \
    --hidden-import=PyQt5.QtQuick \
    --target-arch=universal2 \
    student_manager.py

echo ""
echo "打包完成！"
echo "生成的.app文件位于 dist/ 目录中"
echo "可以拖拽到 Applications 文件夹使用"
echo "" 