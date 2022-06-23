##################################### Message data type
from dataclasses import dataclass
from enum import Enum

class MessageType(Enum):
    #RESPONSE = 0
    LIST = 0
    GET = 1
    PUT = 2

class Response(Enum):
    OK = 0
    ERROR = 1
    

@dataclass
class Message:
    kind: MessageType
    metadata: bytes
    payload: bytes
    checksum: bytes
    
    def data(self) -> bytes:
        return self.kind + self.metadata + self.payload