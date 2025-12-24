"""播放引擎"""

import os
from typing import Optional, List
from PySide6.QtCore import QObject, Signal, QTimer
from pygame import mixer
import time


class PlaybackEngine(QObject):
    """音频播放引擎"""
    
    # 信号
    track_finished = Signal()  # 曲目播放完成
    position_changed = Signal(float)  # 播放位置变化
    state_changed = Signal(str)  # 播放状态变化
    
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
        
        # 创建定时器检测播放结束
        self._check_timer = QTimer()
        self._check_timer.timeout.connect(self._check_playback_finished)
        self._check_timer.start(500)  # 每500ms检查一次
    
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
            error_msg = str(e)
            # 简化 FLAC 错误信息
            if "FLAC" in error_msg:
                print(f"加载音轨失败: FLAC 文件可能损坏或格式不支持 - {os.path.basename(file_path)}")
            else:
                print(f"加载音轨失败: {error_msg}")
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
            # 先获取当前位置再暂停
            current_pos = time.time() - self._start_time
            mixer.music.pause()
            self._is_paused = True
            self._pause_position = current_pos
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
        if not self._current_file:
            return
            
        was_playing = self._is_playing and not self._is_paused
        
        try:
            # 停止当前播放
            mixer.music.stop()
            
            # 重新加载文件
            mixer.music.load(self._current_file)
            
            # 尝试使用 set_pos (仅支持 MP3/OGG)
            try:
                mixer.music.set_pos(position)
                mixer.music.play()
            except:
                # 如果 set_pos 不支持，使用 start 参数
                mixer.music.play(start=position)
            
            # 更新时间基准
            self._start_time = time.time() - position
            self._is_playing = True
            self._is_paused = False
            
            # 如果之前是暂停状态，立即暂停
            if not was_playing:
                mixer.music.pause()
                self._is_paused = True
                self._pause_position = position
                
        except Exception as e:
            print(f"跳转失败: {e}")
    
    def load_and_set_position(self, file_path: str, position: float = 0.0) -> bool:
        """加载音轨并设置到指定位置（暂停状态）
        
        Args:
            file_path: 音频文件路径
            position: 起始位置（秒）
            
        Returns:
            是否加载成功
        """
        try:
            mixer.music.load(file_path)
            self._current_file = file_path
            
            if position > 0:
                # 从指定位置开始播放然后立即暂停
                mixer.music.play(start=position)
                mixer.music.pause()
                self._is_playing = True
                self._is_paused = True
                self._pause_position = position
                self._start_time = time.time() - position
            else:
                # 位置为0，只是加载不播放
                self._is_playing = False
                self._is_paused = False
                self._pause_position = 0.0
                self._start_time = 0.0
                
            return True
        except Exception as e:
            print(f"加载音轨失败: {e}")
            return False
    
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
    
    def _check_playback_finished(self) -> None:
        """检查播放是否结束"""
        if self._is_playing and not self._is_paused:
            # 检查 pygame mixer 是否还在播放
            if not mixer.music.get_busy():
                # 播放已结束
                self._is_playing = False
                self._is_paused = False
                self.state_changed.emit("stopped")
                self.track_finished.emit()
