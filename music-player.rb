class MusicPlayer < Formula
  desc "精美的本地音乐播放器"
  homepage "https://github.com/ShubaoYang/music-player"
  url "https://github.com/ShubaoYang/music-player/archive/refs/tags/v0.1.tar.gz"
  sha256 "b77ec106766b70d3074e5945417ccbed3e4791f25f5827c50cb1cdf73b24c28c"
  license "MIT"

  depends_on "python@3.13"
  depends_on "sdl2"
  depends_on "sdl2_mixer"
  depends_on "sdl2_image"
  depends_on "sdl2_ttf"

  def install
    # 安装主程序
    libexec.install "music_player.py"
    libexec.install "requirements.txt" if File.exist?("requirements.txt")
    
    # 创建启动脚本
    (bin/"music-player").write <<~EOS
      #!/bin/bash
      
      # 检查并安装 Python 依赖
      if ! python3.13 -c "import PyQt5" 2>/dev/null; then
        echo "正在安装 Python 依赖..."
        python3.13 -m pip install --user PyQt5 pygame
      fi
      
      # 运行播放器
      exec python3.13 "#{libexec}/music_player.py" "$@"
    EOS
    
    chmod 0755, bin/"music-player"
  end

  def caveats
    <<~EOS
      首次运行时会自动安装 Python 依赖（PyQt5 和 pygame）。
      
      如果遇到问题，请手动安装依赖：
        python3.13 -m pip install PyQt5 pygame
      
      然后运行：
        music-player
    EOS
  end

  test do
    assert_predicate bin/"music-player", :exist?
    assert_predicate bin/"music-player", :executable?
    assert_predicate libexec/"music_player.py", :exist?
  end
end
