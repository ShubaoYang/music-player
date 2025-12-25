#!/bin/bash

# 使用 PyInstaller 构建新版音乐播放器 macOS .app 应用

set -e

echo "🎵 音乐播放器 v2.0 - PyInstaller 打包流程"
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

# 安装所有依赖
pip3 install -r requirements.txt

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
    --hidden-import=PySide6.QtCore \
    --hidden-import=PySide6.QtGui \
    --hidden-import=PySide6.QtWidgets \
    --hidden-import=soundfile \
    --hidden-import=sounddevice \
    --hidden-import=numpy \
    --hidden-import=mutagen \
    --hidden-import=mutagen.mp3 \
    --hidden-import=mutagen.flac \
    --hidden-import=mutagen.oggvorbis \
    --hidden-import=music_player \
    --hidden-import=music_player.models \
    --hidden-import=music_player.models.playback_engine \
    --hidden-import=music_player.models.playlist_manager \
    --hidden-import=music_player.models.config_manager \
    --hidden-import=music_player.models.metadata_reader \
    --hidden-import=music_player.models.track \
    --hidden-import=music_player.models.playback_mode \
    --hidden-import=music_player.views \
    --hidden-import=music_player.views.main_window \
    --hidden-import=music_player.views.mini_window \
    --hidden-import=music_player.views.control_panel \
    --hidden-import=music_player.views.playlist_view \
    --hidden-import=music_player.views.system_tray \
    --hidden-import=music_player.controllers \
    --hidden-import=music_player.controllers.player_controller \
    --hidden-import=music_player.utils \
    --hidden-import=music_player.utils.logger \
    --collect-all=music_player \
    --collect-all=soundfile \
    --collect-all=sounddevice \
    --copy-metadata=soundfile \
    --copy-metadata=sounddevice \
    --exclude-module=PySide6.QtBluetooth \
    --exclude-module=PySide6.QtDBus \
    --exclude-module=PySide6.QtDesigner \
    --exclude-module=PySide6.QtHelp \
    --exclude-module=PySide6.QtLocation \
    --exclude-module=PySide6.QtMultimedia \
    --exclude-module=PySide6.QtMultimediaWidgets \
    --exclude-module=PySide6.QtNetwork \
    --exclude-module=PySide6.QtNetworkAuth \
    --exclude-module=PySide6.QtNfc \
    --exclude-module=PySide6.QtOpenGL \
    --exclude-module=PySide6.QtPositioning \
    --exclude-module=PySide6.QtPrintSupport \
    --exclude-module=PySide6.QtQml \
    --exclude-module=PySide6.QtQuick \
    --exclude-module=PySide6.QtQuickWidgets \
    --exclude-module=PySide6.QtSensors \
    --exclude-module=PySide6.QtSerialPort \
    --exclude-module=PySide6.QtSql \
    --exclude-module=PySide6.QtSvg \
    --exclude-module=PySide6.QtTest \
    --exclude-module=PySide6.QtWebChannel \
    --exclude-module=PySide6.QtWebEngine \
    --exclude-module=PySide6.QtWebEngineCore \
    --exclude-module=PySide6.QtWebEngineWidgets \
    --exclude-module=PySide6.QtWebSockets \
    --exclude-module=PySide6.QtXml \
    --exclude-module=PySide6.QtXmlPatterns \
    --exclude-module=PyQt5 \
    --exclude-module=PyQt6 \
    --exclude-module=tkinter \
    --exclude-module=matplotlib \
    --exclude-module=PIL.ImageQt \
    --exclude-module=unittest \
    --exclude-module=test \
    --exclude-module=hypothesis \
    --exclude-module=pytest \
    --strip \
    music_player_app.py

echo "✓ 应用构建完成"
echo ""

# 4.5. 清理不必要的文件以减小体积
echo "🗜️  步骤 4.5/6: 优化应用体积..."
APP_PATH="dist/音乐播放器.app"

# 删除不需要的 Qt 翻译文件（保留中文和英文）
find "$APP_PATH" -name "qt_*.qm" ! -name "qt_zh*.qm" ! -name "qt_en*.qm" -delete 2>/dev/null || true

# 删除 Qt 文档
find "$APP_PATH" -type d -name "doc" -exec rm -rf {} + 2>/dev/null || true

# 删除测试文件
find "$APP_PATH" -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
find "$APP_PATH" -type d -name "test" -exec rm -rf {} + 2>/dev/null || true

# 删除示例文件
find "$APP_PATH" -type d -name "examples" -exec rm -rf {} + 2>/dev/null || true

# 删除 .pyc 缓存文件
find "$APP_PATH" -name "*.pyc" -delete 2>/dev/null || true
find "$APP_PATH" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# 显示最终大小
APP_SIZE=$(du -sh "$APP_PATH" | cut -f1)
echo "✓ 优化完成，应用大小: $APP_SIZE"
echo ""

# 5. 创建 DMG 安装包
echo "📀 步骤 5/6: 创建 DMG 安装包..."
DMG_NAME="音乐播放器-v0.2.dmg"
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
hdiutil create -volname "音乐播放器 v2.0" \
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
echo "  1. 直接运行: open dist/音乐播放器.app"
echo "  2. 调试运行: ./run_with_log.sh"
echo "  3. 安装: 双击 $DMG_NAME"
echo ""
echo "� 如果应用闪退："
echo "  1. 运行: ./run_with_log.sh"
echo "  2. 查看日志: cat app_crash.log"
echo "  3. 或直接运行: dist/音乐播放器.app/Contents/MacOS/音乐播放器"
echo ""
echo "📤 分发："
echo "  • 分享 $DMG_NAME 给其他用户"
echo "  • 上传到 GitHub Releases"
echo ""
echo "🎉 新功能："
echo "  • 可拖动进度条"
echo "  • 多种播放模式（顺序/循环/随机/单曲）"
echo "  • 搜索过滤播放列表"
echo "  • 显示歌曲元数据和封面"
echo "  • 保存/加载播放列表"
echo "  • 键盘快捷键支持"
echo "  • 系统托盘支持"
echo "  • 迷你模式（v0.3 新增）"
echo "  • 模块化架构"
echo ""
