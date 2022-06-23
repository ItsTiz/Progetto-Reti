#!/usr/bin/env python
# coding: utf-8
   
#Message utility
from hashlib import md5
from Utils.messageType import Message

#Socket utiity
import socket as Socket
from threading import Thread
import signal, sys

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

class serverSocket(Thread):
    socket: Socket.socket
    address : (str, int)

    #Constructor
    def __init__(self, address : (str, int)):
        # init thread
        super().__init__(daemon=True)
        
       
        # init socket
        self.address = address
        
        #Binding with udp socket
        self.socket = Socket.socket(Socket.AF_INET, Socket.SOCK_DGRAM)
        self.socket.setsockopt(Socket.SOL_SOCKET, Socket.SO_REUSEADDR, 1) 
        self.socket.bind(self.address)
       
       
       
        # catch forced interrupts
        signal.signal(signal.SIGINT, self.close)
       
        self.run();
        
    #Destructor
    def __del__(self):
        self.close(None, None)
        
    #Close socket - also called for SIGINT process calls
    def close(self, signal, frame):
        print('[Closing server]')
        # clear conneaction
        try:
          if( self ):
            self.socket.close()
        finally:
          sys.exit(0)
    
    #Listeniong for client requests
    def run(self):
        # start message heandler in other thread
        print("listening on", self.address)
        
        
        # catch forced interrupts
        signal.signal(signal.SIGINT, self.close)
        
        while True:
            data, address = self.socket.recvfrom(4096)
            data = data.decode('utf8')
            print(data);
        
        #server_address = ('localhost', 1000)
        #self.socket.sendto(data.encode('utf8'),server_address)
            
            
##################################### test server 
#server = serverSocket(("127.0.0.1", 10006))
#server.start()

