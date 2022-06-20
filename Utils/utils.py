#!/usr/bin/env python
# coding: utf-8

# In[ ]:


##################################### Message data type
from dataclasses import dataclass
from enum import Enum
import os

class MessageType(Enum):
    RESPONSE = 0
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
    
##################################### Message utility functions
from hashlib import md5

#checksum function
def checksum(mess: bytes):
    return md5(mess).digest()

# message integrity check
def check_integrity(message: Message):
    return message.checksum == checksum(message.data())


##################################### prove checksum
#header = "get".encode(encoding='utf-8')
#payload = "provaprova".encode(encoding='utf-8')
#metadata = "index=1".encode(encoding='utf-8')
#_mess=Message(header, payload, metadata, "")
#mess=Message(header, payload, metadata, checksum(_mess.data()))
#print(check_integrity(mess))


##################################### files function
def getDir(directory):
    return [f for f in os.listdir('.')]
    
def exists(file):
    return any(filter(os.path.exists, [file]))

from functools import partial
def readFile(filename: str, file_consumer, block_size = 2**10):
    with open(filename, 'rb') as f:
        for block in iter(partial(f.read, block_size), b''):
            file_consumer(block)
        
##################################### test read file with func for blocks
#def processFileBlock(block : bytes):
#    print(block)
#readFile("prova.mp4", processFileBlock, 20)


##################################### socket functions
import socket as sk
from threading import Thread
import signal

class serverSocket(Thread):
    socket: sk.socket
    address : (str, int)

    # socket creation
    def __init__(self, address : (str, int)):
        # init thread
        super().__init__(daemon=True)
        # init socket
        self.address = address
        self.socket = sk.socket(sk.AF_INET, sk.SOCK_DGRAM)
        self.socket.bind(self.address)
        # catch forced interrupts
        signal.signal(signal.SIGINT, self.close)
        
    # socket destructor
    def __del__(self):
        self.close()
        
    def close(self, signal=None, frame=None):
        # clear conneaction
        self.socket.close()
        
    def run(self):
        # start message heandler in other thread
        print("listening on", self.address)
        while True:
            data, address = self.socket.recvfrom(4096)
            print (data.decode('utf8'))
            
##################################### test server 
#server = serverSocket(("127.0.0.1", 10006))
#server.start()





##################################### TODO
#def decode(mess: Message) -> Response:
#    if Message.kind == MessageType.GET:
#        return processGET(mess)
#    if Message.kind == MessageType.PUT:
#        return processPUT(mess)
#    return processResponse(mess)
#

#def processGET(mess: Message) -> Response:
#    # check file existance
#    if not exists(mess.payload):
#        return Response.ERROR
#    # send PUT
#    sendPUT(filename)
#    
#    # file exists
#    return Response.OK
#   

#def processPUT(mess: Message) -> Response:

#def processRESPONSE(mess: Message) -> Response:
    
    
#def sendGET(request:str) -> Response:
    
#    request.encode(encoding='utf-8')
    
#def sendPUT(file_block:bytes) -> Response:
    # send file

#def send(payload:bytes)
    
#def sendResponse() -> Response:
#    mess = Message(MessageType.RESPONSE, )

