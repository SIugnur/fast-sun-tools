import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QFileDialog, QMessageBox, QProgressBar,
                             QGroupBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class WordToPDFConverter(QThread):
    """后台线程用于 Word 转 PDF"""
    conversion_finished = pyqtSignal(str)    # 输出文件路径
    conversion_failed = pyqtSignal(str)      # 错误信息
    
    def __init__(self, word_path, output_path, parent=None):
        super().__init__(parent)
        self.word_path = word_path
        self.output_path = output_path
    
    def run(self):
        """在后台线程中执行转换"""
        word_app = None
        try:
            # 根据文件类型选择转换方式
            ext = os.path.splitext(self.word_path)[1].lower()
            
            if ext == '.docx':
                # .docx 格式直接使用 python-docx 和 reportlab 转换
                self._convert_docx()
            else:
                # .doc 格式使用 Word 应用程序转换
                self._convert_with_word()
            
            # 转换完成
            self.conversion_finished.emit(self.output_path)
            
        except Exception as e:
            self.conversion_failed.emit(str(e))
        finally:
            # 确保 Word 应用程序被关闭
            if word_app is not None:
                try:
                    word_app.Quit()
                except:
                    pass
    
    def _convert_docx(self):
        """使用 python-docx 转换 .docx 文件"""
        from docx import Document
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        
        # 读取 Word 文档
        doc = Document(self.word_path)
        
        # 创建 PDF
        c = canvas.Canvas(self.output_path, pagesize=A4)
        width, height = A4
        
        # 设置中文字体
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        
        # 尝试加载系统字体
        font_name = "Helvetica"
        try:
            # Windows 系统字体路径
            font_paths = [
                "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
                "C:/Windows/Fonts/simhei.ttf",  # 黑体
                "C:/Windows/Fonts/simsun.ttc",  # 宋体
            ]
            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                    font_name = 'ChineseFont'
                    break
        except:
            pass
        
        y_position = height - 50
        line_height = 14
        
        for paragraph in doc.paragraphs:
            text = paragraph.text
            
            if not text.strip():
                y_position -= line_height * 0.5
                continue
            
            # 处理文本换行
            words = text.split('\n')
            for word in words:
                if not word.strip():
                    y_position -= line_height * 0.5
                    continue
                    
                # 简单的文本渲染
                c.setFont(font_name, 10)
                c.drawString(50, y_position, word)
                y_position -= line_height
                
                if y_position < 50:
                    c.showPage()
                    y_position = height - 50
        
        c.save()
    
    def _convert_with_word(self):
        """使用 Word 应用程序转换 .doc 文件"""
        import win32com.client
        import pythoncom
        
        # 初始化 COM
        pythoncom.CoInitializeEx(0, pythoncom.COINIT_APARTMENTTHREADED)
        
        try:
            word_app = win32com.client.Dispatch("Word.Application")
            word_app.Visible = False
            
            # 打开文档
            doc = word_app.Documents.Open(os.path.abspath(self.word_path))
            
            # 转换为 PDF
            doc.SaveAs(os.path.abspath(self.output_path), FileFormat=17)  # 17 = wdFormatPDF
            
            # 关闭文档
            doc.Close(False)
            
        finally:
            # 关闭 Word 应用程序
            if word_app:
                try:
                    word_app.Quit()
                except:
                    pass
            pythoncom.CoUninitialize()


class WordToPDFWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.word_path = None
        self.converter = None
        self.init_ui()
        self.setWindowTitle("Word转PDF工具")
        self.setGeometry(100, 100, 600, 400)
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("Word转PDF工具")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title_label)
        
        # 文件选择区域
        file_group = QGroupBox("文件选择")
        file_layout = QVBoxLayout()
        
        # Word 文件选择
        word_layout = QHBoxLayout()
        word_layout.addWidget(QLabel("Word文件:"))
        self.word_path_label = QLabel("未选择文件")
        self.word_path_label.setStyleSheet("color: #666;")
        word_layout.addWidget(self.word_path_label, 1)
        
        self.select_word_btn = QPushButton("选择Word文件")
        self.select_word_btn.clicked.connect(self.select_word)
        self.select_word_btn.setStyleSheet("padding: 5px 15px;")
        word_layout.addWidget(self.select_word_btn)
        
        file_layout.addLayout(word_layout)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # 提示信息
        hint_label = QLabel("提示: 支持 .docx 和 .doc 格式，.doc 格式需要安装 Microsoft Word")
        hint_label.setStyleSheet("color: #888; font-size: 12px; padding: 5px;")
        layout.addWidget(hint_label)
        
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
    
    def select_word(self):
        """选择 Word 文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择Word文件",
            os.path.expanduser("~"),
            "Word文件 (*.docx *.doc)"
        )
        
        if file_path:
            self.word_path = file_path
            self.word_path_label.setText(os.path.basename(file_path))
            self.word_path_label.setStyleSheet("color: #2196F3; font-weight: bold;")
            self.convert_btn.setEnabled(True)
            self.status_label.setText(f"已选择: {file_path}")
    
    def start_conversion(self):
        """开始转换"""
        if not self.word_path:
            QMessageBox.warning(self, "错误", "请先选择Word文件！")
            return
        
        # 选择保存位置
        default_name = os.path.splitext(os.path.basename(self.word_path))[0] + ".pdf"
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存PDF文件",
            os.path.join(os.path.dirname(self.word_path), default_name),
            "PDF文件 (*.pdf)"
        )
        
        if not output_path:
            return
        
        if not output_path.endswith('.pdf'):
            output_path += '.pdf'
        
        # 开始转换
        self.convert_btn.setEnabled(False)
        self.select_word_btn.setEnabled(False)
        self.status_label.setText("正在转换...")
        
        # 创建后台转换线程
        self.converter = WordToPDFConverter(self.word_path, output_path)
        self.converter.conversion_finished.connect(self.on_conversion_finished)
        self.converter.conversion_failed.connect(self.on_conversion_failed)
        self.converter.start()
    
    def on_conversion_finished(self, output_path):
        """转换完成"""
        self.convert_btn.setEnabled(True)
        self.select_word_btn.setEnabled(True)
        self.status_label.setText("转换完成！")
        
        QMessageBox.information(
            self,
            "成功",
            f"PDF文件已生成！\n\n保存位置: {output_path}"
        )
    
    def on_conversion_failed(self, error_msg):
        """转换失败"""
        self.convert_btn.setEnabled(True)
        self.select_word_btn.setEnabled(True)
        self.status_label.setText(f"转换失败: {error_msg}")
        
        QMessageBox.critical(
            self,
            "错误",
            f"转换失败！\n\n错误信息: {error_msg}"
        )
