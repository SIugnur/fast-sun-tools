import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QToolBar, QAction, QSplitter, QStatusBar, QLabel)
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QIcon, QFont
from src.file_explorer.file_browser import FileBrowser
from src.ocr.screen_capture import ScreenCaptureTool
from src.image_to_pdf.image_to_pdf_window import ImageToPDFWindow
from src.utils.shortcuts import setup_shortcuts
from paddleocr import PaddleOCR


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_topmost = False
        self.image_to_pdf_window = None
        self.ocr = None
        self.init_ocr()
        self.init_ui()
        self.setWindowTitle("FastSunTools - 办公助手")
        self.resize(1200, 800)
        setup_shortcuts(self)
    
    def init_ocr(self):
        """预加载 OCR 模型"""
        try:
            self.ocr = PaddleOCR(
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                lang='ch',
            )
        except Exception:
            self.ocr = None
        
    def init_ui(self):
        self.create_toolbar()
        self.create_central_widget()
        self.create_status_bar()
        
    def create_toolbar(self):
        toolbar = QToolBar("主工具栏")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(toolbar)
        
        topmost_action = QAction("置顶", self)
        topmost_action.setToolTip("将窗口固定在其他窗口上方 (Ctrl+T)")
        topmost_action.triggered.connect(self.toggle_topmost)
        toolbar.addAction(topmost_action)
        
        toolbar.addSeparator()
        
        ocr_action = QAction("OCR 识别", self)
        ocr_action.setToolTip("屏幕截图并识别文字 (Alt+O)")
        ocr_action.triggered.connect(self.start_ocr)
        toolbar.addAction(ocr_action)
        
        toolbar.addSeparator()
        
        # 图片转PDF功能
        image_to_pdf_action = QAction("图片转PDF", self)
        image_to_pdf_action.setToolTip("将多张图片拼接成一个PDF文件")
        image_to_pdf_action.triggered.connect(self.open_image_to_pdf)
        toolbar.addAction(image_to_pdf_action)
        
        toolbar.addSeparator()
        
        home_action = QAction("主页", self)
        home_action.setToolTip("回到用户主目录 (Ctrl+H)")
        home_action.triggered.connect(self.go_home)
        toolbar.addAction(home_action)
        
        refresh_action = QAction("刷新", self)
        refresh_action.setToolTip("刷新当前目录 (Ctrl+R)")
        refresh_action.triggered.connect(self.refresh_files)
        toolbar.addAction(refresh_action)
        
    def create_central_widget(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        splitter = QSplitter(Qt.Horizontal)
        
        self.file_browser = FileBrowser()
        splitter.addWidget(self.file_browser)
        
        layout.addWidget(splitter)
        
    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
        
    def toggle_topmost(self):
        self.is_topmost = not self.is_topmost
        if self.is_topmost:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            self.status_bar.showMessage("窗口已置顶")
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
            self.status_bar.showMessage("窗口已取消置顶")
        self.show()
        
    def start_ocr(self):
        self.ocr_tool = ScreenCaptureTool(self.ocr)
        self.ocr_tool.text_captured.connect(self.on_ocr_text)
        self.hide()
        self.ocr_tool.start_capture()
        
    def on_ocr_text(self, text):
        self.show()
        if text:
            self.status_bar.showMessage("截图已保存")
        else:
            self.status_bar.showMessage("截图完成")
    
    def open_image_to_pdf(self):
        """打开图片转PDF工具窗口"""
        if self.image_to_pdf_window is None:
            self.image_to_pdf_window = ImageToPDFWindow()
        
        self.image_to_pdf_window.show()
        self.image_to_pdf_window.raise_()
        self.image_to_pdf_window.activateWindow()
        self.status_bar.showMessage("已打开图片转PDF工具")
            
    def go_home(self):
        home_dir = os.path.expanduser("~")
        self.file_browser.navigate_to(home_dir)
        
    def refresh_files(self):
        self.file_browser.refresh()
        self.status_bar.showMessage("已刷新")
