# 🚀 GitHub Actions 自动打包教程

使用GitHub的免费云服务，自动为你的程序同时生成Windows和Mac版本！

## 📋 准备工作

### 1. 创建GitHub账号
如果还没有，请到 https://github.com 注册账号

### 2. 创建新仓库
1. 登录GitHub
2. 点击右上角 "+" → "New repository"
3. 填写仓库名：`student-management-system`
4. 选择 "Public"（公开，免费用户只能用公开仓库的Actions）
5. 点击 "Create repository"

## 🔧 上传代码到GitHub

### 方法一：使用命令行（推荐）

在你的项目目录下执行：

```bash
# 1. 添加所有文件
git add .

# 2. 提交代码
git commit -m "学生管理系统初始版本"

# 3. 连接到GitHub仓库（替换成你的用户名和仓库名）
git remote add origin https://github.com/你的用户名/student-management-system.git

# 4. 推送代码
git push -u origin main
```

### 方法二：使用GitHub Desktop
1. 下载GitHub Desktop：https://desktop.github.com/
2. 登录你的GitHub账号
3. 选择 "Add an Existing Repository from your Hard Drive"
4. 选择你的项目文件夹
5. 点击 "Publish repository"

## ⚡ 触发自动打包

### 自动触发（推荐）
```bash
# 创建版本标签，会自动触发打包
git tag v1.0.0
git push origin v1.0.0
```

### 手动触发
1. 进入你的GitHub仓库页面
2. 点击 "Actions" 标签
3. 选择 "构建多平台exe/app" 工作流
4. 点击 "Run workflow" → "Run workflow"

## 📦 下载打包结果

### 查看构建状态
1. 在GitHub仓库页面点击 "Actions"
2. 可以看到构建进程（通常需要5-15分钟）
3. 绿色✅表示成功，红色❌表示失败

### 下载文件
构建完成后有两种下载方式：

**方法1：下载Artifacts（临时文件）**
1. 点击完成的构建任务
2. 向下滚动到 "Artifacts" 部分
3. 下载：
   - `学生管理系统-Windows`（包含.exe文件）
   - `学生管理系统-macOS`（包含.app文件）

**方法2：正式发布版本（永久文件）**
如果你使用标签触发构建，会自动创建Release：
1. 在仓库页面点击 "Releases"
2. 下载对应平台的文件

## 🔍 文件说明

下载后你会得到：
- **Windows版本**: `学生管理系统.exe`（50MB左右）
- **Mac版本**: `学生管理系统.app`（50MB左右）

## 🛠️ 故障排除

### 构建失败怎么办？
1. 点击失败的构建任务
2. 查看错误日志
3. 常见问题：
   - 依赖安装失败：检查requirements.txt
   - QML文件路径错误：确保ui.qml在根目录
   - 权限问题：确保仓库是public

### 如何更新版本？
```bash
# 修改代码后
git add .
git commit -m "修复问题"
git push

# 创建新版本标签
git tag v1.0.1
git push origin v1.0.1
```

## 💡 高级技巧

### 自定义构建参数
编辑 `.github/workflows/build.yml` 文件来自定义：
- Python版本
- 依赖包
- 打包参数
- 发布说明

### 添加图标
- Windows: 将 `icon.ico` 放在根目录
- Mac: 将 `icon.icns` 放在根目录

### 私有仓库
如果你有GitHub Pro账号，可以使用私有仓库，同样支持Actions。

## 🎉 总结

使用GitHub Actions的优势：
- ✅ **完全免费**（每月2000分钟）
- ✅ **自动化**（推送代码自动打包）
- ✅ **多平台**（同时生成Windows和Mac版本）
- ✅ **云端构建**（不占用本地资源）
- ✅ **版本管理**（每个版本都有对应的安装包）

现在你可以轻松地为Mac用户提供原生应用了！🚀 