import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
from src.main_window import MainWindow
from src.utils.theme import apply_theme


def main():
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
