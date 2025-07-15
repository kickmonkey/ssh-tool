from PyQt6.QtCore import QObject, pyqtSignal
import paramiko
import threading
import time
import re

class SSHClient(QObject):
    output_received = pyqtSignal(str)
    connection_status = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.client = None
        self.shell = None
        self.connected = False
        self.connection = None  # 保存连接对象，便于命令时获取提示符等信息
        self.lock = threading.Lock()  # 防止多线程同时访问 shell

    def connect(self, connection):
        self.connection = connection
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if connection.private_key_path:
                self.client.connect(
                    hostname=connection.host,
                    port=connection.port,
                    username=connection.username,
                    key_filename=connection.private_key_path
                )
            else:
                self.client.connect(
                    hostname=connection.host,
                    port=connection.port,
                    username=connection.username,
                    password=connection.password
                )
            self.shell = self.client.invoke_shell()
            self.connected = True
            self.connection_status.emit("已连接")
            self.output_thread = threading.Thread(target=self._read_output)
            self.output_thread.daemon = True
            self.output_thread.start()
        except Exception as e:
            self.connection_status.emit(f"连接失败: {str(e)}")
    
    def _read_output(self):
        # 用于监听服务器主动推送的异步消息（如广播、警告等）
        while self.connected and self.shell:
            try:
                if self.shell.recv_ready():
                    output = self.shell.recv(1024).decode('utf-8', errors='ignore')
                    self.output_received.emit(output)
                time.sleep(0.1)
            except Exception as e:
                break

    def send_command(self, command: str):
        if self.shell and self.connected:
            with self.lock:
                self.shell.send(command + '\n')
                output = ""
                # 假设提示符为 username@host$，可根据实际情况调整
                prompt_pattern = re.escape(f"{self.connection.username}@{self.connection.host}$")
                start_time = time.time()
                while True:
                    if self.shell.recv_ready():
                        recv = self.shell.recv(4096).decode('utf-8', errors='ignore')
                        output += recv
                        # 检查是否出现了新的提示符
                        if re.search(prompt_pattern, output):
                            break
                    else:
                        time.sleep(0.05)
                    # 超时保护，防止死循环
                    if time.time() - start_time > 10:
                        break
                self.output_received.emit(output)
    
    def disconnect(self):
        self.connected = False
        if self.shell:
            self.shell.close()
        if self.client:
            self.client.close()
        self.connection_status.emit("已断开")
