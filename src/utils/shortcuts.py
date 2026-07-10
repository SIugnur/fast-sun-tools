from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt


def setup_shortcuts(window):
    # Focus on search in file browser
    QShortcut(QKeySequence(Qt.CTRL + Qt.Key_F), window, lambda: window.file_browser.search_edit.setFocus())
    # Refresh files
    QShortcut(QKeySequence(Qt.CTRL + Qt.Key_R), window, window.refresh_files)
    # Go to home directory
    QShortcut(QKeySequence(Qt.CTRL + Qt.Key_H), window, window.go_home)
    # Toggle window topmost
    QShortcut(QKeySequence(Qt.CTRL + Qt.Key_T), window, window.toggle_topmost)
    # Start OCR
    QShortcut(QKeySequence(Qt.ALT + Qt.Key_O), window, window.start_ocr)
    # Escape to close
    QShortcut(QKeySequence(Qt.Key_Escape), window, window.close)
