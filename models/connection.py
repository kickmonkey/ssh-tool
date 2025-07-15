from dataclasses import dataclass
from typing import Optional

@dataclass
class SSHConnection:
    name: str
    host: str
    port: int
    username: str
    password: Optional[str] = None
    private_key_path: Optional[str] = None
    group: str = "默认"
