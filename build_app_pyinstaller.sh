#!/bin/bash

# 使用 PyInstaller 构建 macOS .app 应用

set -e

echo "🎵 音乐播放器 - PyInstaller 打包流程"
echo "================================"
echo ""

# 1. 检查并安装依赖
echo "📦 步骤 1/6: 检查依赖..."
if ! python3 -c "import PIL" 2>/dev/null; then
    echo "安装 Pillow..."
    pip3 install pillow
fi

if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "安装 PyInstaller..."
    pip3 install pyinstaller
fi

if ! python3 -c "import PyQt5" 2>/dev/null; then
    echo "安装 PyQt5..."
    pip3 install PyQt5
fi

if ! python3 -c "import pygame" 2>/dev/null; then
    echo "安装 pygame..."
    pip3 install pygame
fi

echo "✓ 依赖检查完成"
echo ""

# 2. 检查图标
echo "🎨 步骤 2/6: 检查应用图标..."
if [ ! -f "assets/icon.icns" ]; then
    echo "❌ 图标文件不存在: assets/icon.icns"
    echo "请先运行 python3 create_icon.py 生成图标"
    exit 1
fi
echo "✓ 图标文件存在"
echo ""

# 3. 清理之前的构建
echo "🧹 步骤 3/6: 清理旧文件..."
rm -rf build dist
echo "✓ 清理完成"
echo ""

# 4. 构建 App
echo "🔨 步骤 4/6: 构建应用..."
pyinstaller --noconfirm \
    --name="音乐播放器" \
    --windowed \
    --icon="assets/icon.icns" \
    --osx-bundle-identifier="com.shubaoyang.musicplayer" \
    --hidden-import=PyQt5.QtCore \
    --hidden-import=PyQt5.QtGui \
    --hidden-import=PyQt5.QtWidgets \
    --hidden-import=pygame \
    --exclude-module=PyQt5.QtBluetooth \
    --exclude-module=PyQt5.QtDBus \
    --exclude-module=PyQt5.QtDesigner \
    --exclude-module=PyQt5.QtHelp \
    --exclude-module=PyQt5.QtLocation \
    --exclude-module=PyQt5.QtMultimedia \
    --exclude-module=PyQt5.QtMultimediaWidgets \
    --exclude-module=PyQt5.QtNetwork \
    --exclude-module=PyQt5.QtNetworkAuth \
    --exclude-module=PyQt5.QtNfc \
    --exclude-module=PyQt5.QtOpenGL \
    --exclude-module=PyQt5.QtPositioning \
    --exclude-module=PyQt5.QtPrintSupport \
    --exclude-module=PyQt5.QtQml \
    --exclude-module=PyQt5.QtQuick \
    --exclude-module=PyQt5.QtQuickWidgets \
    --exclude-module=PyQt5.QtSensors \
    --exclude-module=PyQt5.QtSerialPort \
    --exclude-module=PyQt5.QtSql \
    --exclude-module=PyQt5.QtSvg \
    --exclude-module=PyQt5.QtTest \
    --exclude-module=PyQt5.QtWebChannel \
    --exclude-module=PyQt5.QtWebEngine \
    --exclude-module=PyQt5.QtWebEngineCore \
    --exclude-module=PyQt5.QtWebEngineWidgets \
    --exclude-module=PyQt5.QtWebSockets \
    --exclude-module=PyQt5.QtXml \
    --exclude-module=PyQt5.QtXmlPatterns \
    music_player.py

echo "✓ 应用构建完成"
echo ""

# 5. 创建 DMG 安装包
echo "📀 步骤 5/6: 创建 DMG 安装包..."
DMG_NAME="音乐播放器-v1.0.0.dmg"
rm -f "$DMG_NAME"

# 创建临时目录用于 DMG
DMG_TEMP="dmg_temp"
rm -rf "$DMG_TEMP"
mkdir -p "$DMG_TEMP"

# 复制 App 到临时目录
cp -R "dist/音乐播放器.app" "$DMG_TEMP/"

# 创建 Applications 快捷方式
ln -s /Applications "$DMG_TEMP/Applications"

# 创建 DMG
hdiutil create -volname "音乐播放器" \
    -srcfolder "$DMG_TEMP" \
    -ov \
    -format UDZO \
    "$DMG_NAME"

# 清理临时目录
rm -rf "$DMG_TEMP"

echo "✓ DMG 创建完成"
echo ""

# 6. 完成
echo "✅ 步骤 6/6: 打包完成！"
echo "================================"
echo ""
echo "📦 生成的文件："
echo "  • dist/音乐播放器.app  - macOS 应用"
echo "  • $DMG_NAME - 安装包"
echo ""
echo "🚀 使用方法："
echo "  1. 双击 dist/音乐播放器.app 直接运行"
echo "  2. 双击 $DMG_NAME 打开安装包"
echo "  3. 拖动应用到 Applications 文件夹安装"
echo ""
echo "📤 分发："
echo "  • 分享 $DMG_NAME 给其他用户"
echo "  • 上传到 GitHub Releases"
echo ""
