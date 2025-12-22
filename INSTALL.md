# 通过 Homebrew 分发音乐播放器指南

## 步骤 1: 准备项目

1. **创建 GitHub 仓库**
   - 在 GitHub 上创建一个新仓库（例如：`yourusername/music-player`）
   - 将所有代码推送到仓库

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/music-player.git
git push -u origin main
```

2. **创建发布版本**
   - 在 GitHub 上创建一个 Release（例如：v1.0.0）
   - 下载生成的 tar.gz 文件
   - 计算 SHA256 哈希值：

```bash
shasum -a 256 music-player-1.0.0.tar.gz
```

## 步骤 2: 更新 Homebrew Formula

编辑 `music-player.rb` 文件：
- 将 `homepage` 和 `url` 改为你的 GitHub 仓库地址
- 将 `sha256` 替换为上一步计算的哈希值
- 更新 PyQt5 和 pygame 的资源 URL 和 SHA256

## 步骤 3: 创建 Homebrew Tap

1. **创建 Tap 仓库**

在 GitHub 上创建一个名为 `homebrew-tap` 的仓库（必须以 `homebrew-` 开头）

2. **添加 Formula**

```bash
git clone https://github.com/yourusername/homebrew-tap.git
cd homebrew-tap
mkdir Formula
cp /path/to/music-player.rb Formula/
git add Formula/music-player.rb
git commit -m "Add music-player formula"
git push
```

## 步骤 4: 用户安装方式

其他用户可以通过以下命令安装：

```bash
# 添加你的 tap
brew tap yourusername/tap

# 安装音乐播放器
brew install music-player

# 运行
music-player
```

## 步骤 5: 更新和维护

当你发布新版本时：

1. 在 GitHub 上创建新的 Release
2. 更新 Formula 中的版本号和 SHA256
3. 推送到 homebrew-tap 仓库

用户更新：
```bash
brew update
brew upgrade music-player
```

## 测试 Formula

在发布前测试你的 Formula：

```bash
# 本地测试安装
brew install --build-from-source ./music-player.rb

# 审计 Formula
brew audit --strict music-player

# 测试 Formula
brew test music-player
```

## 注意事项

- Formula 文件名必须与类名匹配（kebab-case vs PascalCase）
- 确保所有依赖都正确声明
- SHA256 哈希值必须准确
- 测试在干净的环境中安装
