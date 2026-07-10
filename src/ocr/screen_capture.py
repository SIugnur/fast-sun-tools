"""屏幕截图工具 - OCR功能已禁用

由于 PyTorch 在 Windows 上的兼容性问题，OCR 功能暂时禁用。
如需使用 OCR，请考虑使用 Tesseract OCR。
"""

import mss
from PIL import Image
from PyQt5.QtWidgets import (QWidget, QDialog, QVBoxLayout, 
                            QTextEdit, QPushButton, QHBoxLayout)
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QPixmap, QImage


class OCRResultDialog(QDialog):
    """截图结果对话框"""
    
    def __init__(self, recognized_text, parent=None):
        super().__init__(parent)
        self.setWindowTitle("截图")
        self.setMinimumSize(400, 200)
        self.init_ui(recognized_text)
    
    def init_ui(self, text):
        layout = QVBoxLayout()
        
        # 文本编辑框
        self.text_edit = QTextEdit()
        self.text_edit.setText(text)
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        
        # 关闭按钮
        btn_layout = QHBoxLayout()
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)


class ScreenCaptureTool(QWidget):
    text_captured = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.is_selecting = False
        self.start_pos = QPoint()
        self.end_pos = QPoint()
        self.screenshot = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)
        self.showFullScreen()
        
    def start_capture(self):
        self.capture_full_screen()
        self.show()
        
    def capture_full_screen(self):
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            img = sct.grab(monitor)
            self.screenshot = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")
            
    def paintEvent(self, event):
        painter = QPainter(self)
        
        if self.screenshot:
            img = self.screenshot
            qimage = QImage(img.tobytes(), img.width, img.height, 
                          QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage)
            painter.drawPixmap(0, 0, pixmap)
            
        dark_color = QColor(0, 0, 0, 100)
        painter.fillRect(self.rect(), dark_color)
        
        if self.is_selecting:
            selected_rect = self.get_selection_rect()
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(selected_rect, Qt.transparent)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            
            pen = QPen(QColor(0, 255, 0), 2, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawRect(selected_rect)
            
    def get_selection_rect(self):
        x1 = min(self.start_pos.x(), self.end_pos.x())
        y1 = min(self.start_pos.y(), self.end_pos.y())
        x2 = max(self.start_pos.x(), self.end_pos.x())
        y2 = max(self.start_pos.y(), self.end_pos.y())
        return QRect(x1, y1, x2 - x1, y2 - y1)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_selecting = True
            self.start_pos = event.pos()
            self.end_pos = event.pos()
            self.update()
            
    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.end_pos = event.pos()
            self.update()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_selecting:
            self.is_selecting = False
            self.end_pos = event.pos()
            self.capture_selected_area()
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            self.text_captured.emit("")
    
    def capture_selected_area(self):
        """截取选定区域并保存为图片"""
        rect = self.get_selection_rect()
        if rect.width() < 10 or rect.height() < 10:
            self.close()
            self.text_captured.emit("")
            return
            
        try:
            x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
            cropped = self.screenshot.crop((x, y, x + w, y + h))
            
            # 保存到剪贴板
            cropped.save('temp_screenshot.png')
            
            # 显示截图预览
            dialog = OCRResultDialog("截图已保存到 temp_screenshot.png", self)
            dialog.exec_()
            
            self.close()
            self.text_captured.emit("")
            
        except Exception as e:
            print(f"[截图] 错误: {e}")
            import traceback
            traceback.print_exc()
            self.close()
            self.text_captured.emit("")
