"""主窗口视图"""

import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QMessageBox,
                             QButtonGroup)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QKeySequence, QPixmap

from .control_panel import ControlPanel
from .playlist_view import PlaylistView
from ..models.playback_mode import PlaybackMode


class MainWindow(QMainWindow):
    """主窗口"""
    
    # 信号
    add_files_requested = pyqtSignal(list)
    add_folder_requested = pyqtSignal(str)
    clear_playlist_requested = pyqtSignal()
    save_playlist_requested = pyqtSignal(str)
    load_playlist_requested = pyqtSignal(str)
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        self.setWindowTitle("🎵 音乐播放器")
        self.setGeometry(100, 100, 900, 700)
        
        # 设置深色主题
        self.set_dark_theme()
        
        # 创建界面
        self.init_ui()
        
        # 创建定时器用于更新进度
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._request_progress_update)
        self.update_timer.start(100)  # 每100ms更新一次
    
    def init_ui(self) -> None:
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
        title_label.setStyleSheet(
            "color: #e94560; padding: 10px; background-color: #16213e; border-radius: 5px;"
        )
        main_layout.addWidget(title_label)
        
        # 当前播放信息区域
        now_playing_layout = QHBoxLayout()
        
        # 封面
        self.cover_label = QLabel()
        self.cover_label.setFixedSize(80, 80)
        self.cover_label.setStyleSheet(
            "background-color: #16213e; border-radius: 5px;"
        )
        self.cover_label.setAlignment(Qt.AlignCenter)
        self.cover_label.setText("♪")
        self.cover_label.setFont(QFont("Arial", 32))
        now_playing_layout.addWidget(self.cover_label)
        
        # 歌曲信息
        info_layout = QVBoxLayout()
        self.song_label = QLabel("未播放")
        self.song_label.setFont(QFont("Arial", 14, QFont.Bold))
        info_layout.addWidget(self.song_label)
        
        self.artist_label = QLabel("")
        self.artist_label.setFont(QFont("Arial", 11))
        self.artist_label.setStyleSheet("color: #a0a0a0;")
        info_layout.addWidget(self.artist_label)
        
        self.album_label = QLabel("")
        self.album_label.setFont(QFont("Arial", 10))
        self.album_label.setStyleSheet("color: #808080;")
        info_layout.addWidget(self.album_label)
        
        now_playing_layout.addLayout(info_layout)
        now_playing_layout.addStretch()
        
        main_layout.addLayout(now_playing_layout)
        
        # 播放模式选择
        mode_layout = QHBoxLayout()
        mode_label = QLabel("播放模式:")
        mode_label.setFont(QFont("Arial", 10))
        mode_layout.addWidget(mode_label)
        
        self.mode_button_group = QButtonGroup()
        
        self.sequential_btn = QPushButton("⏩ 顺序")
        self.sequential_btn.setCheckable(True)
        self.sequential_btn.setChecked(True)
        self.mode_button_group.addButton(self.sequential_btn, 0)
        mode_layout.addWidget(self.sequential_btn)
        
        self.loop_btn = QPushButton("🔁 循环")
        self.loop_btn.setCheckable(True)
        self.mode_button_group.addButton(self.loop_btn, 1)
        mode_layout.addWidget(self.loop_btn)
        
        self.shuffle_btn = QPushButton("🔀 随机")
        self.shuffle_btn.setCheckable(True)
        self.mode_button_group.addButton(self.shuffle_btn, 2)
        mode_layout.addWidget(self.shuffle_btn)
        
        self.single_btn = QPushButton("🔂 单曲")
        self.single_btn.setCheckable(True)
        self.mode_button_group.addButton(self.single_btn, 3)
        mode_layout.addWidget(self.single_btn)
        
        mode_layout.addStretch()
        main_layout.addLayout(mode_layout)
        
        # 控制面板
        self.control_panel = ControlPanel()
        main_layout.addWidget(self.control_panel)
        
        # 播放列表视图
        self.playlist_view = PlaylistView()
        main_layout.addWidget(self.playlist_view)
        
        # 底部按钮
        bottom_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ 添加音乐")
        add_btn.clicked.connect(self._add_music)
        bottom_layout.addWidget(add_btn)
        
        add_folder_btn = QPushButton("📁 添加文件夹")
        add_folder_btn.clicked.connect(self._add_folder)
        bottom_layout.addWidget(add_folder_btn)
        
        save_playlist_btn = QPushButton("💾 保存列表")
        save_playlist_btn.clicked.connect(self._save_playlist)
        bottom_layout.addWidget(save_playlist_btn)
        
        load_playlist_btn = QPushButton("📂 加载列表")
        load_playlist_btn.clicked.connect(self._load_playlist)
        bottom_layout.addWidget(load_playlist_btn)
        
        clear_btn = QPushButton("🗑 清空列表")
        clear_btn.clicked.connect(self._clear_playlist)
        bottom_layout.addWidget(clear_btn)
        
        main_layout.addLayout(bottom_layout)
        
        # 设置键盘快捷键
        self._setup_shortcuts()
    
    def set_dark_theme(self) -> None:
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
            QPushButton:checked {
                background-color: #16213e;
                border: 2px solid #e94560;
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
            QLineEdit {
                background-color: #0f3460;
                border: 1px solid #16213e;
                border-radius: 5px;
                padding: 5px;
                color: #ffffff;
            }
        """)
    
    def _setup_shortcuts(self) -> None:
        """设置键盘快捷键"""
        from PyQt5.QtWidgets import QShortcut
        
        # 空格键：播放/暂停
        QShortcut(QKeySequence(Qt.Key_Space), self, self.control_panel.play_pause_clicked.emit)
        
        # 右箭头：下一首
        QShortcut(QKeySequence(Qt.Key_Right), self, self.control_panel.next_clicked.emit)
        
        # 左箭头：上一首
        QShortcut(QKeySequence(Qt.Key_Left), self, self.control_panel.prev_clicked.emit)
        
        # 上箭头：增加音量
        QShortcut(QKeySequence(Qt.Key_Up), self, self._volume_up)
        
        # 下箭头：减少音量
        QShortcut(QKeySequence(Qt.Key_Down), self, self._volume_down)
    
    def _volume_up(self) -> None:
        """增加音量"""
        current = self.control_panel.volume_slider.value()
        self.control_panel.volume_slider.setValue(min(100, current + 5))
    
    def _volume_down(self) -> None:
        """减少音量"""
        current = self.control_panel.volume_slider.value()
        self.control_panel.volume_slider.setValue(max(0, current - 5))
    
    def _add_music(self) -> None:
        """添加音乐文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择音乐文件",
            "",
            "音频文件 (*.mp3 *.wav *.ogg *.flac);;所有文件 (*.*)"
        )
        if files:
            self.add_files_requested.emit(files)
    
    def _add_folder(self) -> None:
        """添加文件夹"""
        folder = QFileDialog.getExistingDirectory(self, "选择音乐文件夹", "")
        if folder:
            self.add_folder_requested.emit(folder)
    
    def _clear_playlist(self) -> None:
        """清空播放列表"""
        reply = QMessageBox.question(
            self,
            "确认",
            "确定要清空播放列表吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.clear_playlist_requested.emit()
    
    def _save_playlist(self) -> None:
        """保存播放列表"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存播放列表",
            "",
            "播放列表文件 (*.json)"
        )
        if file_path:
            self.save_playlist_requested.emit(file_path)
    
    def _load_playlist(self) -> None:
        """加载播放列表"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "加载播放列表",
            "",
            "播放列表文件 (*.json)"
        )
        if file_path:
            self.load_playlist_requested.emit(file_path)
    
    def update_now_playing(self, title: str, artist: str, album: str, cover: QPixmap = None) -> None:
        """更新正在播放信息
        
        Args:
            title: 标题
            artist: 艺术家
            album: 专辑
            cover: 封面图片
        """
        self.song_label.setText(title)
        self.artist_label.setText(artist)
        self.album_label.setText(album)
        
        if cover and not cover.isNull():
            scaled_cover = cover.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.cover_label.setPixmap(scaled_cover)
        else:
            self.cover_label.clear()
            self.cover_label.setText("♪")
    
    def clear_now_playing(self) -> None:
        """清空正在播放信息"""
        self.song_label.setText("未播放")
        self.artist_label.setText("")
        self.album_label.setText("")
        self.cover_label.clear()
        self.cover_label.setText("♪")
    
    def get_playback_mode(self) -> PlaybackMode:
        """获取播放模式
        
        Returns:
            播放模式
        """
        button_id = self.mode_button_group.checkedId()
        modes = [PlaybackMode.SEQUENTIAL, PlaybackMode.LOOP, 
                 PlaybackMode.SHUFFLE, PlaybackMode.SINGLE_REPEAT]
        return modes[button_id] if 0 <= button_id < len(modes) else PlaybackMode.SEQUENTIAL
    
    def set_playback_mode(self, mode: PlaybackMode) -> None:
        """设置播放模式
        
        Args:
            mode: 播放模式
        """
        mode_map = {
            PlaybackMode.SEQUENTIAL: self.sequential_btn,
            PlaybackMode.LOOP: self.loop_btn,
            PlaybackMode.SHUFFLE: self.shuffle_btn,
            PlaybackMode.SINGLE_REPEAT: self.single_btn
        }
        button = mode_map.get(mode)
        if button:
            button.setChecked(True)
    
    def _request_progress_update(self) -> None:
        """请求进度更新（由外部控制器处理）"""
        pass
    
    def closeEvent(self, event) -> None:
        """窗口关闭事件"""
        # 保存窗口几何信息
        geometry = self.saveGeometry()
        # 这里可以通过信号通知控制器保存配置
        event.accept()
