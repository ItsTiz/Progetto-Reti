##################################### Message data type
from dataclasses import dataclass
from enum import IntEnum
from hashlib import md5, sha256

############################################################### message funcitonss  
class Response(IntEnum):
    OK = 0
    ERROR = 1
    
class MessageType(IntEnum):
    #RESPONSE = 0
    LIST = 0
    GET = 1
    PUT = 2
    LIST_REPLY = 3
    
    
_KIND_SIZE = 1
_CHECKSUM_SIZE = 32

class Message:
    kind: MessageType # 1 byte
    payload: bytes # n bytes
    checksum: bytes # 32 byte
    
    
    
    
    def fromKind (self, kind, payload=b""):
        self.kind = kind
        self.payload = payload
        self.checksum = myChecksum(self.data())
        return self
        
    def fromData (self, kind, payload, checksum):
        self.kind = kind
        self.payload = payload
        self.checksum = checksum
        return self
    
    def data(self) -> bytes:
        return self.kind.to_bytes(_KIND_SIZE,byteorder='big')  + self.payload
    
    def raw(self) -> bytes:
        return self.data() + self.checksum
    
############################################################### checksum funcitonss      


#checksum function
def myChecksum(mess: bytes):
    return sha256(mess).digest()
    

# message integrity check
def check_integrity(message: Message):
    return message.checksum == myChecksum(message.data())
 
