#Message utility
from messageType import MessageType, Message, check_integrity

from messageType import _KIND_SIZE, _CHECKSUM_SIZE

#Socket utiity
import socket as Socket
from threading import Thread
import signal, sys
from math import ceil
import  os
import time

class connectionHandler:
    
    input_DIR = os.path.abspath("/Users/utenteadmin/Desktop/UNIBO/2021-2022/2° semestre/Programmazione di Reti/")
    output_DIR = os.path.abspath("/Users/utenteadmin/Desktop/UNIBO/2021-2022/2° semestre/Programmazione di Reti/Progetto/Progetto-Reti/Client")
    EOF_message = Message().fromKind(MessageType.PUT, b"END_OF_FILE")
    OK_message = Message().fromKind(MessageType.OK)
    ERROR_message = Message().fromKind(MessageType.ERROR)
    reading_file = False
    lastMessage = Message()
    #file
    file = None
    file_index = 0
    
    ############################################################### command funcitonss
    
    
    def decodeMessage(self, command) -> Message:
       #def decode(mess: Message) -> Response
       messageType = MessageType().decode(command[0:_KIND_SIZE])
       print("Messagetype: ", messageType)
       payload =    command[ _KIND_SIZE : len(command) - _CHECKSUM_SIZE]
       checksum =   command[-_CHECKSUM_SIZE : ]
       return Message().fromData(messageType, payload, checksum)
        
    
    def processMessage(self, mess : Message, sock = None, address = None) :
        if mess.kind == MessageType.LIST:
            return self._sendLIST_REPLY(sock,address)
        if mess.kind == MessageType.LIST_REPLY:
            return print("\n".join(self._parseLIST_REPLY(mess.payload)))
        if mess.kind == MessageType.GET:
            return self._sendPUT(mess.payload, sock, address)
        if mess.kind == MessageType.PUT:
            self._writeFile(mess.payload)
            self._sendTo(sock, address, self.OK_Message.raw())
        if mess.kind == MessageType.ERROR:
            return self._sendTo(sock, address, self.lastMessage.raw())
        if mess.kind == MessageType.OK:
            if self.reading_file :
                return self._sendPUT(mess.payload, sock, address)
            #return writeFile()
        #return processResponse(mess)
    
        
    def _sendLIST_REPLY(self, sock,address):
        files =  ';'.join(self._getDir(".")).encode(encoding='utf-8')
        message = Message().fromKind(MessageType.LIST_REPLY, files)
        #sock.sock.sendto(message.raw(), server_address)
        self._sendTo(sock, address, message.raw())
    
    
    def _sendPUT(self, mess, sock, address):
        # if file not opened
        if self.file == None :
            # open file
            self._openFile( mess, "rb")
            # send filename
            self._sendTo(sock, address, Message().fromKind(MessageType.PUT, mess).raw())
            return
        # read file block
        block = self._readFile(2**10)
        # if EOF
        if block == b'':
            # send EOF
            self._sendTo(sock, address, self.EOF_message.raw())
            # close file
            self._closeFile()
            return
        else :
            # send file block
            outMess = Message().fromKind(MessageType.PUT, block).raw()
            self._sendTo(sock, address, outMess)
            return
        return
    
    
    def _parsePUT(self, mess:bytes, sock, address):
        ## if received EOF
        if mess == self.EOF_message.payload:
            self._closeFile()
            return
        ## if file not yet opened
        if self.file == None :
            self._openFile(mess, "wb")
            return
        # write file block
        self._writeFile(mess)
        return


    def _parseLIST_REPLY(self,payload:bytes):
        return payload.decode(encoding="utf-8").split(sep=";");
    
    
    def _sendTo(self, sock,address, mess):
        #print("---> sending:",mess)
        self.lastMessage = mess
        sock.sendto(mess,address)
        
    
    ############################################################### files function
    
    
    # get files in directory
    def _getDir(self, directory):
        return [f for f in os.listdir(directory) if os.path.isfile(f)]
        
    
    def _readFile(self, block_size = 2**10):
        if self.file == None:
            return b''
        return self.file.read(block_size)
    
    def _openFile(self, filename:str, mode:str):
        self.file = open(filename, mode)
        
    def _closeFile(self):
        self.file.close()
        self.file = None

    
    def _writeFile(self, block):
        if self.file == None:
            return
        self.file.write(block)
        

def exists(file):
    return any(filter(os.path.exists, [file]))

###############################################################
###############################################################
###############################################################
###############################################################
############################################################### Server Socket

class serverSocket():
    socket: Socket.socket
    address : (str, int)
    connHandler= connectionHandler()

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
        
    #Close socket - also called for SIGINT process calls
    def close(self, signal, frame):
        print('[Closing server]')
        # clear conneaction
        try:
          if(self):
            self.socket.close()
        finally:
            sys.exit(0)
    
    #Listeniong for client requests
    def start(self):
        # start message heandler in other thread
        
        while True:
            print("listening on", self.address,"\nReady for requests...")
        
            data, address = self.socket.recvfrom(2**10)
            #data = data.decode('utf8')
        
            #decode
            print("<--- input:",data);
            message = self.connHandler.decodeMessage(data)
            #print("- message:",message.raw())
            
            #check integrity
            #print("- integrity:",check_integrity(message))
            if not check_integrity(message) == True:
                # TODO send response:ERROR
                continue
                    
            #process
            self.connHandler.processMessage(message, self.socket, address)
                
           # print("-----------------")
            