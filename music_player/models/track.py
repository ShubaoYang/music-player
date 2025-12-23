"""音轨和元数据数据模型"""

import os
from dataclasses import dataclass
from typing import Optional
from PyQt5.QtGui import QPixmap


@dataclass
class Metadata:
    """音频元数据"""
    title: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    duration: float = 0.0
    cover_art: Optional[QPixmap] = None


@dataclass
class Track:
    """音轨"""
    file_path: str
    title: str
    artist: str
    album: str
    duration: float  # in seconds
    cover_art: Optional[QPixmap] = None
    
    def get_display_name(self) -> str:
        """返回用于显示的名称"""
        if self.title and self.artist:
            return f"{self.artist} - {self.title}"
        return os.path.basename(self.file_path)
    
    def get_duration_string(self) -> str:
        """返回格式化的时长字符串 MM:SS"""
        if self.duration <= 0:
            return "--:--"
        minutes = int(self.duration // 60)
        seconds = int(self.duration % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    @staticmethod
    def format_time(seconds: float) -> str:
        """格式化时间为 MM:SS"""
        if seconds < 0:
            seconds = 0
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
