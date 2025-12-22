class MusicPlayer < Formula
  include Language::Python::Virtualenv

  desc "精美的本地音乐播放器"
  homepage "https://github.com/yourusername/music-player"
  url "https://github.com/yourusername/music-player/archive/v1.0.0.tar.gz"
  sha256 "YOUR_SHA256_HASH_HERE"
  license "MIT"

  depends_on "python@3.13"
  depends_on "sdl2"
  depends_on "sdl2_mixer"
  depends_on "sdl2_image"
  depends_on "sdl2_ttf"

  resource "PyQt5" do
    url "https://files.pythonhosted.org/packages/PyQt5/PyQt5-5.15.10.tar.gz"
    sha256 "PYQT5_SHA256_HERE"
  end

  resource "pygame" do
    url "https://files.pythonhosted.org/packages/pygame/pygame-2.5.2.tar.gz"
    sha256 "PYGAME_SHA256_HERE"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system "#{bin}/music-player", "--version"
  end
end
