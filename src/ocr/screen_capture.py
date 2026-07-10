"""屏幕截图工具 - 支持 PaddleOCR 文字识别"""

import mss
from PIL import Image
from PyQt5.QtWidgets import (QWidget, QDialog, QVBoxLayout, 
                            QTextEdit, QPushButton, QHBoxLayout, QLabel)
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QPixmap, QImage


class OCRResultDialog(QDialog):
    """截图结果对话框"""
    
    def __init__(self, recognized_text, image_path=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("截图识别结果")
        self.setMinimumSize(500, 400)
        self.init_ui(recognized_text, image_path)
    
    def init_ui(self, text, image_path=None):
        layout = QVBoxLayout()
        
        # 状态标签
        if text and text.strip():
            status_label = QLabel("文字识别完成")
            status_label.setStyleSheet("color: green; font-weight: bold;")
            layout.addWidget(status_label)
        else:
            status_label = QLabel("未识别到文字")
            status_label.setStyleSheet("color: orange; font-weight: bold;")
            layout.addWidget(status_label)
        
        # 文本编辑框
        self.text_edit = QTextEdit()
        self.text_edit.setText(text if text else "")
        layout.addWidget(self.text_edit)
        
        # 按钮布局
        btn_layout = QHBoxLayout()
        
        # 复制按钮
        self.copy_btn = QPushButton("复制文字")
        self.copy_btn.clicked.connect(self.copy_text)
        btn_layout.addWidget(self.copy_btn)
        
        # 关闭按钮
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def copy_text(self):
        clipboard = self.text_edit.toPlainText()
        from PyQt5.QtWidgets import QApplication
        QApplication.clipboard().setText(clipboard)


class ScreenCaptureTool(QWidget):
    text_captured = pyqtSignal(str)
    
    def __init__(self, ocr_engine=None):
        super().__init__()
        self.is_selecting = False
        self.start_pos = QPoint()
        self.end_pos = QPoint()
        self.screenshot = None
        self.ocr = ocr_engine
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
        """截取选定区域并使用 OCR 识别文字"""
        rect = self.get_selection_rect()
        if rect.width() < 10 or rect.height() < 10:
            self.close()
            self.text_captured.emit("")
            return
            
        try:
            x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
            cropped = self.screenshot.crop((x, y, x + w, y + h))
            
            # 保存截图
            image_path = 'temp_screenshot.png'
            cropped.save(image_path)
            
            # 使用 OCR 识别文字
            recognized_text = self._perform_ocr(cropped)
            
            # 显示结果
            dialog = OCRResultDialog(recognized_text, image_path, self)
            dialog.exec_()
            
            self.close()
            self.text_captured.emit(recognized_text if recognized_text else "")
            
        except Exception as e:
            print(f"[截图] 错误: {e}")
            import traceback
            traceback.print_exc()
            self.close()
            self.text_captured.emit("")
    
    def _perform_ocr(self, image):
        """使用 PaddleOCR 识别文字"""
        if self.ocr is None:
            return "[OCR 未初始化]"
        
        try:
            import numpy as np
            
            # 将 PIL Image 转换为 numpy array
            img_array = np.array(image)
            
            # PaddleOCR 识别
            result = self.ocr.predict(img_array)
            
            # 提取识别的文字
            all_texts = []
            for res in result:
                # result 是字典格式
                if isinstance(res, dict) and 'rec_texts' in res:
                    all_texts.extend(res['rec_texts'])
                # 如果是对象格式
                elif hasattr(res, 'rec_texts') and res.rec_texts:
                    all_texts.extend(res.rec_texts)
            
            if all_texts:
                return '\n'.join(all_texts)
            else:
                return ""
                
        except Exception as e:
            print(f"[OCR] 识别失败: {e}")
            import traceback
            traceback.print_exc()
            return f"[识别错误: {e}]"
