from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QSpinBox, QRadioButton, QButtonGroup, QPushButton, QHBoxLayout, QFileDialog, QMessageBox
from models.connection import SSHConnection

class ConnectionDialog(QDialog):
    def __init__(self, parent=None, connection=None):
        super().__init__(parent)
        self.connection = connection
        self.setWindowTitle("编辑SSH连接" if connection else "新建SSH连接")
        self.setModal(True)
        self.resize(400, 350)
        self.init_ui()
        if connection:
            self.load_connection_data()
    
    def init_ui(self):
        layout = QFormLayout(self)
        self.name_input = QLineEdit()
        self.host_input = QLineEdit()
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(22)
        self.username_input = QLineEdit()
        self.auth_group = QButtonGroup()
        self.password_radio = QRadioButton("密码认证")
        self.key_radio = QRadioButton("密钥认证")
        self.password_radio.setChecked(True)
        self.auth_group.addButton(self.password_radio)
        self.auth_group.addButton(self.key_radio)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_path_input = QLineEdit()
        self.key_browse_btn = QPushButton("浏览...")
        self.key_browse_btn.clicked.connect(self.browse_key_file)
        self.group_input = QLineEdit()
        self.group_input.setText("默认")
        layout.addRow("连接名称:", self.name_input)
        layout.addRow("主机地址:", self.host_input)
        layout.addRow("端口:", self.port_input)
        layout.addRow("用户名:", self.username_input)
        layout.addRow("", self.password_radio)
        layout.addRow("密码:", self.password_input)
        layout.addRow("", self.key_radio)
        key_layout = QHBoxLayout()
        key_layout.addWidget(self.key_path_input)
        key_layout.addWidget(self.key_browse_btn)
        layout.addRow("密钥文件:", key_layout)
        layout.addRow("分组:", self.group_input)
        button_layout = QHBoxLayout()
        test_btn = QPushButton("测试连接")
        test_btn.clicked.connect(self.test_connection)
        button_layout.addWidget(test_btn)
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        layout.addRow("", button_layout)
    
    def load_connection_data(self):
        if self.connection:
            self.name_input.setText(self.connection.name)
            self.host_input.setText(self.connection.host)
            self.port_input.setValue(self.connection.port)
            self.username_input.setText(self.connection.username)
            self.group_input.setText(self.connection.group)
            if self.connection.private_key_path:
                self.key_radio.setChecked(True)
                self.key_path_input.setText(self.connection.private_key_path)
            else:
                self.password_radio.setChecked(True)
                if self.connection.password:
                    self.password_input.setText(self.connection.password)
    
    def browse_key_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择私钥文件")
        if file_path:
            self.key_path_input.setText(file_path)
    
    def test_connection(self):
        QMessageBox.information(self, "测试", "连接测试功能待实现")
    
    def get_connection(self) -> SSHConnection:
        return SSHConnection(
            name=self.name_input.text(),
            host=self.host_input.text(),
            port=self.port_input.value(),
            username=self.username_input.text(),
            password=self.password_input.text() if self.password_radio.isChecked() else None,
            private_key_path=self.key_path_input.text() if self.key_radio.isChecked() else None,
            group=self.group_input.text()
        )
