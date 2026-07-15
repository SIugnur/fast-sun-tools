import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QFileDialog, QMessageBox, QProgressBar,
                             QGroupBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class PDFToWordConverter(QThread):
    """后台线程用于 PDF 转 Word"""
    progress_updated = pyqtSignal(int, int)  # 当前页数, 总页数
    conversion_finished = pyqtSignal(str)    # 输出文件路径
    conversion_failed = pyqtSignal(str)      # 错误信息
    
    def __init__(self, pdf_path, output_path, parent=None):
        super().__init__(parent)
        self.pdf_path = pdf_path
        self.output_path = output_path
    
    def run(self):
        """在后台线程中执行转换"""
        try:
            from pdf2docx import Converter
            import fitz  # PyMuPDF
            
            # 使用 PyMuPDF 获取 PDF 总页数
            pdf_doc = fitz.open(self.pdf_path)
            total_pages = len(pdf_doc)
            pdf_doc.close()
            
            # 创建转换器并执行转换
            cv = Converter(self.pdf_path)
            cv.convert(self.output_path, start=0, end=total_pages)
            cv.close()
            
            # 转换完成
            self.conversion_finished.emit(self.output_path)
            
        except Exception as e:
            self.conversion_failed.emit(str(e))


class PDFToWordWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.pdf_path = None
        self.converter = None
        self.init_ui()
        self.setWindowTitle("PDF转Word工具")
        self.setGeometry(100, 100, 600, 400)
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("PDF转Word工具")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title_label)
        
        # 文件选择区域
        file_group = QGroupBox("文件选择")
        file_layout = QVBoxLayout()
        
        # PDF 文件选择
        pdf_layout = QHBoxLayout()
        pdf_layout.addWidget(QLabel("PDF文件:"))
        self.pdf_path_label = QLabel("未选择文件")
        self.pdf_path_label.setStyleSheet("color: #666;")
        pdf_layout.addWidget(self.pdf_path_label, 1)
        
        self.select_pdf_btn = QPushButton("选择PDF文件")
        self.select_pdf_btn.clicked.connect(self.select_pdf)
        self.select_pdf_btn.setStyleSheet("padding: 5px 15px;")
        pdf_layout.addWidget(self.select_pdf_btn)
        
        file_layout.addLayout(pdf_layout)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.convert_btn = QPushButton("开始转换")
        self.convert_btn.clicked.connect(self.start_conversion)
        self.convert_btn.setEnabled(False)
        self.convert_btn.setMinimumHeight(40)
        self.convert_btn.setStyleSheet("padding: 0 30px;")
        button_layout.addWidget(self.convert_btn)
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setMinimumHeight(40)
        self.close_btn.setStyleSheet("padding: 0 30px;")
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
    
    def select_pdf(self):
        """选择 PDF 文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择PDF文件",
            os.path.expanduser("~"),
            "PDF文件 (*.pdf)"
        )
        
        if file_path:
            self.pdf_path = file_path
            self.pdf_path_label.setText(os.path.basename(file_path))
            self.pdf_path_label.setStyleSheet("color: #2196F3; font-weight: bold;")
            self.convert_btn.setEnabled(True)
            self.status_label.setText(f"已选择: {file_path}")
    
    def start_conversion(self):
        """开始转换"""
        if not self.pdf_path:
            QMessageBox.warning(self, "错误", "请先选择PDF文件！")
            return
        
        # 选择保存位置
        default_name = os.path.splitext(os.path.basename(self.pdf_path))[0] + ".docx"
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存Word文件",
            os.path.join(os.path.dirname(self.pdf_path), default_name),
            "Word文件 (*.docx)"
        )
        
        if not output_path:
            return
        
        if not output_path.endswith('.docx'):
            output_path += '.docx'
        
        # 开始转换
        self.convert_btn.setEnabled(False)
        self.select_pdf_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("正在转换...")
        
        # 创建后台转换线程
        self.converter = PDFToWordConverter(self.pdf_path, output_path)
        self.converter.conversion_finished.connect(self.on_conversion_finished)
        self.converter.conversion_failed.connect(self.on_conversion_failed)
        self.converter.start()
    
    def on_conversion_finished(self, output_path):
        """转换完成"""
        self.progress_bar.setVisible(False)
        self.convert_btn.setEnabled(True)
        self.select_pdf_btn.setEnabled(True)
        self.status_label.setText("转换完成！")
        
        QMessageBox.information(
            self,
            "成功",
            f"Word文件已生成！\n\n保存位置: {output_path}"
        )
    
    def on_conversion_failed(self, error_msg):
        """转换失败"""
        self.progress_bar.setVisible(False)
        self.convert_btn.setEnabled(True)
        self.select_pdf_btn.setEnabled(True)
        self.status_label.setText(f"转换失败: {error_msg}")
        
        QMessageBox.critical(
            self,
            "错误",
            f"转换失败！\n\n错误信息: {error_msg}"
        )
