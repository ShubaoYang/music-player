"""播放列表视图"""

from typing import List
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QListWidgetItem, QLabel, QLineEdit, QMenu, QAction)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from ..models.track import Track


class PlaylistView(QWidget):
    """播放列表视图"""
    
    # 信号
    track_double_clicked = pyqtSignal(int)
    track_delete_requested = pyqtSignal(int)
    search_changed = pyqtSignal(str)
    
    def __init__(self):
        """初始化播放列表视图"""
        super().__init__()
        self._all_tracks: List[Track] = []
        self._filtered_tracks: List[Track] = []
        self.init_ui()
    
    def init_ui(self) -> None:
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 搜索框
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 搜索:")
        search_label.setFont(QFont("Arial", 10))
        search_layout.addWidget(search_label)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("搜索歌曲、艺术家、专辑...")
        self.search_box.textChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_box)
        
        layout.addLayout(search_layout)
        
        # 播放列表标签
        header_layout = QHBoxLayout()
        
        self.playlist_label = QLabel("播放列表")
        self.playlist_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.playlist_label.setStyleSheet(
            "padding: 5px; background-color: #16213e; border-radius: 5px;"
        )
        header_layout.addWidget(self.playlist_label)
        
        self.count_label = QLabel("0 首歌曲")
        self.count_label.setFont(QFont("Arial", 10))
        self.count_label.setStyleSheet("color: #a0a0a0;")
        header_layout.addWidget(self.count_label)
        
        header_layout.addStretch()
        
        self.duration_label = QLabel("总时长: 00:00")
        self.duration_label.setFont(QFont("Arial", 10))
        self.duration_label.setStyleSheet("color: #a0a0a0;")
        header_layout.addWidget(self.duration_label)
        
        layout.addLayout(header_layout)
        
        # 播放列表
        self.list_widget = QListWidget()
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.list_widget.setDragDropMode(QListWidget.InternalMove)
        layout.addWidget(self.list_widget)
    
    def set_tracks(self, tracks: List[Track]) -> None:
        """设置曲目列表
        
        Args:
            tracks: 曲目列表
        """
        self._all_tracks = tracks
        self._apply_filter()
    
    def update_current_track(self, index: int) -> None:
        """更新当前播放曲目
        
        Args:
            index: 曲目索引
        """
        self.list_widget.setCurrentRow(index)
    
    def clear(self) -> None:
        """清空列表"""
        self._all_tracks.clear()
        self._filtered_tracks.clear()
        self.list_widget.clear()
        self._update_stats()
    
    def _apply_filter(self) -> None:
        """应用过滤"""
        search_term = self.search_box.text().strip()
        
        if not search_term:
            self._filtered_tracks = self._all_tracks.copy()
        else:
            search_lower = search_term.lower()
            self._filtered_tracks = [
                track for track in self._all_tracks
                if (search_lower in track.title.lower() or
                    search_lower in track.artist.lower() or
                    search_lower in track.album.lower() or
                    search_lower in track.file_path.lower())
            ]
        
        self._refresh_list()
        self._update_stats()
    
    def _refresh_list(self) -> None:
        """刷新列表显示"""
        self.list_widget.clear()
        
        for track in self._filtered_tracks:
            display_text = f"{track.get_display_name()}  [{track.get_duration_string()}]"
            item = QListWidgetItem(display_text)
            item.setToolTip(
                f"标题: {track.title}\n"
                f"艺术家: {track.artist}\n"
                f"专辑: {track.album}\n"
                f"时长: {track.get_duration_string()}\n"
                f"路径: {track.file_path}"
            )
            self.list_widget.addItem(item)
    
    def _update_stats(self) -> None:
        """更新统计信息"""
        count = len(self._filtered_tracks)
        self.count_label.setText(f"{count} 首歌曲")
        
        # 计算总时长
        total_duration = sum(track.duration for track in self._filtered_tracks)
        hours = int(total_duration // 3600)
        minutes = int((total_duration % 3600) // 60)
        
        if hours > 0:
            duration_text = f"总时长: {hours}:{minutes:02d}:00"
        else:
            duration_text = f"总时长: {minutes:02d}:00"
        
        self.duration_label.setText(duration_text)
    
    def _on_search_changed(self, text: str) -> None:
        """搜索文本变化"""
        self._apply_filter()
        self.search_changed.emit(text)
    
    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        """列表项双击"""
        index = self.list_widget.row(item)
        # 需要映射到原始索引
        if index >= 0 and index < len(self._filtered_tracks):
            filtered_track = self._filtered_tracks[index]
            original_index = self._all_tracks.index(filtered_track)
            self.track_double_clicked.emit(original_index)
    
    def _show_context_menu(self, position) -> None:
        """显示右键菜单"""
        item = self.list_widget.itemAt(position)
        if item is None:
            return
        
        menu = QMenu(self)
        
        delete_action = QAction("🗑 删除", self)
        delete_action.triggered.connect(lambda: self._delete_selected())
        menu.addAction(delete_action)
        
        menu.exec_(self.list_widget.mapToGlobal(position))
    
    def _delete_selected(self) -> None:
        """删除选中的曲目"""
        current_row = self.list_widget.currentRow()
        if current_row >= 0 and current_row < len(self._filtered_tracks):
            filtered_track = self._filtered_tracks[current_row]
            original_index = self._all_tracks.index(filtered_track)
            self.track_delete_requested.emit(original_index)
