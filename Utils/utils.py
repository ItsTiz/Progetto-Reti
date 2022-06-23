#!/usr/bin/env python
# coding: utf-8
   
#Message utility
from Utils.messageType import *

from Utils.messageType import _KIND_SIZE, _CHECKSUM_SIZE

#Socket utiity
import socket as Socket
from threading import Thread
import signal, sys
import  os


############################################################### command funcitonss
          

def decodeMessageType(command:bytes) -> MessageType:
   #def decode(mess: Message) -> Response
    print(command)
    if command == MessageType.LIST.to_bytes(_KIND_SIZE,byteorder='big'):
        return MessageType.LIST
    if command == MessageType.GET.to_bytes(_KIND_SIZE,byteorder='big'):
        return MessageType.GET
    if command == MessageType.PUT.to_bytes(_KIND_SIZE,byteorder='big'):
        return MessageType.PUT


def decodeMessage(command) -> Message:
   #def decode(mess: Message) -> Response
   messageType = decodeMessageType(command[0:_KIND_SIZE])
   print("Messagetype: ", messageType)
   payload =    command[ _KIND_SIZE : len(command) - _CHECKSUM_SIZE]
   checksum =   command[-_CHECKSUM_SIZE : ]
   
   return Message().fromData(messageType, payload, checksum)
    
def processMessage(mess : Message, sock : Socket.socket, address) :
    if mess.kind == MessageType.LIST:
        return sendLIST(sock,address)
    if mess.kind == MessageType.GET:
        return sendGET(mess)
    if mess.kind == MessageType.PUT:
        return sendPUT(mess)
    return processResponse(mess)

    
def sendLIST(sock,address):
    #print("-LIST-")
    message = Message().fromKind(MessageType.LIST, ';'.join(getDir(".")).encode(encoding='utf-8'))
    #sock.sock.sendto(message.raw(), server_address)
    sock.sendto(message.raw(),address)

def sendGET(args):
    print("-GET-",args)
    return

def sendPUT(args):
    print("-PUT-",args)
    return
    


############################################################### files function

# get files in directory
def getDir(directory):
    return [f for f in os.listdir(directory) if os.path.isfile(f)]
    
def exists(file):
    return any(filter(os.path.exists, [file]))

from functools import partial
def readFile(filename: str, file_consumer, block_size = 2*10):
    with open(filename, 'rb') as f:
        for block in iter(partial(f.read, block_size), b''):
            file_consumer(block)
        


############################################################### prove checksum
#header = "get".encode(encoding='utf-8')
#payload = "provaprova".encode(encoding='utf-8')
#metadata = "index=1".encode(encoding='utf-8')
#_mess=Message(header, payload, metadata, "")
#mess=Message(header, payload, metadata, checksum(_mess.data()))
#print(check_integrity(mess))



###############################################################
###############################################################
###############################################################
###############################################################
############################################################### Server Socket

class serverSocket():
    socket: Socket.socket
    address : (str, int)

    #Constructor
    def __init__(self, address : (str, int)):
       
        # init socket
        self.address = address
        
        #Binding with udp socket
        self.socket = Socket.socket(Socket.AF_INET, Socket.SOCK_DGRAM)
        self.socket.setsockopt(Socket.SOL_SOCKET, Socket.SO_REUSEADDR, 1) 
        self.socket.bind(self.address)
       
        # catch forced interrupts
        signal.signal(signal.SIGINT, self.close)
            
        
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
    def start(self):
        # start message heandler in other thread
        print("listening on", self.address)
        
        while True:
            data, address = self.socket.recvfrom(4096)
            #data = data.decode('utf8')
            
            #decode
            print("input:",data);
            message = decodeMessage(data)
            print("message:",message.raw())
            
            #check integrity
            print("integrity:",check_integrity(message))
            #process
            processMessage(message, self.socket, address)
            
            print("-----------------")
            
        
        #server_address = ('localhost', 1000)
        #self.socket.sendto(data.encode('utf8'),server_address)
            
        #########################################
###############################################################
###############################################################
############################################################### Client Socket

class clientSocket():
    socket: Socket.socket
    address : (str, int)

    #Constructor
    def __init__(self, address : (str, int)):
       
        # init socket
        self.address = address
        
        #Binding with udp socket
        self.socket = Socket.socket(Socket.AF_INET, Socket.SOCK_DGRAM)
       
        # catch forced interrupts
        signal.signal(signal.SIGINT, self.close)
            
        
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
    def start(self):
        
        while True:
            input_command = input('Type in your command:')
            
            #header = MessageType.LIST
            #payload = "provaprova".encode(encoding='utf-8')
            #metadata = "index=1".encode(encoding='utf-8')
            mess=Message().fromKind(MessageType.LIST)
            print(mess.raw())
            sent = self.socket.sendto(mess.raw(), self.address)
            
            data, address = self.socket.recvfrom(4096)
            print("input:",data);
            message = decodeMessage(data)
            print("message:",message.raw())
            
            #check integrity
            print("integrity:",check_integrity(message))
            print("payload", message.payload)
            print("checksum", message.checksum)
            print("-----------------")
            
        
        #server_address = ('localhost', 1000)
        #self.socket.sendto(data.encode('utf8'),server_address)
            
            
##################################### test server 
#server = serverSocket(("127.0.0.1", 10006))
#server.start()

