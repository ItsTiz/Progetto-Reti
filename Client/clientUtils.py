#!/usr/bin/env python
# coding: utf-8
   
#Message utility
from messageType import MessageType, Message, check_integrity

from messageType import _KIND_SIZE, _CHECKSUM_SIZE

#Socket utiity
import socket as Socket
from threading import Thread
import threading
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
    
def processMessage(mess : Message, optionalArg : str = "") :
    
    if mess.kind == MessageType.LIST_REPLY:
        return print("\n".join(parseLIST_REPLY(mess.payload)))
    if mess.kind == MessageType.PUT:
        writeFile(optionalArg, mess.payload)
    

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
            
            
def writeFile(filename: str, block):
    with open(filename, 'ab') as f:
        f.write(block)
        
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
        
        
        
    #Close socket - also called for SIGINT process calls
    def close(self, signal, frame):
        print("[Closing client]")
        # clear conneaction
        try:
          if(self):
            self.socket.close()
        finally:
            sys.exit(0)
    
    #Listeniong for client requests
    def start(self):
        
        createConn = 0;
        conn = None
        while True:
            
            #if(conn != None):
            #    conn.pause();
            input_command = input("Type in your command:")
            
            mess, ok = decodeInput(input_command)
            
            if not ok :
                print("Could not recognize \"", input_command, "\" as a command")
                continue
            #header = MessageType.LIST
            #payload = "provaprova".encode(encoding='utf-8')
            #metadata = "index=1".encode(encoding='utf-8')
            #mess=Message().fromKind(MessageType.LIST)
            
            sent = sendTo(self.socket, ("127.0.0.1", 10001), mess.raw())
            if(createConn == 0):
                createConn = 1
                conn = clientConnectionHandler(self.socket, self.address, mess)
            elif (createConn == 1):
                conn.setMessageArgument(mess)
                conn.resume()
            
            # create listening thread
            
            

class clientConnectionHandler(Thread):
    socket: Socket.socket
    address : (str, int)
    messSent: Message

    #Constructor
    def __init__(self, socket, address : (str, int), mess : Message):
        
        super(clientConnectionHandler, self).__init__(daemon=True)
        self.__flag = threading.Event() # The flag used to pause the thread
        self.__flag.set() # Set to True
        self.__running = threading.Event() # Used to stop the thread identification
        self.__running.set() # Set running to True
        
        # init socket
        self.address = address
        self.socket = socket     
        self.messSent = mess
        # autorun
        self.start()
        
        
    #Listeniong for client requests
    def run(self):
        print("listening for input...")
        
        data = None
        
        while True:
            
            
            data, address = self.socket.recvfrom(4096)
            #print("<--- input:",data);
            message = decodeMessage(data)
                
            if(message.payload == b"END_OF_FILE"):
                self.pause()
            
            #print("- message:",message.raw())
            
            #check integrity
            #print("- payload", message.payload)
            if self.messSent.kind != MessageType.LIST:
                processMessage(message,self.messSent.payload.decode())
            else:
                processMessage(message)
                
                
            #print("- payload", message.payload)
            #print("- integrity:",check_integrity(message))
            
            #print("-----------------")
            
    def pause(self):
        self.__flag.clear() # Set to False to block the thread

    def resume(self):
        self.__flag.set() # Set to True, let the thread stop blocking
        
    def stop(self):
        self.__flag.set() # Resume the thread from the suspended state, if it is already suspended
        self.__running.clear() # Set to False
           
             
    def setMessageArgument(self, message: Message):        
        self.messSent = message       
            