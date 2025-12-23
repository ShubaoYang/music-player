"""播放模式枚举"""

from enum import Enum


class PlaybackMode(Enum):
    """播放模式"""
    SEQUENTIAL = "sequential"  # 顺序播放
    LOOP = "loop"              # 列表循环
    SHUFFLE = "shuffle"        # 随机播放
    SINGLE_REPEAT = "single"   # 单曲循环
