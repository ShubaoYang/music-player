"""控制面板视图"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QSlider, QLabel)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont

from ..models.track import Track


class ControlPanel(QWidget):
    """播放控制面板"""
    
    # 信号
    play_pause_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    prev_clicked = pyqtSignal()
    next_clicked = pyqtSignal()
    seek_requested = pyqtSignal(float)
    volume_changed = pyqtSignal(float)
    
    def __init__(self):
        """初始化控制面板"""
        super().__init__()
        self._is_seeking = False
        self._duration = 0.0
        self.init_ui()
    
    def init_ui(self) -> None:
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 时间标签
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setFont(QFont("Arial", 10))
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("color: #a0a0a0;")
        layout.addWidget(self.time_label)
        
        # 进度条
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 1000)
        self.progress_slider.setValue(0)
        self.progress_slider.sliderPressed.connect(self._on_slider_pressed)
        self.progress_slider.sliderReleased.connect(self._on_slider_released)
        self.progress_slider.sliderMoved.connect(self._on_slider_moved)
        layout.addWidget(self.progress_slider)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        control_layout.setSpacing(10)
        
        self.prev_btn = QPushButton("⏮ 上一首")
        self.prev_btn.clicked.connect(self.prev_clicked.emit)
        control_layout.addWidget(self.prev_btn)
        
        self.play_btn = QPushButton("▶ 播放")
        self.play_btn.clicked.connect(self.play_pause_clicked.emit)
        control_layout.addWidget(self.play_btn)
        
        self.next_btn = QPushButton("⏭ 下一首")
        self.next_btn.clicked.connect(self.next_clicked.emit)
        control_layout.addWidget(self.next_btn)
        
        self.stop_btn = QPushButton("⏹ 停止")
        self.stop_btn.clicked.connect(self.stop_clicked.emit)
        control_layout.addWidget(self.stop_btn)
        
        layout.addLayout(control_layout)
        
        # 音量控制
        volume_layout = QHBoxLayout()
        volume_label = QLabel("🔊 音量")
        volume_label.setFont(QFont("Arial", 10))
        volume_layout.addWidget(volume_label)
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.valueChanged.connect(
            lambda v: self.volume_changed.emit(v / 100.0)
        )
        volume_layout.addWidget(self.volume_slider)
        
        layout.addLayout(volume_layout)
    
    def update_play_button(self, is_playing: bool) -> None:
        """更新播放按钮状态
        
        Args:
            is_playing: 是否正在播放
        """
        if is_playing:
            self.play_btn.setText("⏸ 暂停")
        else:
            self.play_btn.setText("▶ 播放")
    
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
