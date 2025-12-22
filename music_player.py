import sys
import os
import json
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QListWidget, QLabel, 
                             QSlider, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from pygame import mixer
import time

class MusicPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🎵 音乐播放器")
        self.setGeometry(100, 100, 800, 600)
        
        # 设置深色主题
        self.set_dark_theme()
        
        # 初始化 pygame mixer
        mixer.init()
        
        # 播放列表
        self.playlist_paths = []
        self.current_index = -1
        self.is_playing = False
        self.is_paused = False
        
        # 创建界面
        self.init_ui()
        
        # 加载配置
        self.load_config()
        
        # 设置音量
        mixer.music.set_volume(0.7)
        
        # 定时器检查播放状态
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_music_status)
        self.timer.start(1000)
        
    def set_dark_theme(self):
        """设置深色主题"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a2e;
            }
            QWidget {
                background-color: #1a1a2e;
                color: #ffffff;
                font-family: Arial;
            }
            QPushButton {
                background-color: #e94560;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 12px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c23b4f;
            }
            QPushButton:pressed {
                background-color: #a02f3f;
            }
            QListWidget {
                background-color: #0f3460;
                border: none;
                border-radius: 5px;
                padding: 5px;
                font-size: 11px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 3px;
            }
            QListWidget::item:selected {
                background-color: #e94560;
            }
            QListWidget::item:hover {
                background-color: #16213e;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #16213e;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #e94560;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QSlider::sub-page:horizontal {
                background: #e94560;
                border-radius: 3px;
            }
            QLabel {
                color: #ffffff;
            }
        """)
        
    def init_ui(self):
        """初始化界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("🎵 音乐播放器")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #e94560; padding: 10px; background-color: #16213e; border-radius: 5px;")
        main_layout.addWidget(title_label)
        
        # 当前播放信息
        self.song_label = QLabel("未播放")
        self.song_label.setFont(QFont("Arial", 14))
        self.song_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.song_label)
        
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setFont(QFont("Arial", 10))
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("color: #a0a0a0;")
        main_layout.addWidget(self.time_label)
        
        # 进度条（仅显示用）
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 100)
        main_layout.addWidget(self.progress_slider)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)
        
        self.prev_btn = QPushButton("⏮ 上一首")
        self.prev_btn.clicked.connect(self.prev_song)
        control_layout.addWidget(self.prev_btn)
        
        self.play_btn = QPushButton("▶ 播放")
        self.play_btn.clicked.connect(self.play_pause)
        control_layout.addWidget(self.play_btn)
        
        self.next_btn = QPushButton("⏭ 下一首")
        self.next_btn.clicked.connect(self.next_song)
        control_layout.addWidget(self.next_btn)
        
        self.stop_btn = QPushButton("⏹ 停止")
        self.stop_btn.clicked.connect(self.stop_music)
        control_layout.addWidget(self.stop_btn)
        
        main_layout.addLayout(control_layout)
        
        # 音量控制
        volume_layout = QHBoxLayout()
        volume_label = QLabel("🔊 音量")
        volume_label.setFont(QFont("Arial", 10))
        volume_layout.addWidget(volume_label)
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.valueChanged.connect(self.change_volume)
        volume_layout.addWidget(self.volume_slider)
        
        main_layout.addLayout(volume_layout)
        
        # 播放列表标签
        playlist_label = QLabel("播放列表")
        playlist_label.setFont(QFont("Arial", 12, QFont.Bold))
        playlist_label.setStyleSheet("padding: 5px; background-color: #16213e; border-radius: 5px;")
        main_layout.addWidget(playlist_label)
        
        # 播放列表
        self.playlist_widget = QListWidget()
        self.playlist_widget.itemDoubleClicked.connect(self.play_selected)
        main_layout.addWidget(self.playlist_widget)
        
        # 底部按钮
        bottom_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ 添加音乐")
        add_btn.clicked.connect(self.add_music)
        bottom_layout.addWidget(add_btn)
        
        add_folder_btn = QPushButton("📁 添加文件夹")
        add_folder_btn.clicked.connect(self.add_folder)
        bottom_layout.addWidget(add_folder_btn)
        
        clear_btn = QPushButton("🗑 清空列表")
        clear_btn.clicked.connect(self.clear_playlist)
        bottom_layout.addWidget(clear_btn)
        
        main_layout.addLayout(bottom_layout)
        
    def add_music(self):
        """添加音乐文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择音乐文件",
            "",
            "音频文件 (*.mp3 *.wav *.ogg *.flac);;所有文件 (*.*)"
        )
        
        for file in files:
            if file not in self.playlist_paths:
                self.playlist_paths.append(file)
                filename = os.path.basename(file)
                self.playlist_widget.addItem(filename)
        
        self.save_config()
    
    def add_folder(self):
        """添加文件夹中的所有音乐"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "选择音乐文件夹",
            ""
        )
        
        if folder:
            # 支持的音频格式
            audio_extensions = ['.mp3', '.wav', '.ogg', '.flac']
            added_count = 0
            
            # 遍历文件夹
            for root, dirs, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = os.path.splitext(file)[1].lower()
                    
                    if file_ext in audio_extensions and file_path not in self.playlist_paths:
                        self.playlist_paths.append(file_path)
                        self.playlist_widget.addItem(file)
                        added_count += 1
            
            if added_count > 0:
                QMessageBox.information(self, "成功", f"已添加 {added_count} 首歌曲")
                self.save_config()
            else:
                QMessageBox.warning(self, "提示", "该文件夹中没有找到音频文件")
        
    def play_pause(self):
        """播放/暂停"""
        if not self.playlist_paths:
            QMessageBox.warning(self, "提示", "播放列表为空，请先添加音乐")
            return
        
        if self.is_paused:
            mixer.music.unpause()
            self.is_paused = False
            self.play_btn.setText("⏸ 暂停")
        elif self.is_playing:
            mixer.music.pause()
            self.is_paused = True
            self.play_btn.setText("▶ 播放")
        else:
            if self.current_index == -1:
                self.current_index = 0
            self.play_current_song()
            
    def play_current_song(self):
        """播放当前歌曲"""
        if 0 <= self.current_index < len(self.playlist_paths):
            try:
                mixer.music.load(self.playlist_paths[self.current_index])
                mixer.music.play()
                self.is_playing = True
                self.is_paused = False
                self.play_btn.setText("⏸ 暂停")
                
                filename = os.path.basename(self.playlist_paths[self.current_index])
                self.song_label.setText(f"正在播放: {filename}")
                
                self.playlist_widget.setCurrentRow(self.current_index)
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法播放音乐:\n{str(e)}")
                
    def play_selected(self, item):
        """播放选中的歌曲"""
        self.current_index = self.playlist_widget.row(item)
        self.play_current_song()
        
    def prev_song(self):
        """上一首"""
        if self.playlist_paths:
            self.current_index = (self.current_index - 1) % len(self.playlist_paths)
            self.play_current_song()
        
    def next_song(self):
        """下一首"""
        if self.playlist_paths:
            self.current_index = (self.current_index + 1) % len(self.playlist_paths)
            self.play_current_song()
        
    def stop_music(self):
        """停止播放"""
        mixer.music.stop()
        self.is_playing = False
        self.is_paused = False
        self.play_btn.setText("▶ 播放")
        self.song_label.setText("未播放")
        self.time_label.setText("00:00 / 00:00")
        self.progress_slider.setValue(0)
        
    def change_volume(self, value):
        """改变音量"""
        mixer.music.set_volume(value / 100)
        
    def check_music_status(self):
        """检查音乐播放状态"""
        if self.is_playing and not mixer.music.get_busy() and not self.is_paused:
            # 歌曲播放完毕，自动播放下一首
            self.next_song()
        
    def clear_playlist(self):
        """清空播放列表"""
        reply = QMessageBox.question(
            self,
            "确认",
            "确定要清空播放列表吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.stop_music()
            self.playlist_widget.clear()
            self.playlist_paths.clear()
            self.current_index = -1
            self.save_config()
            
    def load_config(self):
        """加载配置"""
        try:
            if os.path.exists("music_player_config.json"):
                with open("music_player_config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.playlist_paths = config.get("playlist", [])
                    volume = config.get("volume", 70)
                    
                    for file in self.playlist_paths:
                        if os.path.exists(file):
                            filename = os.path.basename(file)
                            self.playlist_widget.addItem(filename)
                    
                    self.volume_slider.setValue(volume)
        except Exception as e:
            print(f"加载配置失败: {e}")
            
    def save_config(self):
        """保存配置"""
        try:
            config = {
                "playlist": self.playlist_paths,
                "volume": self.volume_slider.value()
            }
            with open("music_player_config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")
            
    def closeEvent(self, event):
        """关闭窗口时保存配置"""
        self.save_config()
        mixer.music.stop()
        event.accept()

def main():
    """主函数入口"""
    app = QApplication(sys.argv)
    player = MusicPlayer()
    player.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
