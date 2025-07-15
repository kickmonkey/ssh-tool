from PyQt6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem, QTabWidget, QPushButton, QStyle, QMessageBox, QDialog  
from PyQt6.QtGui import QAction
from core.connection_manager import ConnectionManager
from gui.terminal_widget import TerminalWidget
from gui.dialogs import ConnectionDialog
from PyQt6.QtCore import Qt

class SSHToolGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.connection_manager = ConnectionManager()
        self.ssh_clients = {}
        self.init_ui()
        self.load_connections()
    
    def init_ui(self):
        self.setWindowTitle("SSH工具 - 美观、简单、便捷")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("""
        QMainWindow {
            background-color: #23272e;
            color: #d3dae3;
        }
        QTreeWidget {
            background-color: #282c34;
            border: none;
            color: #d3dae3;
            selection-background-color: #3a3f4b;
        }
        QTabWidget::pane {
            border-top: 2px solid #3a3f4b;
        }
        QTabBar::tab {
            background: #23272e;
            color: #d3dae3;
            padding: 8px 20px;
            border-radius: 4px 4px 0 0;
        }
        QTabBar::tab:selected {
            background: #3a3f4b;
            color: #4ec9b0;
        }
        QTextEdit, QLineEdit {
            background-color: #1e1e1e;
            color: #4ec9b0;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 13px;
            border: 1px solid #3a3f4b;
            border-radius: 3px;
        }
        QPushButton {
            background-color: #3a3f4b;
            color: #d3dae3;
            border: 1px solid #4ec9b0;
            border-radius: 4px;
            padding: 6px 16px;
        }
        QPushButton:hover {
            background-color: #4ec9b0;
            color: #23272e;
        }
        QStatusBar {
            background: #23272e;
            color: #d3dae3;
        }
        """)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        left_panel = self.create_connection_panel()
        main_layout.addWidget(left_panel, 1)
        right_panel = self.create_terminal_panel()
        main_layout.addWidget(right_panel, 3)
        self.create_menu_bar()
    
    def create_connection_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        title = QLabel("连接列表")
        title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        self.connection_tree = QTreeWidget()
        self.connection_tree.setHeaderLabel("服务器")
        self.connection_tree.itemDoubleClicked.connect(self.connect_to_server)
        layout.addWidget(self.connection_tree)
        button_layout = QHBoxLayout()
        new_btn = QPushButton("新建")
        new_btn.clicked.connect(self.show_new_connection_dialog)
        button_layout.addWidget(new_btn)
        edit_btn = QPushButton("编辑")
        edit_btn.clicked.connect(self.edit_connection)
        button_layout.addWidget(edit_btn)
        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(self.delete_connection)
        button_layout.addWidget(delete_btn)
        layout.addLayout(button_layout)
        return panel
    
    def create_terminal_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_terminal_tab)
        layout.addWidget(self.tab_widget)
        return panel
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        new_action = QAction('新建连接', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.show_new_connection_dialog)
        file_menu.addAction(new_action)
        exit_action = QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        view_menu = menubar.addMenu('视图')
        theme_action = QAction('切换主题', self)
        theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(theme_action)
    
    def show_new_connection_dialog(self):
        dialog = ConnectionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            connection = dialog.get_connection()
            self.connection_manager.save_connection(connection)
            self.load_connections()
    
    def edit_connection(self):
        current_item = self.connection_tree.currentItem()
        if current_item:
            connection = current_item.data(0, Qt.ItemDataRole.UserRole)
            if connection:
                dialog = ConnectionDialog(self, connection)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    new_connection = dialog.get_connection()
                    self.connection_manager.save_connection(new_connection)
                    self.load_connections()
    
    def delete_connection(self):
        current_item = self.connection_tree.currentItem()
        if current_item:
            connection = current_item.data(0, Qt.ItemDataRole.UserRole)
            if connection:
                reply = QMessageBox.question(
                    self, '确认删除', 
                    f'确定要删除连接 \"{connection.name}\" 吗？',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.connection_manager.delete_connection(connection.name)
                    self.load_connections()
    
    def load_connections(self):
        self.connection_tree.clear()
        connections = self.connection_manager.get_all_connections()
        groups = {}
        for conn in connections:
            if conn.group not in groups:
                groups[conn.group] = []
            groups[conn.group].append(conn)
        for group_name, group_connections in groups.items():
            group_item = QTreeWidgetItem([group_name])
            group_item.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
            for conn in group_connections:
                conn_item = QTreeWidgetItem([conn.name])
                conn_item.setIcon(0, self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
                conn_item.setData(0, Qt.ItemDataRole.UserRole, conn)
                group_item.addChild(conn_item)
            self.connection_tree.addTopLevelItem(group_item)
            group_item.setExpanded(True)
    
    def connect_to_server(self, item, column):
        connection = item.data(0, Qt.ItemDataRole.UserRole)
        if connection:
            self.create_terminal_tab(connection)
    
    def create_terminal_tab(self, connection):
        terminal_widget = TerminalWidget(connection)
        tab_index = self.tab_widget.addTab(terminal_widget, connection.name)
        self.tab_widget.setCurrentIndex(tab_index)
        self.ssh_clients[tab_index] = terminal_widget.ssh_client
    
    def close_terminal_tab(self, index):
        if index in self.ssh_clients:
            self.ssh_clients[index].disconnect()
            del self.ssh_clients[index]
        self.tab_widget.removeTab(index)
    
    def toggle_theme(self):
        QMessageBox.information(self, "主题", "主题切换功能待实现")
    
    def closeEvent(self, event):
        for client in self.ssh_clients.values():
            client.disconnect()
        event.accept()
