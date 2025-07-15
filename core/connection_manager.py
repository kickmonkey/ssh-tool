import sqlite3
from typing import List
from models.connection import SSHConnection
from utils.encryption import get_or_create_key, encrypt, decrypt

class ConnectionManager:
    def __init__(self, db_path="ssh_connections.db"):
        self.db_path = db_path
        self.cipher_key = get_or_create_key()
        self._init_database()
    
    def _init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS connections (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                host TEXT,
                port INTEGER,
                username TEXT,
                password_encrypted TEXT,
                private_key_path TEXT,
                group_name TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def save_connection(self, ssh_conn: SSHConnection):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        encrypted_password = None
        if ssh_conn.password:
            encrypted_password = encrypt(ssh_conn.password, self.cipher_key)
        cursor.execute('''
            INSERT OR REPLACE INTO connections 
            (name, host, port, username, password_encrypted, private_key_path, group_name)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (ssh_conn.name, ssh_conn.host, ssh_conn.port, ssh_conn.username,
              encrypted_password, ssh_conn.private_key_path, ssh_conn.group))
        conn.commit()
        conn.close()
    
    def get_all_connections(self) -> List[SSHConnection]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM connections')
        rows = cursor.fetchall()
        conn.close()
        connections = []
        for row in rows:
            password = None
            if row[5]:
                password = decrypt(row[5], self.cipher_key)
            connections.append(SSHConnection(
                name=row[1], host=row[2], port=row[3], username=row[4],
                password=password, private_key_path=row[6], group=row[7]
            ))
        return connections
    
    def delete_connection(self, name: str):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM connections WHERE name = ?', (name,))
        conn.commit()
        conn.close()
