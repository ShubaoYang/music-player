"""播放引擎"""

import os
import threading
import numpy as np
from typing import Optional, List
from PySide6.QtCore import QObject, Signal, QTimer
import soundfile as sf
import sounddevice as sd


class PlaybackEngine(QObject):
    """音频播放引擎"""
    
    # 信号
    track_finished = Signal()  # 曲目播放完成
    position_changed = Signal(float)  # 播放位置变化
    state_changed = Signal(str)  # 播放状态变化
    
    def __init__(self):
        """初始化播放引擎"""
        super().__init__()
        
        try:
            # 检查音频设备
            devices = sd.query_devices()
            print(f"✓ SoundDevice 音频引擎初始化成功")
            print(f"ℹ️ 找到 {len(devices)} 个音频设备")
        except Exception as e:
            print(f"❌ SoundDevice 初始化失败: {e}")
            raise
        
        self._current_file: Optional[str] = None
        self._audio_data: Optional[np.ndarray] = None
        self._sample_rate: int = 44100
        self._is_playing = False
        self._is_paused = False
        self._duration = 0.0
        self._position = 0.0
        
        # 播放控制
        self._stream = None
        self._play_thread = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._volume = 1.0
        self._current_frame = 0
        
        # 创建定时器检测播放结束
        self._check_timer = QTimer()
        self._check_timer.timeout.connect(self._check_playback_finished)
        self._check_timer.start(100)  # 每100ms检查一次
    
    def load_track(self, file_path: str) -> bool:
        """加载音轨
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            是否加载成功
        """
        try:
            print(f"🎵 尝试加载: {os.path.basename(file_path)}")
            
            # 停止当前播放
            if self._is_playing:
                self.stop()
            
            # 使用 soundfile 加载音频（支持 FLAC, WAV, OGG, MP3 等）
            self._audio_data, self._sample_rate = sf.read(file_path, dtype='float32')
            
            self._current_file = file_path
            self._duration = len(self._audio_data) / self._sample_rate
            self._position = 0.0
            self._current_frame = 0
            
            print(f"✓ 加载成功: {os.path.basename(file_path)} (时长: {self._duration:.2f}秒, 采样率: {self._sample_rate}Hz)")
            return True
            
        except Exception as e:
            print(f"❌ 加载音轨失败: {e} - {os.path.basename(file_path)}")
            return False
    
    def play(self) -> None:
        """播放"""
        if self._audio_data is None:
            return
        
        if self._is_paused:
            # 从暂停恢复
            self._pause_event.clear()
            self._is_paused = False
            self._is_playing = True
            self.state_changed.emit("playing")
        else:
            # 开始新的播放（从当前位置）
            self._stop_event.clear()
            self._pause_event.clear()
            self._is_playing = True
            self._is_paused = False
            
            # 在新线程中播放
            self._play_thread = threading.Thread(target=self._play_audio, daemon=True)
            self._play_thread.start()
            
            self.state_changed.emit("playing")
    
    def pause(self) -> None:
        """暂停"""
        if self._is_playing and not self._is_paused:
            self._pause_event.set()
            self._is_paused = True
            self.state_changed.emit("paused")
    
    def stop(self) -> None:
        """停止"""
        self._stop_event.set()
        self._pause_event.clear()
        self._is_playing = False
        self._is_paused = False
        self._position = 0.0
        self._current_frame = 0
        
        # 停止音频流
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except:
                pass
            self._stream = None
        
        # 等待播放线程结束
        if self._play_thread and self._play_thread.is_alive():
            self._play_thread.join(timeout=1.0)
        
        self.state_changed.emit("stopped")
    
    def seek(self, position: float) -> None:
        """跳转到指定位置
        
        Args:
            position: 位置（秒）
        """
        if self._audio_data is None or position < 0 or position > self._duration:
            return
        
        was_playing = self._is_playing and not self._is_paused
        
        # 停止当前播放（不触发信号）
        self._stop_event.set()
        self._pause_event.clear()
        
        # 停止音频流
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except:
                pass
            self._stream = None
        
        # 等待播放线程结束
        if self._play_thread and self._play_thread.is_alive():
            self._play_thread.join(timeout=0.5)
        
        # 设置新位置
        self._position = position
        self._current_frame = int(position * self._sample_rate)
        
        # 重置标志
        self._stop_event.clear()
        
        # 如果之前在播放，继续播放
        if was_playing:
            self._is_playing = False  # 重置状态
            self._is_paused = False
            self.play()
        else:
            # 如果之前是暂停状态，保持暂停
            self._is_playing = False
            self._is_paused = False
    
    def load_and_set_position(self, file_path: str, position: float = 0.0) -> bool:
        """加载音轨并设置到指定位置（准备播放状态）
        
        Args:
            file_path: 音频文件路径
            position: 起始位置（秒）
            
        Returns:
            是否加载成功
        """
        if self.load_track(file_path):
            # 设置位置
            self._position = min(position, self._duration)
            self._current_frame = int(self._position * self._sample_rate)
            
            # 不设置播放状态，保持加载状态
            # 这样点击播放时会从当前位置开始
            
            print(f"✓ 已加载并设置位置: {os.path.basename(file_path)} 到 {position:.2f}秒")
            return True
        return False
    
    def get_position(self) -> float:
        """获取当前播放位置
        
        Returns:
            当前位置（秒）
        """
        return self._position
    
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
        # soundfile 会自动获取时长，这个方法保留以兼容接口
        pass
    
    def set_volume(self, volume: float) -> None:
        """设置音量
        
        Args:
            volume: 音量（0.0 到 1.0）
        """
        self._volume = max(0.0, min(1.0, volume))
    
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
        return self._is_playing
    
    def set_equalizer(self, bands: List[float]) -> None:
        """设置均衡器
        
        Args:
            bands: 频段增益列表
        """
        pass
    
    def _play_audio(self) -> None:
        """在后台线程中播放音频"""
        playback_completed = False  # 标记是否正常播放完成
        
        try:
            # 从当前帧开始播放
            start_frame = self._current_frame
            total_frames = len(self._audio_data)
            
            # 应用音量
            audio_to_play = self._audio_data[start_frame:].copy()
            if self._volume != 1.0:
                audio_to_play = audio_to_play * self._volume
            
            # 确保是2D数组（即使是单声道）
            if len(audio_to_play.shape) == 1:
                audio_to_play = audio_to_play.reshape(-1, 1)
            
            # 当前播放位置
            current_pos = [0]
            
            def callback(outdata, frames, time_info, status):
                """音频回调函数"""
                if status:
                    print(f"⚠️ 播放状态: {status}")
                
                # 检查停止标志
                if self._stop_event.is_set():
                    raise sd.CallbackStop()
                
                # 检查暂停标志
                if self._pause_event.is_set():
                    outdata.fill(0)  # 静音
                    return
                
                # 计算剩余帧数
                remaining_frames = len(audio_to_play) - current_pos[0]
                
                if remaining_frames <= 0:
                    # 播放完毕
                    outdata.fill(0)
                    raise sd.CallbackStop()
                
                # 复制音频数据
                frames_to_copy = min(frames, remaining_frames)
                outdata[:frames_to_copy] = audio_to_play[current_pos[0]:current_pos[0] + frames_to_copy]
                
                if frames_to_copy < frames:
                    outdata[frames_to_copy:].fill(0)
                
                # 更新位置
                current_pos[0] += frames_to_copy
                self._current_frame = start_frame + current_pos[0]
                self._position = self._current_frame / self._sample_rate
            
            # 创建并启动音频流
            channels = audio_to_play.shape[1]
            
            with sd.OutputStream(
                samplerate=self._sample_rate,
                channels=channels,
                callback=callback,
                blocksize=2048,  # 增加缓冲区大小
                dtype='float32'
            ) as stream:
                # 等待播放完成或被停止
                while stream.active and not self._stop_event.is_set():
                    sd.sleep(100)
            
            # 如果正常播放完毕（不是被停止）
            if not self._stop_event.is_set() and current_pos[0] >= len(audio_to_play):
                playback_completed = True
                self._position = self._duration
                print("🎵 播放线程：音频播放完成")
                
        except sd.CallbackStop:
            pass
        except Exception as e:
            print(f"❌ 播放错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # 线程结束时，如果是正常播放完成，触发信号
            if playback_completed:
                print("🎵 播放线程：准备触发 track_finished 信号")
                # 注意：不要在这里设置 _is_playing = False
                # 让 _check_playback_finished 来处理
    
    def _check_playback_finished(self) -> None:
        """检查播放是否结束"""
        # 检查播放线程是否结束
        if self._play_thread and not self._play_thread.is_alive():
            # 线程已结束
            if self._is_playing:  # 之前是播放状态
                if not self._stop_event.is_set():  # 自然结束，不是被停止
                    print("🎵 检测到播放完成，触发 track_finished 信号")
                    self._is_playing = False
                    self._is_paused = False
                    self.state_changed.emit("stopped")
                    self.track_finished.emit()
                else:
                    # 被手动停止
                    print("⏹ 检测到手动停止")
                    self._is_playing = False
                    self._is_paused = False
