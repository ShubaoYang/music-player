"""主窗口视图"""

import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QFileDialog, QMessageBox,
                               QButtonGroup, QComboBox, QMenu, QToolButton,
                               QSlider)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QKeySequence, QPixmap, QAction, QShortcut

from .control_panel import ControlPanel
from .playlist_view import PlaylistView
from ..models.playback_mode import PlaybackMode


class MainWindow(QMainWindow):
    """主窗口"""
    
    # 信号
    add_files_requested = Signal(list)
    add_folder_requested = Signal(str)
    clear_playlist_requested = Signal()
    save_playlist_requested = Signal(str)
    load_playlist_requested = Signal(str)
    play_pause_clicked = Signal()
    prev_clicked = Signal()
    next_clicked = Signal()
    seek_requested = Signal(float)
    volume_changed = Signal(float)
    window_closing = Signal()  # 窗口关闭信号
    mini_mode_requested = Signal()  # 切换到迷你模式
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        self.setWindowTitle("🎵 音乐播放器")
        
        # 固定窗口尺寸
        self.setFixedSize(900, 500)
        
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
        
        # 左侧：播放器主区域（固定宽度）
        player_widget = QWidget(central_widget)
        player_widget.setGeometry(0, 0, 550, 500)  # 固定位置和大小
        player_widget.setStyleSheet("""
            background: #000000;
        """)
        player_layout = QVBoxLayout(player_widget)
        player_layout.setSpacing(10)
        player_layout.setContentsMargins(15, 15, 15, 15)
        
        # 第一行：歌曲信息（封面 + 歌名 + 艺术家）
        info_widget = QWidget()
        info_widget.setStyleSheet("""
            background: rgba(15, 15, 15, 0.95);
            border-radius: 18px;
            border: 1px solid rgba(40, 40, 40, 0.8);
            padding: 20px;
        """)
        info_layout = QHBoxLayout(info_widget)
        info_layout.setSpacing(20)
        
        # 封面（优化样式 - 黑色主题）
        self.cover_label = QLabel()
        self.cover_label.setFixedSize(100, 100)
        self.cover_label.setStyleSheet("""
            background: rgba(25, 25, 25, 0.9);
            border-radius: 15px;
            border: 2px solid rgba(50, 50, 50, 0.8);
            font-size: 42px;
            qproperty-alignment: AlignCenter;
        """)
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setText("♪")
        self.cover_label.setFont(QFont("SF Pro Display", 42, QFont.Weight.Bold))
        info_layout.addWidget(self.cover_label)
        
        # 歌曲信息
        song_info_layout = QVBoxLayout()
        song_info_layout.setSpacing(8)
        
        self.song_label = QLabel("未播放")
        self.song_label.setFont(QFont("SF Pro Display", 20, QFont.Weight.Bold))
        self.song_label.setStyleSheet("""
            color: white;
            background: transparent;
        """)
        song_info_layout.addWidget(self.song_label)
        
        self.artist_label = QLabel("")
        self.artist_label.setFont(QFont("SF Pro Display", 14))
        self.artist_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.7);
            background: transparent;
        """)
        song_info_layout.addWidget(self.artist_label)
        
        self.album_label = QLabel("")
        self.album_label.setFont(QFont("SF Pro Display", 12))
        self.album_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.5);
            background: transparent;
        """)
        song_info_layout.addWidget(self.album_label)
        
        song_info_layout.addStretch()
        info_layout.addLayout(song_info_layout, 1)
        
        player_layout.addWidget(info_widget)
        
        # 第二行：播放进度条 + 时间
        progress_widget = QWidget()
        progress_layout = QVBoxLayout(progress_widget)
        progress_layout.setSpacing(5)
        
        # 进度条
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 1000)
        self.progress_slider.setValue(0)
        self.progress_slider.sliderPressed.connect(self._on_slider_pressed)
        self.progress_slider.sliderReleased.connect(self._on_slider_released)
        self.progress_slider.sliderMoved.connect(self._on_slider_moved)
        progress_layout.addWidget(self.progress_slider)
        
        # 时间标签
        time_layout = QHBoxLayout()
        self.current_time_label = QLabel("00:00")
        self.current_time_label.setFont(QFont("SF Pro Display", 11))
        self.current_time_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.7);
            background: transparent;
        """)
        time_layout.addWidget(self.current_time_label)
        
        time_layout.addStretch()
        
        self.total_time_label = QLabel("00:00")
        self.total_time_label.setFont(QFont("SF Pro Display", 11))
        self.total_time_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.5);
            background: transparent;
        """)
        time_layout.addWidget(self.total_time_label)
        
        progress_layout.addLayout(time_layout)
        player_layout.addWidget(progress_widget)
        
        # 第三行：控制面板（上一曲、播放/暂停、下一曲、音量）
        control_widget = QWidget()
        control_widget.setStyleSheet("""
            background: rgba(15, 15, 15, 0.95);
            border-radius: 18px;
            border: 1px solid rgba(40, 40, 40, 0.8);
            padding: 15px;
        """)
        control_layout = QHBoxLayout(control_widget)
        control_layout.setSpacing(15)
        
        # 播放控制按钮
        play_control_layout = QHBoxLayout()
        play_control_layout.setSpacing(12)
        
        # 统一的按钮样式 - 黑色主题
        button_style = """
            QPushButton {
                background: rgba(40, 40, 40, 0.9);
                color: white;
                border: 1px solid rgba(60, 60, 60, 0.6);
                border-radius: 16px;
                font-size: 14px;
                min-width: 36px;
                max-width: 36px;
                min-height: 36px;
                max-height: 36px;
            }
            QPushButton:hover {
                background: rgba(60, 60, 60, 0.95);
                border: 1px solid rgba(80, 80, 80, 0.8);
            }
            QPushButton:pressed {
                background: rgba(30, 30, 30, 0.9);
            }
        """
        
        play_button_style = """
            QPushButton {
                background: rgba(255, 255, 255, 0.95);
                color: #000000;
                border: none;
                border-radius: 24px;
                font-size: 18px;
                min-width: 48px;
                max-width: 48px;
                min-height: 48px;
                max-height: 48px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 1);
            }
            QPushButton:pressed {
                background: rgba(220, 220, 220, 0.95);
            }
        """
        
        self.prev_btn = QPushButton("⏮")
        self.prev_btn.setStyleSheet(button_style)
        self.prev_btn.clicked.connect(self._on_prev_clicked)
        play_control_layout.addWidget(self.prev_btn)
        
        play_control_layout.addSpacing(8)
        
        self.play_btn = QPushButton("▶")
        self.play_btn.setStyleSheet(play_button_style)
        self.play_btn.clicked.connect(self._on_play_pause_clicked)
        play_control_layout.addWidget(self.play_btn)
        
        play_control_layout.addSpacing(8)
        
        self.next_btn = QPushButton("⏭")
        self.next_btn.setStyleSheet(button_style)
        self.next_btn.clicked.connect(self._on_next_clicked)
        play_control_layout.addWidget(self.next_btn)
        
        control_layout.addLayout(play_control_layout)
        control_layout.addStretch()
        
        # 音量控制（细长样式）
        volume_layout = QHBoxLayout()
        volume_layout.setSpacing(10)
        
        # 音量滑块 - 更细长，增加宽度
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setFixedWidth(150)
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 3px;
                background: rgba(80, 80, 80, 0.5);
                border-radius: 1px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                width: 12px;
                height: 12px;
                margin: -5px 0;
                border-radius: 6px;
                border: none;
            }
            QSlider::handle:horizontal:hover {
                background: #e0e0e0;
                width: 14px;
                height: 14px;
                margin: -6px 0;
                border-radius: 7px;
            }
            QSlider::sub-page:horizontal {
                background: #ffffff;
                border-radius: 1px;
            }
        """)
        volume_layout.addWidget(self.volume_slider)
        
        control_layout.addLayout(volume_layout)
        
        # 播放模式按钮（放在音量后面）
        self.mode_btn = QPushButton()
        self.mode_btn.setFixedSize(60, 36)
        self.mode_btn.setText("▶▶")
        self.mode_btn.setFont(QFont("Arial", 12))
        self.mode_btn.setStyleSheet("""
            QPushButton {
                background: rgba(40, 40, 40, 0.9);
                color: white;
                border: 1px solid rgba(60, 60, 60, 0.6);
                border-radius: 18px;
                font-size: 12px;
                padding: 0px;
                text-align: center;
            }
            QPushButton:hover {
                background: rgba(60, 60, 60, 0.95);
                border: 1px solid rgba(80, 80, 80, 0.8);
            }
            QPushButton:pressed {
                background: rgba(30, 30, 30, 0.9);
            }
        """)
        self.mode_btn.setToolTip("播放模式：顺序播放")
        self.mode_btn.clicked.connect(self._cycle_play_mode)
        control_layout.addWidget(self.mode_btn)
        
        player_layout.addWidget(control_widget)
        player_layout.addStretch()
        
        # 右侧：播放列表（使用绝对定位）
        self.playlist_container = QWidget(central_widget)
        self.playlist_container.setGeometry(550, 0, 350, 500)  # 固定在右侧
        self.playlist_container.setStyleSheet("""
            background: rgba(10, 10, 10, 0.98);
            border-left: 1px solid rgba(60, 60, 60, 0.5);
        """)
        playlist_layout = QVBoxLayout(self.playlist_container)
        playlist_layout.setSpacing(12)
        playlist_layout.setContentsMargins(15, 15, 15, 15)
        
        # 播放列表标题栏（包含标题和菜单按钮）
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        
        playlist_header = QLabel("📀 播放列表")
        playlist_header.setFont(QFont("SF Pro Display", 18, QFont.Weight.Bold))
        playlist_header.setStyleSheet("""
            color: white;
            background: transparent;
            padding: 10px;
        """)
        header_layout.addWidget(playlist_header)
        
        header_layout.addStretch()
        
        # 菜单按钮
        self.menu_btn = QToolButton()
        self.menu_btn.setText("☰")
        self.menu_btn.setFixedSize(32, 32)
        self.menu_btn.setFont(QFont("SF Pro Display", 14))
        self.menu_btn.setStyleSheet("""
            QToolButton {
                background: rgba(30, 30, 30, 0.9);
                color: white;
                border: 1px solid rgba(50, 50, 50, 0.8);
                border-radius: 16px;
            }
            QToolButton:hover {
                background: rgba(50, 50, 50, 0.95);
                border: 1px solid rgba(70, 70, 70, 0.9);
            }
            QToolButton::menu-indicator {
                image: none;
            }
        """)
        self.menu_btn.setToolTip("菜单")
        self.menu_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self._create_menu()
        header_layout.addWidget(self.menu_btn)
        
        playlist_layout.addLayout(header_layout)
        
        # 播放列表视图
        self.playlist_view = PlaylistView()
        playlist_layout.addWidget(self.playlist_view)
        
        # 设置键盘快捷键
        self._setup_shortcuts()
        
        # 初始化进度条状态
        self._is_seeking = False
        self._duration = 0.0
    
    def set_dark_theme(self) -> None:
        """设置现代化深色主题 - 黑色主调"""
        self.setStyleSheet("""
            QMainWindow {
                background: #000000;
            }
            QWidget {
                background-color: transparent;
                color: #ffffff;
                font-family: "SF Pro Display", "Helvetica Neue", "Arial", sans-serif;
            }
            QPushButton {
                background: rgba(40, 40, 40, 0.9);
                color: white;
                border: 1px solid rgba(80, 80, 80, 0.5);
                padding: 12px 24px;
                font-size: 13px;
                border-radius: 10px;
                font-weight: 600;
                min-height: 20px;
            }
            QPushButton:hover {
                background: rgba(60, 60, 60, 0.9);
                border: 1px solid rgba(100, 100, 100, 0.7);
            }
            QPushButton:pressed {
                background: rgba(30, 30, 30, 0.9);
            }
            QPushButton:checked {
                background: rgba(80, 80, 80, 0.9);
                border: 2px solid rgba(120, 120, 120, 0.8);
            }
            QListWidget {
                background-color: rgba(10, 10, 10, 0.95);
                border: 1px solid rgba(60, 60, 60, 0.5);
                border-radius: 15px;
                padding: 10px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 14px;
                border-radius: 10px;
                margin: 3px 0;
                color: rgba(255, 255, 255, 0.9);
            }
            QListWidget::item:selected {
                background: rgba(80, 80, 80, 0.6);
                color: white;
                border-left: 3px solid rgba(200, 200, 200, 1);
            }
            QListWidget::item:hover {
                background-color: rgba(50, 50, 50, 0.5);
            }
            QSlider::groove:horizontal {
                height: 4px;
                background: rgba(80, 80, 80, 0.5);
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
                border: none;
            }
            QSlider::handle:horizontal:hover {
                background: #e0e0e0;
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
            QSlider::sub-page:horizontal {
                background: #ffffff;
                border-radius: 2px;
            }
            QLabel {
                color: #ffffff;
            }
            QLineEdit {
                background-color: rgba(30, 30, 30, 0.8);
                border: 1px solid rgba(80, 80, 80, 0.5);
                border-radius: 12px;
                padding: 10px 15px;
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid rgba(120, 120, 120, 0.8);
                background-color: rgba(40, 40, 40, 0.9);
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.3);
            }
            QComboBox {
                background: rgba(30, 30, 30, 0.8);
                color: white;
                border: 1px solid rgba(80, 80, 80, 0.5);
                padding: 5px;
                border-radius: 10px;
                font-size: 11px;
            }
            QComboBox:hover {
                background: rgba(40, 40, 40, 0.9);
                border: 1px solid rgba(100, 100, 100, 0.7);
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: rgba(20, 20, 20, 0.98);
                color: white;
                selection-background-color: rgba(80, 80, 80, 0.8);
                border: 1px solid rgba(80, 80, 80, 0.5);
                border-radius: 8px;
            }
        """)
    
    def _setup_shortcuts(self) -> None:
        """设置键盘快捷键"""
        
        # 空格键：播放/暂停
        QShortcut(QKeySequence(Qt.Key.Key_Space), self, self._on_play_pause_clicked)
        
        # 右箭头：下一首
        QShortcut(QKeySequence(Qt.Key.Key_Right), self, self._on_next_clicked)
        
        # 左箭头：上一首
        QShortcut(QKeySequence(Qt.Key.Key_Left), self, self._on_prev_clicked)
        
        # 上箭头：增加音量
        QShortcut(QKeySequence(Qt.Key.Key_Up), self, self._volume_up)
        
        # 下箭头：减少音量
        QShortcut(QKeySequence(Qt.Key.Key_Down), self, self._volume_down)
    
    def _create_menu(self) -> None:
        """创建菜单"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(20, 20, 20, 0.98);
                color: white;
                border: 1px solid rgba(80, 80, 80, 0.5);
                border-radius: 12px;
                padding: 8px;
            }
            QMenu::item {
                padding: 10px 25px;
                border-radius: 8px;
                margin: 2px 4px;
            }
            QMenu::item:selected {
                background: rgba(80, 80, 80, 0.8);
            }
            QMenu::separator {
                height: 1px;
                background: rgba(80, 80, 80, 0.5);
                margin: 5px 10px;
            }
        """)
        
        add_files_action = QAction("➕ 添加音乐文件", self)
        add_files_action.triggered.connect(self._add_music)
        menu.addAction(add_files_action)
        
        add_folder_action = QAction("📁 添加文件夹", self)
        add_folder_action.triggered.connect(self._add_folder)
        menu.addAction(add_folder_action)
        
        menu.addSeparator()
        
        save_action = QAction("💾 保存播放列表", self)
        save_action.triggered.connect(self._save_playlist)
        menu.addAction(save_action)
        
        load_action = QAction("📂 加载播放列表", self)
        load_action.triggered.connect(self._load_playlist)
        menu.addAction(load_action)
        
        menu.addSeparator()
        
        clear_action = QAction("🗑 清空列表", self)
        clear_action.triggered.connect(self._clear_playlist)
        menu.addAction(clear_action)
        
        menu.addSeparator()
        
        mini_action = QAction("🎵 迷你模式", self)
        mini_action.triggered.connect(self.mini_mode_requested.emit)
        menu.addAction(mini_action)
        
        self.menu_btn.setMenu(menu)
    
    def _on_play_pause_clicked(self) -> None:
        """播放/暂停按钮点击"""
        self.play_pause_clicked.emit()
    
    def _on_prev_clicked(self) -> None:
        """上一曲按钮点击"""
        self.prev_clicked.emit()
    
    def _on_next_clicked(self) -> None:
        """下一曲按钮点击"""
        self.next_clicked.emit()
    
    def _on_volume_changed(self, value: int) -> None:
        """音量改变"""
        self.volume_changed.emit(value / 100.0)
    
    def _on_slider_pressed(self) -> None:
        """进度条按下"""
        self._is_seeking = True
    
    def _on_slider_released(self) -> None:
        """进度条释放"""
        self._is_seeking = False
        # 发送跳转请求
        if self._duration > 0:
            position = (self.progress_slider.value() / 1000.0) * self._duration
            self.seek_requested.emit(position)
    
    def _on_slider_moved(self, value: int) -> None:
        """进度条移动"""
        if self._duration > 0:
            position = (value / 1000.0) * self._duration
            from ..models.track import Track
            current_time = Track.format_time(position)
            self.current_time_label.setText(current_time)
    
    def _volume_up(self) -> None:
        """增加音量"""
        current = self.volume_slider.value()
        self.volume_slider.setValue(min(100, current + 5))
    
    def _volume_down(self) -> None:
        """减少音量"""
        current = self.volume_slider.value()
        self.volume_slider.setValue(max(0, current - 5))
    
    def update_play_button(self, is_playing: bool) -> None:
        """更新播放按钮状态"""
        if is_playing:
            self.play_btn.setText("⏸")
        else:
            self.play_btn.setText("▶")
    
    def update_progress(self, position: float, duration: float) -> None:
        """更新进度"""
        if self._is_seeking:
            return
        
        self._duration = duration
        
        # 更新进度条
        if duration > 0:
            progress = int((position / duration) * 1000)
            self.progress_slider.setValue(progress)
        else:
            self.progress_slider.setValue(0)
        
        # 更新时间标签
        from ..models.track import Track
        current_time = Track.format_time(position)
        total_time = Track.format_time(duration)
        self.current_time_label.setText(current_time)
        self.total_time_label.setText(total_time)
    
    def reset_progress(self) -> None:
        """重置进度"""
        self.progress_slider.setValue(0)
        self.current_time_label.setText("00:00")
        self.total_time_label.setText("00:00")
        self._duration = 0.0
    
    def _add_music(self) -> None:
        """添加音乐文件"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择音乐文件",
            os.path.expanduser("~"),
            "音频文件 (*.mp3 *.wav *.ogg *.flac);;所有文件 (*.*)"
        )
        if files:
            self.add_files_requested.emit(files)
    
    def _add_folder(self) -> None:
        """添加文件夹"""
        folder = QFileDialog.getExistingDirectory(
            self, "选择音乐文件夹", os.path.expanduser("~")
        )
        if folder:
            self.add_folder_requested.emit(folder)
    
    def _clear_playlist(self) -> None:
        """清空播放列表"""
        reply = QMessageBox.question(
            self,
            "确认",
            "确定要清空播放列表吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.clear_playlist_requested.emit()
    
    def _save_playlist(self) -> None:
        """保存播放列表"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存播放列表", os.path.expanduser("~"), "播放列表文件 (*.json)"
        )
        if file_path:
            self.save_playlist_requested.emit(file_path)
    
    def _load_playlist(self) -> None:
        """加载播放列表"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "加载播放列表",
            os.path.expanduser("~"),
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
            scaled_cover = cover.scaled(90, 90, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
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
        mode_icons = ["▶▶", "🔁", "🔀", "1️⃣"]
        modes = [PlaybackMode.SEQUENTIAL, PlaybackMode.LOOP, 
                 PlaybackMode.SHUFFLE, PlaybackMode.SINGLE_REPEAT]
        
        current_text = self.mode_btn.text()
        try:
            mode_index = mode_icons.index(current_text)
            return modes[mode_index] if 0 <= mode_index < len(modes) else PlaybackMode.SEQUENTIAL
        except ValueError:
            return PlaybackMode.SEQUENTIAL
    
    def set_playback_mode(self, mode: PlaybackMode) -> None:
        """设置播放模式
        
        Args:
            mode: 播放模式
        """
        mode_icons = ["▶▶", "🔁", "🔀", "1️⃣"]
        mode_names = ["顺序播放", "列表循环", "随机播放", "单曲循环"]
        mode_map = {
            PlaybackMode.SEQUENTIAL: 0,
            PlaybackMode.LOOP: 1,
            PlaybackMode.SHUFFLE: 2,
            PlaybackMode.SINGLE_REPEAT: 3
        }
        index = mode_map.get(mode, 0)
        self.mode_btn.setText(mode_icons[index])
        self.mode_btn.setToolTip(f"播放模式：{mode_names[index]}")
    
    def _request_progress_update(self) -> None:
        """请求进度更新（由外部控制器处理）"""
        pass
    
    def _cycle_play_mode(self) -> None:
        """循环切换播放模式"""
        mode_icons = ["▶▶", "🔁", "🔀", "1️⃣"]
        mode_names = ["顺序播放", "列表循环", "随机播放", "单曲循环"]
        modes = [PlaybackMode.SEQUENTIAL, PlaybackMode.LOOP, 
                 PlaybackMode.SHUFFLE, PlaybackMode.SINGLE_REPEAT]
        
        current_text = self.mode_btn.text()
        try:
            current_index = mode_icons.index(current_text)
            next_index = (current_index + 1) % len(mode_icons)
        except ValueError:
            next_index = 0
        
        self.mode_btn.setText(mode_icons[next_index])
        self.mode_btn.setToolTip(f"播放模式：{mode_names[next_index]}")
    
    def closeEvent(self, event) -> None:
        """窗口关闭事件"""
        # 发送窗口关闭信号，让主应用保存状态
        self.window_closing.emit()
        event.accept()
