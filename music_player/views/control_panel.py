"""控制面板视图"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QSlider, QLabel)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont

from ..models.track import Track


class ControlPanel(QWidget):
    """播放控制面板"""
    
    # 信号
    play_pause_clicked = Signal()
    prev_clicked = Signal()
    next_clicked = Signal()
    seek_requested = Signal(float)
    volume_changed = Signal(float)
    
    def __init__(self):
        """初始化控制面板"""
        super().__init__()
        self._is_seeking = False
        self._duration = 0.0
        self.init_ui()
    
    def init_ui(self) -> None:
        """初始化界面"""
        # 主容器
        container = QWidget()
        container.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(102, 126, 234, 0.15), stop:1 rgba(118, 75, 162, 0.15));
            border-radius: 15px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 20px;
        """)
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.addWidget(container)
        
        inner_layout = QVBoxLayout(container)
        inner_layout.setSpacing(15)
        
        # 时间标签
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setFont(QFont("Helvetica Neue", 12, QFont.Weight.Bold))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        inner_layout.addWidget(self.time_label)
        
        # 进度条
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 1000)
        self.progress_slider.setValue(0)
        self.progress_slider.sliderPressed.connect(self._on_slider_pressed)
        self.progress_slider.sliderReleased.connect(self._on_slider_released)
        self.progress_slider.sliderMoved.connect(self._on_slider_moved)
        inner_layout.addWidget(self.progress_slider)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        control_layout.setSpacing(15)
        
        # 按钮样式
        button_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                padding: 12px 20px;
                font-size: 13px;
                border-radius: 10px;
                font-weight: 700;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7b8ff7, stop:1 #8a5fb8);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5568d3, stop:1 #63408e);
            }
        """
        
        play_button_style = """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f093fb, stop:1 #f5576c);
                color: white;
                border: none;
                padding: 15px 30px;
                font-size: 15px;
                border-radius: 12px;
                font-weight: 700;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ffa4fc, stop:1 #ff6b7f);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e082ea, stop:1 #e44659);
            }
        """
        
        control_layout.addStretch()
        
        self.prev_btn = QPushButton("⏮")
        self.prev_btn.setStyleSheet(button_style)
        self.prev_btn.clicked.connect(self.prev_clicked.emit)
        control_layout.addWidget(self.prev_btn)
        
        self.play_btn = QPushButton("▶")
        self.play_btn.setStyleSheet(play_button_style)
        self.play_btn.clicked.connect(self.play_pause_clicked.emit)
        control_layout.addWidget(self.play_btn)
        
        self.next_btn = QPushButton("⏭")
        self.next_btn.setStyleSheet(button_style)
        self.next_btn.clicked.connect(self.next_clicked.emit)
        control_layout.addWidget(self.next_btn)
        
        control_layout.addStretch()
        
        inner_layout.addLayout(control_layout)
        
        # 音量控制
        volume_layout = QHBoxLayout()
        volume_label = QLabel("🔊")
        volume_label.setFont(QFont("Helvetica Neue", 16))
        volume_layout.addWidget(volume_label)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.valueChanged.connect(
            lambda v: self.volume_changed.emit(v / 100.0)
        )
        volume_layout.addWidget(self.volume_slider)
        
        self.volume_label = QLabel("70%")
        self.volume_label.setFont(QFont("Helvetica Neue", 11, QFont.Weight.Bold))
        self.volume_label.setStyleSheet("color: rgba(255, 255, 255, 0.7); min-width: 40px;")
        self.volume_slider.valueChanged.connect(lambda v: self.volume_label.setText(f"{v}%"))
        volume_layout.addWidget(self.volume_label)
        
        inner_layout.addLayout(volume_layout)
    
    def update_play_button(self, is_playing: bool) -> None:
        """更新播放按钮状态
        
        Args:
            is_playing: 是否正在播放
        """
        if is_playing:
            self.play_btn.setText("⏸")
        else:
            self.play_btn.setText("▶")
    
    def update_progress(self, position: float, duration: float) -> None:
        """更新进度
        
        Args:
            position: 当前位置（秒）
            duration: 总时长（秒）
        """
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
        current_time = Track.format_time(position)
        total_time = Track.format_time(duration)
        self.time_label.setText(f"{current_time} / {total_time}")
    
    def reset_progress(self) -> None:
        """重置进度"""
        self.progress_slider.setValue(0)
        self.time_label.setText("00:00 / 00:00")
        self._duration = 0.0
    
    def set_volume(self, volume: int) -> None:
        """设置音量
        
        Args:
            volume: 音量（0-100）
        """
        self.volume_slider.setValue(volume)
    
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
            current_time = Track.format_time(position)
            total_time = Track.format_time(self._duration)
            self.time_label.setText(f"{current_time} / {total_time}")
