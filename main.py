"""
QTKT Generator App
Ứng dụng tạo Quy trình kỹ thuật lâm sàng theo mẫu Bộ Y tế
"""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from ui.main_window import MainWindow
from config import APP_NAME


def main():
    """Entry point của ứng dụng"""
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    
    # Set app style
    app.setStyle("Fusion")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
