##################################### Message data type
from dataclasses import dataclass
from enum import IntEnum
from hashlib import md5, sha256

############################################################### message funcitonss  
class Response(IntEnum):
    OK = 0
    ERROR = 1
        
_KIND_SIZE = 1
_CHECKSUM_SIZE = 32

class MessageType(IntEnum):
    #RESPONSE = 0
    LIST = 0
    GET = 1
    PUT = 2
    LIST_REPLY = 3
    OK = 4
    ERROR = 5
    
    def encoded(self):
        return self.to_bytes(_KIND_SIZE,byteorder='big')
    
    def decode(command:bytes):
        if command == MessageType.LIST.encoded():
            return MessageType.LIST
        if command == MessageType.LIST_REPLY.encoded():
            return MessageType.LIST_REPLY
        if command == MessageType.GET.encoded():
            return MessageType.GET
        if command == MessageType.PUT.encoded():
            return MessageType.PUT
        if command == MessageType.ERROR.encoded():
            return MessageType.ERROR
        if command == MessageType.OK.encoded():
            return MessageType.OK
    

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
        return self.kind.encoded()  + self.payload
    
    def raw(self) -> bytes:
        return self.data() + self.checksum
    
############################################################### checksum funcitonss      


#checksum function
def myChecksum(mess: bytes):
    return sha256(mess).digest()
    

# message integrity check
def check_integrity(message: Message):
    return message.checksum == myChecksum(message.data())
 
