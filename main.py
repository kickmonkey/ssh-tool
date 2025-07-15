import sys
from PyQt6.QtWidgets import QApplication
from gui.main_window import SSHToolGUI

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("SSH工具")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("SSH Tool")
    window = SSHToolGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()