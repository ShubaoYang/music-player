"""迷你播放器窗口"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QLabel, QSlider)
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QFont, QMouseEvent, QPixmap


class MiniWindow(QWidget):
    """迷你播放器窗口 - 紧凑的悬浮窗口"""
    
    # 信号
    play_pause_clicked = Signal()
    prev_clicked = Signal()
    next_clicked = Signal()
    volume_changed = Signal(float)
    restore_clicked = Signal()  # 恢复到正常窗口
    close_clicked = Signal()
    
    def __init__(self):
        """初始化迷你窗口"""
        super().__init__()
        
        # 设置窗口属性
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |  # 无边框
            Qt.WindowType.WindowStaysOnTopHint |  # 置顶
            Qt.WindowType.Tool  # 工具窗口（不在任务栏显示）
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)  # 透明背景
        
        # 固定尺寸
        self.setFixedSize(350, 120)
        
        # 拖动相关
        self._dragging = False
        self._drag_position = QPoint()
        
        # 初始化界面
        self.init_ui()
    
    def init_ui(self) -> None:
        """初始化界面"""
        # 主容器
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background: rgba(0, 0, 0, 0.95);
                border-radius: 15px;
                border: 1px solid rgba(60, 60, 60, 0.8);
            }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)
        
        layout = QVBoxLayout(container)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 10, 12, 10)
        
        # 顶部栏：歌曲信息 + 控制按钮
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        
        # 封面
        self.cover_label = QLabel()
        self.cover_label.setFixedSize(60, 60)
        self.cover_label.setStyleSheet("""
            background: rgba(25, 25, 25, 0.9);
            border-radius: 10px;
            border: 1px solid rgba(50, 50, 50, 0.8);
            font-size: 28px;
            qproperty-alignment: AlignCenter;
            color: rgba(255, 255, 255, 0.6);
        """)
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setText("♪")
        self.cover_label.setFont(QFont("SF Pro Display", 28, QFont.Weight.Bold))
        top_layout.addWidget(self.cover_label)
        
        # 歌曲信息
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        self.song_label = QLabel("未播放")
        self.song_label.setFont(QFont("SF Pro Display", 13, QFont.Weight.Bold))
        self.song_label.setStyleSheet("""
            color: white;
            background: transparent;
        """)
        self.song_label.setWordWrap(False)
        info_layout.addWidget(self.song_label)
        
        self.artist_label = QLabel("")
        self.artist_label.setFont(QFont("SF Pro Display", 11))
        self.artist_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.6);
            background: transparent;
        """)
        self.artist_label.setWordWrap(False)
        info_layout.addWidget(self.artist_label)
        
        # 时间标签
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setFont(QFont("SF Pro Display", 10))
        self.time_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.5);
            background: transparent;
        """)
        info_layout.addWidget(self.time_label)
        
        info_layout.addStretch()
        top_layout.addLayout(info_layout, 1)
        
        # 右侧控制按钮
        control_layout = QVBoxLayout()
        control_layout.setSpacing(4)
        
        # 恢复/关闭按钮
        btn_row = QHBoxLayout()
        btn_row.setSpacing(4)
        
        self.restore_btn = QPushButton("□")
        self.restore_btn.setFixedSize(24, 24)
        self.restore_btn.setStyleSheet("""
            QPushButton {
                background: rgba(40, 40, 40, 0.8);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(60, 60, 60, 0.9);
            }
        """)
        self.restore_btn.setToolTip("恢复正常窗口")
        self.restore_btn.clicked.connect(self.restore_clicked.emit)
        btn_row.addWidget(self.restore_btn)
        
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(200, 50, 50, 0.8);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(220, 60, 60, 0.9);
            }
        """)
        self.close_btn.setToolTip("关闭迷你模式")
        self.close_btn.clicked.connect(self.close_clicked.emit)
        btn_row.addWidget(self.close_btn)
        
        control_layout.addLayout(btn_row)
        control_layout.addStretch()
        
        top_layout.addLayout(control_layout)
        
        layout.addLayout(top_layout)
        
        # 播放控制按钮
        play_layout = QHBoxLayout()
        play_layout.setSpacing(8)
        
        button_style = """
            QPushButton {
                background: rgba(40, 40, 40, 0.9);
                color: white;
                border: 1px solid rgba(60, 60, 60, 0.6);
                border-radius: 14px;
                font-size: 12px;
                min-width: 28px;
                max-width: 28px;
                min-height: 28px;
                max-height: 28px;
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
                border-radius: 18px;
                font-size: 14px;
                min-width: 36px;
                max-width: 36px;
                min-height: 36px;
                max-height: 36px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 1);
            }
            QPushButton:pressed {
                background: rgba(220, 220, 220, 0.95);
            }
        """
        
        play_layout.addStretch()
        
        self.prev_btn = QPushButton("⏮")
        self.prev_btn.setStyleSheet(button_style)
        self.prev_btn.clicked.connect(self.prev_clicked.emit)
        play_layout.addWidget(self.prev_btn)
        
        self.play_btn = QPushButton("▶")
        self.play_btn.setStyleSheet(play_button_style)
        self.play_btn.clicked.connect(self.play_pause_clicked.emit)
        play_layout.addWidget(self.play_btn)
        
        self.next_btn = QPushButton("⏭")
        self.next_btn.setStyleSheet(button_style)
        self.next_btn.clicked.connect(self.next_clicked.emit)
        play_layout.addWidget(self.next_btn)
        
        # 音量控制
        volume_icon = QLabel("🔊")
        volume_icon.setFont(QFont("SF Pro Display", 12))
        volume_icon.setStyleSheet("background: transparent; color: rgba(255, 255, 255, 0.7);")
        play_layout.addWidget(volume_icon)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.setFixedWidth(80)
        self.volume_slider.valueChanged.connect(self._on_volume_changed)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 3px;
                background: rgba(80, 80, 80, 0.5);
                border-radius: 1px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                width: 10px;
                height: 10px;
                margin: -4px 0;
                border-radius: 5px;
                border: none;
            }
            QSlider::handle:horizontal:hover {
                background: #e0e0e0;
                width: 12px;
                height: 12px;
                margin: -5px 0;
                border-radius: 6px;
            }
            QSlider::sub-page:horizontal {
                background: #ffffff;
                border-radius: 1px;
            }
        """)
        play_layout.addWidget(self.volume_slider)
        
        play_layout.addStretch()
        
        layout.addLayout(play_layout)
    
    def update_now_playing(self, title: str, artist: str, cover: QPixmap = None) -> None:
        """更新正在播放信息
        
        Args:
            title: 标题
            artist: 艺术家
            cover: 封面图片
        """
        # 截断过长的文本
        max_title_length = 25
        max_artist_length = 30
        
        display_title = title if len(title) <= max_title_length else title[:max_title_length] + "..."
        display_artist = artist if len(artist) <= max_artist_length else artist[:max_artist_length] + "..."
        
        self.song_label.setText(display_title)
        self.artist_label.setText(display_artist)
        
        if cover and not cover.isNull():
            scaled_cover = cover.scaled(
                60, 60, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            self.cover_label.setPixmap(scaled_cover)
        else:
            self.cover_label.clear()
            self.cover_label.setText("♪")
    
    def clear_now_playing(self) -> None:
        """清空正在播放信息"""
        self.song_label.setText("未播放")
        self.artist_label.setText("")
        self.time_label.setText("00:00 / 00:00")
        self.cover_label.clear()
        self.cover_label.setText("♪")
    
    def update_play_button(self, is_playing: bool) -> None:
        """更新播放按钮状态
        
        Args:
            is_playing: 是否正在播放
        """
        if is_playing:
            self.play_btn.setText("⏸")
        else:
            self.play_btn.setText("▶")
    
    def update_time(self, current: str, total: str) -> None:
        """更新时间显示
        
        Args:
            current: 当前时间
            total: 总时长
        """
        self.time_label.setText(f"{current} / {total}")
    
    def set_volume(self, volume: int) -> None:
        """设置音量
        
        Args:
            volume: 音量（0-100）
        """
        self.volume_slider.setValue(volume)
    
    def _on_volume_changed(self, value: int) -> None:
        """音量改变"""
        self.volume_changed.emit(value / 100.0)
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """鼠标按下事件 - 开始拖动"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """鼠标移动事件 - 拖动窗口"""
        if self._dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """鼠标释放事件 - 结束拖动"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            event.accept()
