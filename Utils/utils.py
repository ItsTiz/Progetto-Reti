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


input_DIR = os.path.abspath("/Users/utenteadmin/Desktop/UNIBO/2021-2022/2° semestre/Programmazione di Reti/")
output_DIR = os.path.abspath("/Users/utenteadmin/Desktop/UNIBO/2021-2022/2° semestre/Programmazione di Reti/Progetto/Progetto-Reti/Client")

############################################################### command funcitonss
def decodeInput(command:str) -> (Message, bool): 
    if command == "list":
        return (Message().fromKind(MessageType.LIST), True)
    if command.startswith("get"):
        comms = command.split(sep=" ",maxsplit=1)
        return (Message().fromKind(MessageType.GET,command.split(sep=" ",maxsplit=1)[1].encode(encoding="utf-8")) , True) if len(comms) == 2 else (Message(), False) 
    if command == "put":
        return (Message(), False)
    return (Message(), False)
          

def decodeMessageType(command:bytes) -> MessageType:
   #def decode(mess: Message) -> Response
    if command == MessageType.LIST.to_bytes(_KIND_SIZE,byteorder='big'):
        return MessageType.LIST
    if command == MessageType.LIST_REPLY.to_bytes(_KIND_SIZE,byteorder='big'):
        return MessageType.LIST_REPLY
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
    
def processMessage(mess : Message, sock = None, address = None) :
    if mess.kind == MessageType.LIST:
        return sendLIST_REPLY(sock,address)
    if mess.kind == MessageType.LIST_REPLY:
        return print("\n".join(parseLIST_REPLY(mess.payload)))
    if mess.kind == MessageType.GET:
        return sendPUT(mess)
    if mess.kind == MessageType.PUT:
        return writeFile()
    return processResponse(mess)

    
def sendLIST_REPLY(sock,address):
    files =  ';'.join(getDir()).encode(encoding='utf-8')
    message = Message().fromKind(MessageType.LIST_REPLY, files)
    #sock.sock.sendto(message.raw(), server_address)
    sendTo(sock, address, message.raw())


def parseLIST_REPLY(payload:bytes):
    return payload.decode(encoding="utf-8").split(sep=";");

def sendGET(args):
    print("-GET-",args)
    return

def sendPUT(args):
    print("-PUT-",args)
    return

def sendTo(sock,address, mess):
    print("---> sending:",mess)
    sock.sendto(mess,address)
    


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
            print("<--- input:",data);
            message = decodeMessage(data)
            print("- message:",message.raw())
            
            #check integrity
            print("- integrity:",check_integrity(message))
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
        self.socket.settimeout(10)
       
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
            
            mess, ok = decodeInput(input_command)
            
            if not ok :
                print("wrong command")
                continue
            #header = MessageType.LIST
            #payload = "provaprova".encode(encoding='utf-8')
            #metadata = "index=1".encode(encoding='utf-8')
            #mess=Message().fromKind(MessageType.LIST)
            
            sent = sendTo(self.socket, self.address, mess.raw())
            
            data, address = self.socket.recvfrom(4096)
            print("<--- input:",data);
            message = decodeMessage(data)
            print("- message:",message.raw())
            
            #check integrity
            print("- integrity:",check_integrity(message))
            print("- payload", message.payload)
            processMessage(message)
            print("- checksum", message.checksum)
            print("-----------------")
            
        
        #server_address = ('localhost', 1000)
        #self.socket.sendto(data.encode('utf8'),server_address)
            
            
##################################### test server 
#server = serverSocket(("127.0.0.1", 10006))
#server.start()

