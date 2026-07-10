import sys
import os

# 禁用 PaddleOCR 日志
os.environ['FLAGS_enable_api_barrier'] = '0'

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from src.main_window import MainWindow
from src.utils.theme import apply_theme


def main():
    # 禁用 GLOG 输出
    import logging
    logging.getLogger('paddle').setLevel(logging.ERROR)
    
    app = QApplication(sys.argv)
    app.setApplicationName("FastSunTools")
    app.setOrganizationName("FastSun")
    
    apply_theme(app)
    app.setFont(QFont("Microsoft YaHei", 10))
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
