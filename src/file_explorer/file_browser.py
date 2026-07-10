import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeView, 
                             QListView, QSplitter, QLineEdit, QPushButton, 
                             QLabel, QFileSystemModel, QHeaderView, QMessageBox,
                             QComboBox, QToolButton, QMenu, QAction, QSizePolicy)
from PyQt5.QtCore import Qt, QSize, QModelIndex, QFileInfo, QDir
from PyQt5.QtGui import QIcon, QFont, QStandardItemModel, QStandardItem
from src.file_explorer.file_preview import FilePreview


class FileBrowser(QWidget):
    def __init__(self):
        super().__init__()
        self.current_path = os.path.expanduser("~")
        self.current_sort_by = "name"
        self.current_view_mode = "icon"
        self.init_ui()
        self.navigate_to(self.current_path)
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        
        # 导航栏
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(4)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        
        self.back_btn = QPushButton("←")
        self.back_btn.setFixedSize(28, 24)
        self.back_btn.setStyleSheet("padding: 0px; margin: 0px; font-size: 12px;")
        self.back_btn.clicked.connect(self.go_back)
        nav_layout.addWidget(self.back_btn)
        
        self.forward_btn = QPushButton("→")
        self.forward_btn.setFixedSize(28, 24)
        self.forward_btn.setStyleSheet("padding: 0px; margin: 0px; font-size: 12px;")
        self.forward_btn.clicked.connect(self.go_forward)
        nav_layout.addWidget(self.forward_btn)
        
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("路径...")
        self.path_edit.setFixedHeight(24)
        self.path_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.path_edit.setStyleSheet("padding: 0px 6px; margin: 0px; font-size: 12px;")
        self.path_edit.returnPressed.connect(self.navigate_from_edit)
        nav_layout.addWidget(self.path_edit)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索...")
        self.search_edit.setFixedHeight(24)
        self.search_edit.setMinimumWidth(120)
        self.search_edit.setMaximumWidth(140)
        self.search_edit.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.search_edit.setStyleSheet("padding: 0px 6px; margin: 0px; font-size: 12px;")
        self.search_edit.textChanged.connect(self.filter_files)
        nav_layout.addWidget(self.search_edit)
        
        layout.addLayout(nav_layout)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(6)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)
        
        sort_label = QLabel("排序:")
        sort_label.setStyleSheet("font-size: 12px; margin: 0px; padding: 0px;")
        toolbar_layout.addWidget(sort_label)
        
        self.sort_combo = QComboBox()
        self.sort_combo.setFixedHeight(24)
        self.sort_combo.setMinimumWidth(90)
        self.sort_combo.setStyleSheet("""
            QComboBox {
                padding: 0px 6px;
                margin: 0px;
                font-size: 12px;
                border: 1px solid #ccc;
            }
            QComboBox::drop-down {
                width: 18px;
                border: none;
            }
        """)
        self.sort_combo.addItems(["名称", "时间", "大小", "类型"])
        self.sort_combo.currentTextChanged.connect(self.on_sort_changed)
        toolbar_layout.addWidget(self.sort_combo)
        
        view_label = QLabel("视图:")
        view_label.setStyleSheet("font-size: 12px; margin: 0px 0px 0px 10px; padding: 0px;")
        toolbar_layout.addWidget(view_label)
        
        self.icon_view_btn = QPushButton("🗀")
        self.icon_view_btn.setCheckable(True)
        self.icon_view_btn.setChecked(True)
        self.icon_view_btn.setFixedSize(24, 24)
        self.icon_view_btn.setStyleSheet("padding: 0px; margin: 0px; font-size: 12px;")
        self.icon_view_btn.setToolTip("缩略图")
        self.icon_view_btn.clicked.connect(lambda: self.set_view_mode("icon"))
        toolbar_layout.addWidget(self.icon_view_btn)
        
        self.list_view_btn = QPushButton("📋")
        self.list_view_btn.setCheckable(True)
        self.list_view_btn.setFixedSize(24, 24)
        self.list_view_btn.setStyleSheet("padding: 0px; margin: 0px; font-size: 12px;")
        self.list_view_btn.setToolTip("列表")
        self.list_view_btn.clicked.connect(lambda: self.set_view_mode("list"))
        toolbar_layout.addWidget(self.list_view_btn)
        
        toolbar_layout.addStretch()
        
        self.file_count_label = QLabel("共 0 项")
        self.file_count_label.setStyleSheet("font-size: 12px; color: #666; margin: 0px; padding: 0px;")
        toolbar_layout.addWidget(self.file_count_label)
        
        layout.addLayout(toolbar_layout)
        
        # 主内容区 - 使用 splitter
        splitter = QSplitter(Qt.Horizontal)
        
        self.tree_view = QTreeView()
        self.setup_tree_view()
        splitter.addWidget(self.tree_view)
        splitter.setStretchFactor(0, 1)
        
        right_splitter = QSplitter(Qt.Vertical)
        
        self.list_view = QListView()
        self.setup_list_view()
        right_splitter.addWidget(self.list_view)
        right_splitter.setStretchFactor(0, 2)
        
        self.preview = FilePreview()
        right_splitter.addWidget(self.preview)
        right_splitter.setStretchFactor(1, 1)
        
        splitter.addWidget(right_splitter)
        splitter.setStretchFactor(1, 3)
        
        # 关键：让 splitter 占据所有剩余空间
        layout.addWidget(splitter, 1)
        
        self.history = []
        self.history_index = -1
        
        # 设置 FileBrowser 的 size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
    def setup_tree_view(self):
        self.dir_model = QFileSystemModel()
        self.dir_model.setRootPath("")
        self.dir_model.setFilter(QDir.Dirs | QDir.NoDotAndDotDot | QDir.AllDirs)
        self.tree_view.setModel(self.dir_model)
        self.tree_view.hideColumn(1)
        self.tree_view.hideColumn(2)
        self.tree_view.hideColumn(3)
        self.tree_view.clicked.connect(self.on_tree_clicked)
        self.tree_view.setStyleSheet("font-size: 12px;")
        
    def setup_list_view(self):
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath("")
        self.file_model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)
        self.list_view.setModel(self.file_model)
        self.set_view_mode("icon")
        self.list_view.setSelectionMode(QListView.SingleSelection)
        self.list_view.setFocusPolicy(Qt.StrongFocus)
        
        self.list_view.clicked.connect(self.on_file_clicked)
        self.list_view.selectionModel().currentChanged.connect(self.on_current_changed)
        self.list_view.doubleClicked.connect(self.on_file_double_clicked)
        
    def set_view_mode(self, mode):
        """设置视图模式"""
        self.current_view_mode = mode
        
        if mode == "icon":
            self.list_view.setViewMode(QListView.IconMode)
            self.list_view.setIconSize(QSize(64, 64))
            self.list_view.setGridSize(QSize(100, 100))
            self.list_view.setSpacing(5)
            self.list_view.setWordWrap(True)
            self.list_view.setResizeMode(QListView.Adjust)
            self.icon_view_btn.setChecked(True)
            self.list_view_btn.setChecked(False)
        else:
            self.list_view.setViewMode(QListView.ListMode)
            self.list_view.setIconSize(QSize(24, 24))
            self.list_view.setGridSize(QSize(-1, 28))
            self.list_view.setSpacing(0)
            self.list_view.setWordWrap(False)
            self.list_view.setResizeMode(QListView.Fixed)
            self.icon_view_btn.setChecked(False)
            self.list_view_btn.setChecked(True)
        
        self.refresh_view()
        
    def on_sort_changed(self, text):
        """排序方式改变"""
        sort_map = {
            "名称": "name",
            "时间": "time",
            "大小": "size",
            "类型": "type"
        }
        self.current_sort_by = sort_map.get(text, "name")
        self.apply_sort_mode()
        self.refresh_view()
        
    def apply_sort_mode(self):
        """应用排序模式"""
        if not self.list_view.model():
            return
            
        if self.current_sort_by == "name":
            self.file_model.setSortCaseSensitivity(Qt.CaseInsensitive)
            self.list_view.model().sort(0, Qt.AscendingOrder)
        elif self.current_sort_by == "time":
            self.list_view.model().sort(3, Qt.DescendingOrder)
        elif self.current_sort_by == "size":
            self.list_view.model().sort(2, Qt.DescendingOrder)
        elif self.current_sort_by == "type":
            self.list_view.model().sort(1, Qt.AscendingOrder)
            
    def refresh_view(self):
        """刷新视图"""
        index = self.file_model.index(self.current_path)
        self.list_view.setRootIndex(index)
        
        count = self.file_model.rowCount(index)
        self.file_count_label.setText(f"共 {count} 项")
        
    def on_current_changed(self, current, previous):
        """当列表视图中选中项改变时"""
        if current.isValid():
            path = self.file_model.filePath(current)
            self.preview.preview_file(path)
        
    def navigate_to(self, path):
        if not os.path.exists(path):
            return
            
        self.current_path = path
        self.path_edit.setText(path)
        
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        self.history.append(path)
        self.history_index = len(self.history) - 1
        
        index = self.file_model.setRootPath(path)
        self.list_view.setRootIndex(index)
        
        count = self.file_model.rowCount(index)
        self.file_count_label.setText(f"共 {count} 项")
        
        tree_index = self.dir_model.index(path)
        self.tree_view.expand(tree_index)
        self.tree_view.setCurrentIndex(tree_index)
        
    def navigate_from_edit(self):
        path = self.path_edit.text()
        self.navigate_to(path)
        
    def on_tree_clicked(self, index):
        path = self.dir_model.filePath(index)
        self.navigate_to(path)
        
    def on_file_clicked(self, index):
        path = self.file_model.filePath(index)
        self.preview.preview_file(path)
        
    def on_file_double_clicked(self, index):
        path = self.file_model.filePath(index)
        if os.path.isdir(path):
            self.navigate_to(path)
            
    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            path = self.history[self.history_index]
            self.current_path = path
            self.path_edit.setText(path)
            index = self.file_model.setRootPath(path)
            self.list_view.setRootIndex(index)
            
    def go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            path = self.history[self.history_index]
            self.current_path = path
            self.path_edit.setText(path)
            index = self.file_model.setRootPath(path)
            self.list_view.setRootIndex(index)
            
    def filter_files(self, text):
        if text:
            self.file_model.setNameFilters([f"*{text}*"])
            self.file_model.setNameFilterDisables(False)
        else:
            self.file_model.setNameFilters([])
            
    def refresh(self):
        self.navigate_to(self.current_path)
