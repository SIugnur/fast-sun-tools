import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QToolBar, QAction, QSplitter, QStatusBar, QLabel)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QThread
from PyQt5.QtGui import QIcon, QFont
from src.file_explorer.file_browser import FileBrowser
from src.ocr.screen_capture import ScreenCaptureTool
from src.image_to_pdf.image_to_pdf_window import ImageToPDFWindow
from src.utils.shortcuts import setup_shortcuts


class OCRLoaderThread(QThread):
    """后台线程用于加载 OCR 模型"""
    ocr_loaded = pyqtSignal(object)  # 加载完成后发出信号，传递 OCR 实例
    load_failed = pyqtSignal(str)    # 加载失败时发出信号，传递错误信息
    
    def run(self):
        """在后台线程中加载 OCR 模型"""
        try:
            from paddleocr import PaddleOCR
            ocr = PaddleOCR(
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
                lang='ch',
            )
            self.ocr_loaded.emit(ocr)  # 发出加载成功的信号
        except Exception as e:
            self.load_failed.emit(str(e))  # 发出加载失败的信号


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.is_topmost = False
        self.image_to_pdf_window = None
        self.ocr = None
        self.ocr_loader = None
        self.is_ocr_loading = False
        self.init_ui()
        self.setWindowTitle("FastSunTools - 办公助手")
        self.resize(1200, 800)
        setup_shortcuts(self)
    
    def _load_ocr_async(self):
        """异步加载 OCR 模型，不阻塞界面"""
        if self.ocr is not None:
            # OCR 已经加载，直接启动
            self._start_ocr_capture()
            return
        
        if self.is_ocr_loading:
            # 正在加载中，忽略重复点击
            return
        
        # 标记正在加载
        self.is_ocr_loading = True
        self.ocr_action.setEnabled(False)
        self.ocr_action.setText("加载中...")
        self.status_bar.showMessage("正在后台加载 OCR 模型...")
        
        # 创建后台线程加载 OCR
        self.ocr_loader = OCRLoaderThread()
        self.ocr_loader.ocr_loaded.connect(self._on_ocr_loaded)
        self.ocr_loader.load_failed.connect(self._on_ocr_load_failed)
        self.ocr_loader.start()
    
    def _on_ocr_loaded(self, ocr):
        """OCR 加载成功后的回调"""
        self.ocr = ocr
        self.is_ocr_loading = False
        self.ocr_action.setText("OCR 识别")
        self.ocr_action.setEnabled(True)
        self.status_bar.showMessage("OCR 模型加载完成")
        
        # 启动截图
        self._start_ocr_capture()
    
    def _on_ocr_load_failed(self, error_msg):
        """OCR 加载失败后的回调"""
        self.is_ocr_loading = False
        self.ocr_action.setText("OCR 识别")
        self.ocr_action.setEnabled(True)
        self.status_bar.showMessage(f"OCR 加载失败: {error_msg}")
    
    def _start_ocr_capture(self):
        """启动 OCR 截图功能"""
        if self.ocr is None:
            return
        
        self.ocr_tool = ScreenCaptureTool(self.ocr)
        self.ocr_tool.text_captured.connect(self.on_ocr_text)
        self.hide()
        self.ocr_tool.start_capture()
        
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
        
        self.ocr_action = QAction("OCR 识别", self)
        self.ocr_action.setToolTip("屏幕截图并识别文字 (Alt+O)")
        self.ocr_action.triggered.connect(self.start_ocr)
        toolbar.addAction(self.ocr_action)
        
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
        """启动 OCR 识别功能"""
        # 异步加载 OCR 模型，不阻塞界面
        self._load_ocr_async()
        
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
