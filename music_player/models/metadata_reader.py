"""元数据读取器"""

import os
from typing import Optional, Dict
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QByteArray
from mutagen import File as MutagenFile
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis

from .track import Metadata


class MetadataReader:
    """读取音频文件的元数据"""
    
    def __init__(self):
        """初始化元数据读取器"""
        self._cache: Dict[str, Metadata] = {}
    
    def read_metadata(self, file_path: str) -> Metadata:
        """读取音频文件元数据
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            元数据对象
        """
        # 检查缓存
        if file_path in self._cache:
            return self._cache[file_path]
        
        metadata = Metadata()
        
        try:
            audio = MutagenFile(file_path, easy=True)
            
            if audio is None:
                # 无法读取元数据，使用文件名
                metadata.title = os.path.splitext(os.path.basename(file_path))[0]
                metadata.duration = self.get_duration(file_path)
            else:
                # 提取标题
                if 'title' in audio and audio['title']:
                    metadata.title = audio['title'][0]
                else:
                    metadata.title = os.path.splitext(os.path.basename(file_path))[0]
                
                # 提取艺术家
                if 'artist' in audio and audio['artist']:
                    metadata.artist = audio['artist'][0]
                
                # 提取专辑
                if 'album' in audio and audio['album']:
                    metadata.album = audio['album'][0]
                
                # 提取时长
                metadata.duration = self.get_duration(file_path)
                
                # 提取封面
                metadata.cover_art = self.get_cover_art(file_path)
        
        except Exception as e:
            print(f"读取元数据失败 {file_path}: {e}")
            metadata.title = os.path.splitext(os.path.basename(file_path))[0]
            metadata.duration = self.get_duration(file_path)
        
        # 缓存元数据
        self._cache[file_path] = metadata
        return metadata
    
    def get_duration(self, file_path: str) -> float:
        """获取音频文件时长
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            时长（秒）
        """
        try:
            audio = MutagenFile(file_path)
            if audio is not None and hasattr(audio.info, 'length'):
                return float(audio.info.length)
        except Exception as e:
            print(f"获取时长失败 {file_path}: {e}")
        
        return 0.0
    
    def get_cover_art(self, file_path: str) -> Optional[QPixmap]:
        """获取专辑封面
        
        Args:
            file_path: 音频文件路径
            
        Returns:
            封面图片或 None
        """
        try:
            audio = MutagenFile(file_path)
            
            if audio is None:
                return None
            
            # MP3 文件
            if isinstance(audio, MP3):
                for tag in audio.tags.values():
                    if hasattr(tag, 'mime') and tag.mime.startswith('image/'):
                        pixmap = QPixmap()
                        pixmap.loadFromData(QByteArray(tag.data))
                        return pixmap
            
            # FLAC 文件
            elif isinstance(audio, FLAC):
                if audio.pictures:
                    picture = audio.pictures[0]
                    pixmap = QPixmap()
                    pixmap.loadFromData(QByteArray(picture.data))
                    return pixmap
            
            # OGG 文件
            elif isinstance(audio, OggVorbis):
                if 'metadata_block_picture' in audio:
                    import base64
                    from mutagen.flac import Picture
                    picture_data = base64.b64decode(audio['metadata_block_picture'][0])
                    picture = Picture(picture_data)
                    pixmap = QPixmap()
                    pixmap.loadFromData(QByteArray(picture.data))
                    return pixmap
        
        except Exception as e:
            print(f"获取封面失败 {file_path}: {e}")
        
        return None
    
    def clear_cache(self) -> None:
        """清空元数据缓存"""
        self._cache.clear()
