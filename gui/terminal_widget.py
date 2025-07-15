from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QHBoxLayout, QLineEdit, QPushButton, QPlainTextEdit
from PyQt6.QtCore import Qt
from core.ssh_client import SSHClient
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import QUrl
import webbrowser
from PyQt6.QtGui import QTextCursor

class TerminalOutput(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setReadOnly(True)
        self.setOpenExternalLinks(False)  # 禁用自动打开外部链接
        self.anchorClicked.connect(self.handle_link_clicked)

    def handle_link_clicked(self, url: QUrl):
        try:
            webbrowser.open(url.toString())
        except Exception as e:
            print("打开链接失败：", e)

class TerminalWidget(QPlainTextEdit):
    def __init__(self, connection):
        super().__init__()
        self.connection = connection
        self.ssh_client = SSHClient()
        self.setReadOnly(False)
        self.setStyleSheet("""
            background-color: #181c20;
            color: #c7ffb6;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 14px;
        """)
        self.prompt = f"{connection.username}@{connection.host}$ "
        self.insertPlainText(self.prompt)
        self.command_history = []
        self.history_index = -1
        self.ssh_client.output_received.connect(self.append_output)
        self.ssh_client.connection_status.connect(self.append_output)
        import threading
        threading.Thread(target=self.ssh_client.connect, args=(self.connection,)).start()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(cursor)
            text = self.document().toPlainText()
            last_line = text.split('\n')[-1]
            command = last_line[len(self.prompt):]
            self.command_history.append(command)
            self.history_index = len(self.command_history)
            self.ssh_client.send_command(command)
            self.insertPlainText('\n' + self.prompt)
        elif event.key() == Qt.Key.Key_Up:
            if self.history_index > 0:
                self.history_index -= 1
                self.replace_current_line(self.command_history[self.history_index])
        elif event.key() == Qt.Key.Key_Down:
            if self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                self.replace_current_line(self.command_history[self.history_index])
            else:
                self.replace_current_line('')
        else:
            super().keyPressEvent(event)

    def replace_current_line(self, text):
        cursor = self.textCursor()
        cursor.movePosition(cursor.StartOfLine, cursor.KeepAnchor)
        cursor.removeSelectedText()
        cursor.insertText(self.prompt + text)

    def append_output(self, output):
        self.insertPlainText('\n' + output)
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)