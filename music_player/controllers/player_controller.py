"""播放器控制器"""

import os
from typing import List, Optional
from PyQt5.QtCore import QObject, pyqtSignal

from ..models.playback_engine import PlaybackEngine
from ..models.playlist_manager import PlaylistManager
from ..models.config_manager import ConfigManager
from ..models.metadata_reader import MetadataReader
from ..models.track import Track
from ..models.playback_mode import PlaybackMode


class PlayerController(QObject):
    """协调各组件之间的交互"""
    
    # 信号
    track_changed = pyqtSignal(int)  # 当前曲目变化
    error_occurred = pyqtSignal(str)  # 错误发生
    
    def __init__(self, engine: PlaybackEngine, playlist: PlaylistManager, 
                 config: ConfigManager, metadata_reader: MetadataReader):
        """初始化控制器
        
        Args:
            engine: 播放引擎
            playlist: 播放列表管理器
            config: 配置管理器
            metadata_reader: 元数据读取器
        """
        super().__init__()
        self.engine = engine
        self.playlist = playlist
        self.config = config
        self.metadata_reader = metadata_reader
        
        self.current_index = -1
        
        # 连接信号
        self.engine.track_finished.connect(self._on_track_finished)
    
    def play_pause(self) -> None:
        """播放/暂停"""
        if self.engine.is_playing():
            self.engine.pause()
        elif self.engine.is_paused():
            self.engine.play()
        else:
            # 如果没有播放，从当前索引开始
            if self.current_index == -1 and self.playlist.get_track_count() > 0:
                self.current_index = 0
            self.play_track_at_index(self.current_index)
    
    def stop(self) -> None:
        """停止播放"""
        self.engine.stop()
    
    def next_track(self) -> None:
        """下一首"""
        next_index = self.playlist.get_next_track(self.current_index)
        if next_index is not None:
            self.play_track_at_index(next_index)
    
    def previous_track(self) -> None:
        """上一首"""
        prev_index = self.playlist.get_previous_track(self.current_index)
        if prev_index is not None:
            self.play_track_at_index(prev_index)
    
    def play_track_at_index(self, index: int) -> None:
        """播放指定索引的曲目
        
        Args:
            index: 曲目索引
        """
        track = self.playlist.get_track(index)
        if track is None:
            return
        
        # 检查文件是否存在
        if not os.path.exists(track.file_path):
            self.error_occurred.emit(f"文件不存在: {track.file_path}")
            # 跳到下一首
            self.next_track()
            return
        
        # 加载并播放
        if self.engine.load_track(track.file_path):
            self.engine.set_duration(track.duration)
            self.engine.play()
            self.current_index = index
            self.track_changed.emit(index)
        else:
            self.error_occurred.emit(f"无法播放: {track.file_path}")
            # 跳到下一首
            self.next_track()
    
    def seek(self, position: float) -> None:
        """跳转到指定位置
        
        Args:
            position: 位置（秒）
        """
        self.engine.seek(position)
    
    def set_volume(self, volume: float) -> None:
        """设置音量
        
        Args:
            volume: 音量（0.0 到 1.0）
        """
        self.engine.set_volume(volume)
    
    def set_play_mode(self, mode: PlaybackMode) -> None:
        """设置播放模式
        
        Args:
            mode: 播放模式
        """
        self.playlist.set_play_mode(mode)
    
    def add_tracks(self, file_paths: List[str]) -> None:
        """添加曲目
        
        Args:
            file_paths: 文件路径列表
        """
        tracks = []
        for file_path in file_paths:
            if os.path.exists(file_path):
                metadata = self.metadata_reader.read_metadata(file_path)
                track = Track(
                    file_path=file_path,
                    title=metadata.title or os.path.splitext(os.path.basename(file_path))[0],
                    artist=metadata.artist or "未知艺术家",
                    album=metadata.album or "未知专辑",
                    duration=metadata.duration,
                    cover_art=metadata.cover_art
                )
                tracks.append(track)
        
        self.playlist.add_tracks(tracks)
    
    def remove_track(self, index: int) -> None:
        """删除曲目
        
        Args:
            index: 曲目索引
        """
        # 如果删除的是当前播放的曲目
        if index == self.current_index:
            self.engine.stop()
            self.current_index = -1
        elif index < self.current_index:
            # 如果删除的曲目在当前曲目之前，调整索引
            self.current_index -= 1
        
        self.playlist.remove_track(index)
    
    def save_state(self) -> None:
        """保存当前状态"""
        config = {
            "volume": int(self.engine.is_playing() and 100 or 70),  # 简化处理
            "playback_mode": self.playlist.get_play_mode().value,
            "current_track_index": self.current_index,
            "current_position": self.engine.get_position(),
            "playlist": [track.file_path for track in self.playlist.get_all_tracks()]
        }
        self.config.save_config(config)
    
    def restore_state(self) -> None:
        """恢复状态"""
        config = self.config.load_config()
        
        # 恢复播放模式
        mode_str = config.get("playback_mode", "sequential")
        try:
            mode = PlaybackMode(mode_str)
            self.playlist.set_play_mode(mode)
        except ValueError:
            pass
        
        # 恢复播放列表
        playlist_paths = config.get("playlist", [])
        if playlist_paths:
            self.add_tracks(playlist_paths)
        
        # 恢复当前曲目索引
        self.current_index = config.get("current_track_index", -1)
    
    def _on_track_finished(self) -> None:
        """曲目播放完成处理"""
        # 根据播放模式决定下一步
        next_index = self.playlist.get_next_track(self.current_index)
        if next_index is not None:
            self.play_track_at_index(next_index)
        else:
            # 顺序播放模式下，播放完最后一首就停止
            self.engine.stop()
