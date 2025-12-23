"""播放列表管理器"""

import os
import json
import random
from typing import List, Optional
from PyQt5.QtCore import QObject, pyqtSignal

from .track import Track
from .playback_mode import PlaybackMode


class PlaylistManager(QObject):
    """管理播放列表和播放顺序"""
    
    # 信号
    playlist_changed = pyqtSignal()  # 播放列表变化
    play_mode_changed = pyqtSignal(PlaybackMode)  # 播放模式变化
    
    def __init__(self):
        """初始化播放列表管理器"""
        super().__init__()
        self._tracks: List[Track] = []
        self._play_mode = PlaybackMode.SEQUENTIAL
        self._shuffle_order: List[int] = []
        self._shuffle_index = 0
    
    def add_track(self, track: Track) -> None:
        """添加音轨
        
        Args:
            track: 音轨对象
        """
        self._tracks.append(track)
        self.playlist_changed.emit()
    
    def add_tracks(self, tracks: List[Track]) -> None:
        """批量添加音轨
        
        Args:
            tracks: 音轨列表
        """
        self._tracks.extend(tracks)
        self.playlist_changed.emit()
    
    def remove_track(self, index: int) -> None:
        """删除音轨
        
        Args:
            index: 音轨索引
        """
        if 0 <= index < len(self._tracks):
            self._tracks.pop(index)
            self.playlist_changed.emit()
    
    def clear(self) -> None:
        """清空播放列表"""
        self._tracks.clear()
        self._shuffle_order.clear()
        self.playlist_changed.emit()
    
    def move_track(self, from_index: int, to_index: int) -> None:
        """移动音轨
        
        Args:
            from_index: 源索引
            to_index: 目标索引
        """
        if 0 <= from_index < len(self._tracks) and 0 <= to_index < len(self._tracks):
            track = self._tracks.pop(from_index)
            self._tracks.insert(to_index, track)
            self.playlist_changed.emit()
    
    def get_track(self, index: int) -> Optional[Track]:
        """获取音轨
        
        Args:
            index: 音轨索引
            
        Returns:
            音轨对象或 None
        """
        if 0 <= index < len(self._tracks):
            return self._tracks[index]
        return None
    
    def get_all_tracks(self) -> List[Track]:
        """获取所有音轨
        
        Returns:
            音轨列表
        """
        return self._tracks.copy()
    
    def get_track_count(self) -> int:
        """获取音轨数量
        
        Returns:
            音轨数量
        """
        return len(self._tracks)
    
    def set_play_mode(self, mode: PlaybackMode) -> None:
        """设置播放模式
        
        Args:
            mode: 播放模式
        """
        self._play_mode = mode
        
        # 如果切换到随机模式，生成随机顺序
        if mode == PlaybackMode.SHUFFLE:
            self._generate_shuffle_order()
        
        self.play_mode_changed.emit(mode)
    
    def get_play_mode(self) -> PlaybackMode:
        """获取当前播放模式
        
        Returns:
            播放模式
        """
        return self._play_mode
    
    def get_next_track(self, current_index: int) -> Optional[int]:
        """获取下一首音轨索引
        
        Args:
            current_index: 当前音轨索引
            
        Returns:
            下一首音轨索引或 None
        """
        if not self._tracks:
            return None
        
        if self._play_mode == PlaybackMode.SINGLE_REPEAT:
            return current_index
        
        elif self._play_mode == PlaybackMode.SHUFFLE:
            if not self._shuffle_order:
                self._generate_shuffle_order()
            
            self._shuffle_index = (self._shuffle_index + 1) % len(self._shuffle_order)
            return self._shuffle_order[self._shuffle_index]
        
        elif self._play_mode == PlaybackMode.LOOP:
            return (current_index + 1) % len(self._tracks)
        
        else:  # SEQUENTIAL
            next_index = current_index + 1
            if next_index < len(self._tracks):
                return next_index
            return None
    
    def get_previous_track(self, current_index: int) -> Optional[int]:
        """获取上一首音轨索引
        
        Args:
            current_index: 当前音轨索引
            
        Returns:
            上一首音轨索引或 None
        """
        if not self._tracks:
            return None
        
        if self._play_mode == PlaybackMode.SINGLE_REPEAT:
            return current_index
        
        elif self._play_mode == PlaybackMode.SHUFFLE:
            if not self._shuffle_order:
                self._generate_shuffle_order()
            
            self._shuffle_index = (self._shuffle_index - 1) % len(self._shuffle_order)
            return self._shuffle_order[self._shuffle_index]
        
        else:  # SEQUENTIAL or LOOP
            return (current_index - 1) % len(self._tracks)
    
    def filter_tracks(self, search_term: str) -> List[Track]:
        """过滤音轨
        
        Args:
            search_term: 搜索词
            
        Returns:
            匹配的音轨列表
        """
        if not search_term:
            return self._tracks.copy()
        
        search_lower = search_term.lower()
        filtered = []
        
        for track in self._tracks:
            # 搜索文件名、标题、艺术家、专辑
            if (search_lower in os.path.basename(track.file_path).lower() or
                search_lower in track.title.lower() or
                search_lower in track.artist.lower() or
                search_lower in track.album.lower()):
                filtered.append(track)
        
        return filtered
    
    def save_playlist(self, name: str, file_path: str) -> None:
        """保存播放列表
        
        Args:
            name: 播放列表名称
            file_path: 保存路径
        """
        playlist_data = {
            "name": name,
            "tracks": [track.file_path for track in self._tracks]
        }
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(playlist_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存播放列表失败: {e}")
    
    def load_playlist(self, file_path: str) -> List[str]:
        """加载播放列表
        
        Args:
            file_path: 播放列表文件路径
            
        Returns:
            音轨文件路径列表
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                playlist_data = json.load(f)
                return playlist_data.get("tracks", [])
        except Exception as e:
            print(f"加载播放列表失败: {e}")
            return []
    
    def _generate_shuffle_order(self) -> None:
        """生成随机播放顺序"""
        self._shuffle_order = list(range(len(self._tracks)))
        random.shuffle(self._shuffle_order)
        self._shuffle_index = 0
