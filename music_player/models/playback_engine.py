"""播放引擎"""

from typing import Optional, List
from PyQt5.QtCore import QObject, pyqtSignal
from pygame import mixer
import time


class PlaybackEngine(QObject):
    """音频播放引擎"""
    
    # 信号
    track_finished = pyqtSignal()  # 曲目播放完成
    position_changed = pyqtSignal(float)  # 播放位置变化
    state_changed = pyqtSignal(str)  # 播放状态变化
    
    def __init__(self):
        """初始化播放引擎"""
        super().__init__()
        mixer.init()
        
        self._current_file: Optional[str] = None
        self._is_playing = False
        self._is_paused = False
        self._duration = 0.0
        self._start_time = 0.0
        self._pause_position = 0.0
    
    def load_track(self, file_path: str) -> bool:
        """加载音轨
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            是否加载成功
        """
        try:
            mixer.music.load(file_path)
            self._current_file = file_path
            self._duration = 0.0  # 将在播放时获取
            return True
        except Exception as e:
            print(f"加载音轨失败: {e}")
            return False
    
    def play(self) -> None:
        """播放"""
        if self._is_paused:
            mixer.music.unpause()
            self._is_paused = False
            self._start_time = time.time() - self._pause_position
        else:
            mixer.music.play()
            self._start_time = time.time()
        
        self._is_playing = True
        self.state_changed.emit("playing")
    
    def pause(self) -> None:
        """暂停"""
        if self._is_playing and not self._is_paused:
            mixer.music.pause()
            self._is_paused = True
            self._pause_position = self.get_position()
            self.state_changed.emit("paused")
    
    def stop(self) -> None:
        """停止"""
        mixer.music.stop()
        self._is_playing = False
        self._is_paused = False
        self._pause_position = 0.0
        self.state_changed.emit("stopped")
    
    def seek(self, position: float) -> None:
        """跳转到指定位置
        
        Args:
            position: 位置（秒）
        """
        # pygame.mixer.music 不支持直接 seek
        # 我们需要重新加载并从指定位置开始播放
        if self._current_file:
            was_playing = self._is_playing and not self._is_paused
            
            try:
                mixer.music.load(self._current_file)
                mixer.music.play(start=position)
                self._start_time = time.time() - position
                
                if not was_playing:
                    mixer.music.pause()
                    self._is_paused = True
                    self._pause_position = position
                else:
                    self._is_playing = True
                    self._is_paused = False
            except Exception as e:
                print(f"跳转失败: {e}")
    
    def get_position(self) -> float:
        """获取当前播放位置
        
        Returns:
            当前位置（秒）
        """
        if self._is_paused:
            return self._pause_position
        elif self._is_playing:
            return time.time() - self._start_time
        return 0.0
    
    def get_duration(self) -> float:
        """获取当前曲目时长
        
        Returns:
            时长（秒）
        """
        return self._duration
    
    def set_duration(self, duration: float) -> None:
        """设置当前曲目时长
        
        Args:
            duration: 时长（秒）
        """
        self._duration = duration
    
    def set_volume(self, volume: float) -> None:
        """设置音量
        
        Args:
            volume: 音量（0.0 到 1.0）
        """
        mixer.music.set_volume(max(0.0, min(1.0, volume)))
    
    def is_playing(self) -> bool:
        """是否正在播放
        
        Returns:
            是否正在播放
        """
        return self._is_playing and not self._is_paused
    
    def is_paused(self) -> bool:
        """是否已暂停
        
        Returns:
            是否已暂停
        """
        return self._is_paused
    
    def is_busy(self) -> bool:
        """检查是否正在播放
        
        Returns:
            是否正在播放
        """
        return mixer.music.get_busy()
    
    def set_equalizer(self, bands: List[float]) -> None:
        """设置均衡器
        
        Args:
            bands: 频段增益列表
        """
        # pygame.mixer 不直接支持均衡器
        # 这里只是占位符，实际实现需要使用其他库
        pass
