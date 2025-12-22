# 🎵 本地音乐播放器

一个使用 Python + PyQt5 + Pygame 开发的精美桌面音乐播放器。

## ✨ 特性

- 🎨 精美的深色主题界面
- 🎵 支持 MP3、WAV、OGG、FLAC 等多种音频格式
- 📁 支持添加单个文件或整个文件夹
- 📝 播放列表管理
- ⏯️ 完整的播放控制（播放/暂停/停止/上一首/下一首）
- 🔊 音量调节
- 💾 自动保存播放列表和设置
- 🖱️ 双击播放列表项目即可播放
- 🔄 自动播放下一首

## 🚀 安装

### 方式 1: 手动安装

1. 安装系统依赖：
```bash
brew install sdl2 sdl2_mixer sdl2_image sdl2_ttf python@3.13
```

2. 安装 Python 依赖：
```bash
pip install -r requirements.txt
```

3. 运行播放器：
```bash
python music_player.py
```

### 方式 2: 通过 Homebrew Tap

```bash
brew tap yourusername/tap
brew install music-player
music-player
```

详细发布步骤请查看 [INSTALL.md](INSTALL.md)

## 🎮 使用方法

1. **添加音乐**：
   - 点击"➕ 添加音乐"按钮，选择音频文件
   - 点击"📁 添加文件夹"按钮，选择包含音乐的文件夹（会自动扫描子文件夹）

2. **播放音乐**：
   - 点击"▶ 播放"按钮播放当前选中的音乐
   - 双击播放列表中的歌曲直接播放

3. **控制播放**：
   - ⏮ 上一首：播放上一首歌曲
   - ▶/⏸ 播放/暂停：播放或暂停当前音乐
   - ⏭ 下一首：播放下一首歌曲
   - ⏹ 停止：停止播放

4. **调节音量**：拖动音量滑块

5. **清空列表**：点击"🗑 清空列表"按钮

## 🎨 界面预览

- 深色主题配色（深蓝 + 粉红色调）
- 简洁现代的按钮设计
- 清晰的播放信息显示
- 友好的播放列表界面

## 📝 配置文件

播放器会自动在当前目录生成 `music_player_config.json` 配置文件，保存：
- 播放列表
- 音量设置

## 🔧 技术栈

- Python 3.7+
- PyQt5（GUI 界面）
- Pygame（音频播放）
- SDL2（音频后端）

## 📦 发布到 Homebrew

详细步骤请查看 [INSTALL.md](INSTALL.md)

## 📄 许可

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
