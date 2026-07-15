import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QListWidget, QListWidgetItem, QLabel, QFileDialog, QMessageBox,
                             QGroupBox, QCheckBox, QSpinBox, QComboBox, QProgressBar,
                             QInputDialog, QAbstractItemView)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon
from PIL import Image


class ImageToPDFWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.image_files = []
        self.drag_start_row = -1  # 记录拖拽开始的行
        self.init_ui()
        self.setWindowTitle("图片转PDF工具")
        self.setGeometry(100, 100, 900, 700)
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # 标题
        title_label = QLabel("图片转PDF工具")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title_label)
        
        # 按钮区域 - 纯文字按钮
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("添加图片")
        self.add_btn.clicked.connect(self.add_images)
        self.add_btn.setMinimumHeight(40)
        self.add_btn.setStyleSheet("padding: 0 15px;")
        button_layout.addWidget(self.add_btn)
        
        self.batch_add_btn = QPushButton("批量导入文件夹")
        self.batch_add_btn.clicked.connect(self.batch_add_images)
        self.batch_add_btn.setMinimumHeight(40)
        self.batch_add_btn.setStyleSheet("padding: 0 15px;")
        button_layout.addWidget(self.batch_add_btn)
        
        self.remove_btn = QPushButton("移除选中")
        self.remove_btn.clicked.connect(self.remove_selected)
        self.remove_btn.setMinimumHeight(40)
        self.remove_btn.setStyleSheet("padding: 0 15px;")
        button_layout.addWidget(self.remove_btn)
        
        self.clear_btn = QPushButton("清空全部")
        self.clear_btn.clicked.connect(self.clear_all)
        self.clear_btn.setMinimumHeight(40)
        self.clear_btn.setStyleSheet("padding: 0 15px;")
        button_layout.addWidget(self.clear_btn)
        
        layout.addLayout(button_layout)
        
        # 图片列表区域
        list_group = QGroupBox("待转换图片列表")
        list_layout = QVBoxLayout()
        
        # 移动按钮区域
        move_btn_layout = QHBoxLayout()
        move_btn_layout.addStretch()
        
        self.move_up_btn = QPushButton("上移")
        self.move_up_btn.clicked.connect(self.move_up)
        self.move_up_btn.setMinimumWidth(80)
        self.move_up_btn.setStyleSheet("padding: 5px 15px;")
        move_btn_layout.addWidget(self.move_up_btn)
        
        self.move_down_btn = QPushButton("下移")
        self.move_down_btn.clicked.connect(self.move_down)
        self.move_down_btn.setMinimumWidth(80)
        self.move_down_btn.setStyleSheet("padding: 5px 15px;")
        move_btn_layout.addWidget(self.move_down_btn)
        
        move_btn_layout.addStretch()
        list_layout.addLayout(move_btn_layout)
        
        # 图片列表
        self.image_list = QListWidget()
        self.image_list.setSelectionMode(QListWidget.ExtendedSelection)  # 支持Ctrl/Shift多选
        self.image_list.setViewMode(QListWidget.IconMode)
        self.image_list.setIconSize(QSize(100, 100))
        self.image_list.setSpacing(10)
        
        list_layout.addWidget(self.image_list)
        
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # 设置区域
        settings_group = QGroupBox("PDF设置")
        settings_layout = QVBoxLayout()
        
        # 输出文件名
        filename_layout = QHBoxLayout()
        filename_layout.addWidget(QLabel("输出文件名:"))
        self.filename_edit = QLabel("output.pdf")
        self.filename_edit.setStyleSheet("font-weight: bold; color: #2196F3;")
        filename_layout.addWidget(self.filename_edit)
        self.custom_name_btn = QPushButton("自定义")
        self.custom_name_btn.clicked.connect(self.set_custom_filename)
        self.custom_name_btn.setStyleSheet("padding: 0 15px;")
        filename_layout.addWidget(self.custom_name_btn)
        filename_layout.addStretch()
        settings_layout.addLayout(filename_layout)
        
        # 图片质量
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("图片质量:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["低 (适合小文件)", "中 (平衡)", "高 (最佳质量)"])
        self.quality_combo.setCurrentIndex(1)
        settings_layout.addLayout(quality_layout)
        
        # 页面方向
        orientation_layout = QHBoxLayout()
        orientation_layout.addWidget(QLabel("页面方向:"))
        self.orientation_combo = QComboBox()
        self.orientation_combo.addItems(["自动 (保持原图方向)", "纵向", "横向"])
        settings_layout.addLayout(orientation_layout)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("准备就绪")
        self.status_label.setStyleSheet("padding: 5px; background: #f0f0f0;")
        layout.addWidget(self.status_label)
        
        # 转换按钮
        self.convert_btn = QPushButton("开始转换PDF")
        self.convert_btn.clicked.connect(self.convert_to_pdf)
        self.convert_btn.setMinimumHeight(50)
        self.convert_btn.setStyleSheet("background: #4CAF50; color: white; font-size: 16px; font-weight: bold;")
        layout.addWidget(self.convert_btn)
    
    def add_images(self):
        """添加单张或多张图片"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "选择图片",
            "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp);;所有文件 (*.*)"
        )
        
        if files:
            for file in files:
                if file not in self.image_files:
                    self.image_files.append(file)
                    self.add_list_item(file)
            self.update_status()
    
    def batch_add_images(self):
        """批量导入整个文件夹的图片"""
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        
        if folder:
            image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp']
            count = 0
            
            for filename in sorted(os.listdir(folder)):
                ext = os.path.splitext(filename)[1].lower()
                if ext in image_extensions:
                    full_path = os.path.join(folder, filename)
                    if full_path not in self.image_files:
                        self.image_files.append(full_path)
                        self.add_list_item(full_path)
                        count += 1
            
            if count > 0:
                self.update_status()
                QMessageBox.information(self, "批量导入", f"成功导入 {count} 张图片！")
            else:
                QMessageBox.warning(self, "批量导入", "文件夹中没有找到图片文件。")
    
    def add_list_item(self, file_path):
        """添加列表项"""
        item = QListWidgetItem()
        item.setText(os.path.basename(file_path))
        
        # 创建缩略图
        try:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(QSize(100, 100), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                item.setIcon(QIcon(scaled))
            else:
                item.setIcon(QIcon.fromTheme("image-x-generic"))
        except:
            item.setIcon(QIcon.fromTheme("image-x-generic"))
        
        item.setToolTip(file_path)
        self.image_list.addItem(item)
    
    def remove_selected(self):
        """移除选中的图片"""
        selected_items = self.image_list.selectedItems()
        
        if not selected_items:
            QMessageBox.information(self, "提示", "请先选择要移除的图片（可使用Ctrl/Shift多选）")
            return
        
        # 从后往前删除，避免索引问题
        for item in reversed(selected_items):
            row = self.image_list.row(item)
            self.image_list.takeItem(row)
            if row < len(self.image_files):
                self.image_files.pop(row)
        
        self.update_status()
    
    def clear_all(self):
        """清空所有图片"""
        if self.image_files:
            reply = QMessageBox.question(
                self, 
                "确认清空", 
                f"确定要清空所有 {len(self.image_files)} 张图片吗？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.image_list.clear()
                self.image_files.clear()
                self.update_status()
    
    def set_custom_filename(self):
        """设置自定义输出文件名"""
        filename, ok = QInputDialog.getText(self, "自定义文件名", "请输入PDF文件名（不含扩展名）:")
        
        if ok and filename:
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            self.filename_edit.setText(filename)
    
    def move_up(self):
        """将选中项上移"""
        selected_items = self.image_list.selectedItems()
        
        if not selected_items:
            return
        
        # 获取所有选中项的行号并排序
        rows = sorted([self.image_list.row(item) for item in selected_items])
        
        # 从上往下移动（先处理最小的行号）
        for row in rows:
            if row > 0:  # 不是第一行
                # 交换数据和列表项
                self.image_files[row], self.image_files[row - 1] = \
                    self.image_files[row - 1], self.image_files[row]
                
                # 交换列表项
                item = self.image_list.takeItem(row)
                self.image_list.insertItem(row - 1, item)
                item.setSelected(True)
    
    def move_down(self):
        """将选中项下移"""
        selected_items = self.image_list.selectedItems()
        
        if not selected_items:
            return
        
        # 获取所有选中项的行号并反向排序
        rows = sorted([self.image_list.row(item) for item in selected_items], reverse=True)
        
        # 从下往上移动（先处理最大的行号）
        for row in rows:
            if row < self.image_list.count() - 1:  # 不是最后一行
                # 交换数据和列表项
                self.image_files[row], self.image_files[row + 1] = \
                    self.image_files[row + 1], self.image_files[row]
                
                # 交换列表项
                item = self.image_list.takeItem(row)
                self.image_list.insertItem(row + 1, item)
                item.setSelected(True)
    
    def update_status(self):
        """更新状态信息"""
        self.status_label.setText(f"已添加 {len(self.image_files)} 张图片")
    
    def convert_to_pdf(self):
        """将图片转换为PDF"""
        if not self.image_files:
            QMessageBox.warning(self, "错误", "请先添加要转换的图片！")
            return
        
        # 选择保存位置
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存PDF文件",
            os.path.join(os.path.expanduser("~"), self.filename_edit.text()),
            "PDF文件 (*.pdf)"
        )
        
        if not output_path:
            return
        
        if not output_path.endswith('.pdf'):
            output_path += '.pdf'
        
        # 获取设置
        quality_map = {0: 30, 1: 70, 2: 95}
        quality = quality_map[self.quality_combo.currentIndex()]
        
        orientation_map = {0: None, 1: "portrait", 2: "landscape"}
        orientation = orientation_map[self.orientation_combo.currentIndex()]
        
        try:
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(len(self.image_files))
            self.convert_btn.setEnabled(False)
            
            images = []
            
            for i, img_path in enumerate(self.image_files):
                self.progress_bar.setValue(i + 1)
                self.status_label.setText(f"正在处理: {os.path.basename(img_path)}")
                
                # 打开并处理图片
                img = Image.open(img_path)
                
                # 转换模式为RGB（如果是RGBA或其他模式）
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                
                # 根据方向调整图片
                if orientation:
                    if orientation == "portrait" and img.width > img.height:
                        img = img.rotate(90, expand=True)
                    elif orientation == "landscape" and img.height > img.width:
                        img = img.rotate(90, expand=True)
                
                images.append(img)
            
            self.status_label.setText("正在生成PDF...")
            
            # 保存为PDF
            if images:
                images[0].save(
                    output_path,
                    save_all=True,
                    append_images=images[1:],
                    quality=quality,
                    optimize=True
                )
            
            self.progress_bar.setVisible(False)
            self.convert_btn.setEnabled(True)
            
            QMessageBox.information(
                self, 
                "成功", 
                f"PDF文件已生成！\n\n保存位置: {output_path}\n\n包含 {len(self.image_files)} 张图片"
            )
            
            self.status_label.setText("转换完成！")
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.convert_btn.setEnabled(True)
            QMessageBox.critical(self, "错误", f"转换失败！\n\n错误信息: {str(e)}")
            self.status_label.setText("转换失败")
