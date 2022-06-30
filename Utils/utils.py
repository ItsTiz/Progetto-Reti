#!/usr/bin/env python
# coding: utf-8
   
#Message utility
from Utils.messageType import MessageType, Message, check_integrity

from Utils.messageType import _KIND_SIZE, _CHECKSUM_SIZE

#Socket utiity
import socket as Socket
from socket import timeout
from threading import Thread
import signal, sys
import  os
import argparse


##########################################
##########################################
# connectionHandler
# 
# handles protocol, connection, and files
#
class connectionHandler:
    
    
    ############################################################### variables
    
    ## configurations
    # from where to get files
    input_DIR = "./"
    # to where to put files
    output_DIR = "./"
    # max number of tries for each message sent
    MAX_TRIES = 5
    ## constants
    EOF_message = Message().fromKind(MessageType.PUT, b"END_OF_FILE")
    OK_message = Message().fromKind(MessageType.OK)
    ERROR_message = Message().fromKind(MessageType.ERROR)
    WRONG_FILE_message = Message().fromKind(MessageType.WRONG_FILE)
    # private 
    lastMessage : bytes = b""
    # opened file
    file = None
    
    ############################################################### funcitons
            
    
    ##############
    # decode command strings into messages
    #
    # @parameter 
    # command: "list" "get <file>" "put <file>"
    #    
    # @return 
    # Message: the corresponding message
    # bool: True if command is correct, False otherwise
    def decodeInput(self, command:str) -> (Message, bool): 
        if command == "list":
            return (Message().fromKind(MessageType.LIST), True)
        if command.startswith("get"):
            #split command
            comms = command.split(sep=" ",maxsplit=1)
            return (Message().fromKind(MessageType.GET,command.split(sep=" ",maxsplit=1)[1].encode(encoding="utf-8")) , True) if len(comms) == 2 else (Message(), False) 
        if command.startswith("put"):
            # split command
            comms = command.split(sep=" ",maxsplit=1)
            if not self._exists(os.path.join(self.input_DIR, comms[1])) :
                return (Message().fromKind(MessageType.WRONG_FILE), True)
            return (Message().fromKind(MessageType.PUT,comms[1].encode(encoding="utf-8")) , True) if len(comms) == 2 else (Message(), False) 
        return (Message(), False)
    
    
    ##############
    # decode raw bytes into messages
    #
    # @parameter 
    # command: raw bytes
    #    
    # @return 
    # Message: the corresponding message
    def decodeMessage(self, command: bytes) -> Message:
        # decoding messageType        
        messageType = MessageType.decode(command[0:_KIND_SIZE])
        # decoding payload
        payload =    command[ _KIND_SIZE : len(command) - _CHECKSUM_SIZE]
        # decoding checksum
        checksum =   command[-_CHECKSUM_SIZE : ]
        return Message().fromData(messageType, payload, checksum)
        
    
    ##############
    # protocol-based parser for input messages
    #
    # @parameter 
    # mess: input message
    # sock: socket to use
    # address: (ip, port) to use
    #    
    def processMessage(self, mess : Message, sock : Socket.socket = None, address : (str, int) = None) :
        if mess.kind == MessageType.LIST:
            return self._sendLIST_REPLY(sock,address)
        if mess.kind == MessageType.LIST_REPLY:
            return print("\n".join(self._parseLIST_REPLY(mess.payload)))
        if mess.kind == MessageType.GET:
            return self._sendPUT(mess.payload, sock, address)
        if mess.kind == MessageType.PUT:
            self._parsePUT(mess.payload, sock, address)
            # send ok
            self._sendTo(sock, address, self.OK_message.raw())
            return 
        if mess.kind == MessageType.ERROR:
            # resend last command
            return self._sendTo(sock, address, self.lastMessage)
        if mess.kind == MessageType.WRONG_FILE:
            return print("Could not find specified file")
        if mess.kind == MessageType.OK:
            # received ok and continue send put
            if self.file != None :
                return self._sendPUT(mess.payload, sock, address)
    
        
    ##############
    # LIST_REPLY sender
    #
    # @parameter 
    # sock: socket to use
    # address: (ip, port) to use
    #    
    def _sendLIST_REPLY(self, sock : Socket.socket, address: (str, int)):
        print("\nSending list ");
        files =  ';'.join(self._getDir(os.path.abspath(self.input_DIR))).encode(encoding='utf-8')
        message = Message().fromKind(MessageType.LIST_REPLY, files)
        self._sendTo(sock, address, message.raw())
    
    
    ##############
    # PUT sender
    #
    # @parameter 
    # mess: input message
    # sock: socket to use
    # address: (ip, port) to use
    #    
    def _sendPUT(self, mess: bytes, sock : Socket.socket, address: (str, int)):
        # if file not opened
        if self.file == None :
            if not self._exists(os.path.join(self.input_DIR,mess.decode(encoding='utf-8'))) :
                # send error
                self._sendTo(sock, address, self.WRONG_FILE_message.raw())
                return
            print("\nSending: ",mess.decode(encoding='utf-8'));
            # open file
            self._openFile(os.path.abspath(os.path.join(self.input_DIR, mess.decode(encoding='utf-8'))), "rb")
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
            print("Sent.\n");
            return
        else :
            # send file block
            outMess = Message().fromKind(MessageType.PUT, block).raw()
            self._sendTo(sock, address, outMess)
            return
        return
    
    
    ##############
    # PUT parser
    #
    # @parameter 
    # mess: input message
    # sock: socket to use
    # address: (ip, port) to use
    #    
    def _parsePUT(self, mess:bytes, sock : Socket.socket, address: (str, int)):
        ## if received EOF
        if mess == self.EOF_message.payload:
            self._closeFile()
            print("Received.\n");
            return
        ## if file not yet opened
        if self.file == None :
            print("\nReceiving: ",mess.decode(encoding='utf-8'));
            self._openFile(os.path.abspath(os.path.join(self.output_DIR, mess.decode(encoding='utf-8'))), "wb")
            return
        # write file block
        self._writeFile(mess)
        return

    ##############
    # LIST_REPLY sender
    #
    # @parameter 
    # mess: input message
    # sock: socket to use
    # address: (ip, port) to use
    #    
    def _parseLIST_REPLY(self,payload:bytes):
        return payload.decode(encoding="utf-8").split(sep=";");
    
    
    ##############
    # socket bytes sending function
    #
    # @parameter 
    # mess: input message
    # sock: socket to use
    # address: (ip, port) to use
    #  
    def _sendTo(self, sock,address, mess: bytes) -> bool:
        # save last message
        if self.decodeMessage(mess).kind != MessageType.ERROR :
            self.lastMessage = mess
        # try to send
        tries = self.MAX_TRIES
        while tries>0:
            try:
                sock.sendto(mess,address)
            except timeout:
                print(address,"is unreachable")
                tries = tries-1
                continue
            return True
        return False
    
    
    ##############
    # socket listnening function
    #
    # @parameter 
    # mess: input message
    # sock: socket to use
    # address: (ip, port) to use
    #  
    # @return: 
    # bool: True if responding, False otherwise
    # bytes: bytes received
    # (str, int): address from which been receiving
    def _listenTo(self, sock, addr) -> (bool, bytes, (str,int)) :
        # try to receive
        tries = self.MAX_TRIES
        while tries>0:
            try:
                data, address = sock.recvfrom(4096)
            except timeout:
                print("Timeout, resending..")
                # resend last message
                self._sendTo(sock, addr, self.lastMessage)
                tries = tries-1
                continue
            return True, data, address
        # address not responding, close file 
        if self.file != None :
            self._closeFile()
        return False, None, None
    
    ############################################################### file function
    
    ##############
    # directory scanner
    #
    # @parameter 
    # directory: directory to scan
    #  
    # @return: 
    # list of files
    def _getDir(self, directory):
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) ]
    
    
    ##############
    # file checker
    #
    # @parameter 
    # file: file to check
    def _exists(self, file):
        return os.path.exists(file)
        
    
    ##############
    # file opener
    #
    # @parameter 
    # filename: name of file
    # mode: how to open the file
    #  
    def _openFile(self, filename:str, mode:str):
        if self.file != None:
            self._closeFile()
        self.file = open(filename, mode)
        
    ##############
    # file closer
    #  
    def _closeFile(self):
        if self.file == None:
            return
        self.file.close()
        self.file = None

    ##############
    # file writer
    #
    # @parameter 
    # block: bytes to write
    #  
    def _writeFile(self, block: bytes):
        if self.file == None:
            return
        self.file.write(block)
        
    
    ##############
    # file reader
    #
    # @parameter 
    # block_size: number of bytes to read
    #  
    def _readFile(self, block_size = 2**10):
        if self.file == None:
            return b''
        return self.file.read(block_size)
    
    ###################################################### setters
        
    def setInputDir(self, directory):
        if not os.path.exists(directory):
            return
        self.input_DIR = directory
    
    def setOutputDir(self, directory):
        if not os.path.exists(directory):
            return
        self.output_DIR = directory
        
    def setMaxTries(self, maxTries):
        self.MAX_TRIES = maxTries
        
        
        


            
            
##########################################
##########################################
# clientSocket
# 
# interoperates with a server using protocol
#
class clientSocket(Thread):
    socket: Socket.socket
    address : (str, int)
    conn = connectionHandler()
    timeout = 3 #s

    #Constructor
    def __init__(self, args = None):
        
        # init thread
        super().__init__()
       
        # init address
        self.address = (args.ip, args.port)
        
        #Binding with udp socket
        self.socket = Socket.socket(Socket.AF_INET, Socket.SOCK_DGRAM)
        self.socket.settimeout(self.timeout)
       
        # catch forced interrupts
        signal.signal(signal.SIGINT, self.close)
        
        # parse args
        self.conn.setInputDir(args.input_DIR)
        self.conn.setOutputDir(args.output_DIR)
        self.conn.setMaxTries(args.max_tries)
        self.socket.settimeout(args.timeout)
        
        
    #Close socket - also called for SIGINT process calls
    def close(self, signal, frame):
        print("[Closing client]")
        # clear conneaction
        try:
          if(self):
            self.socket.close()
        finally:
            sys.exit(0)
    
    #Listening for input commands
    def run(self):
        
        while True:
            
            # parse CLI input
            input_command = input("> Type in your command:")
            
            # decode input into message
            input_mess, ok = self.conn.decodeInput(input_command)
            
            # check input command
            if not ok :
                print("Could not recognize \"", input_command, "\" as a command\n")
                continue
            
            # check if filename is wrong
            if input_mess.kind == MessageType.WRONG_FILE:
                print("File name is incorrect or couldn't find file\n")
                continue
            
            # check if put input command
            if input_mess.kind == MessageType.PUT:
                # send put correctly (and open file)
                self.conn._sendPUT(input_mess.payload, self.socket, self.address)
            else:   
                # send input command as message
                ok = self.conn._sendTo(self.socket, self.address, input_mess.raw())
                
                # check if connection timeout
                if not ok:
                    continue
            
            while True:
                
                # listen for server
                ok, data, message = self.conn._listenTo(self.socket, self.address)
            
                # if connection timeout
                if not ok:
                    break
                
                #decode
                message = self.conn.decodeMessage(data)
                    
                #check integrity
                if not check_integrity(message):
                    # send error
                    self.conn._sendTo(self.socket, self.address, self.conn.ERROR_message.raw())
                    continue
                
                # process
                self.conn.processMessage(message, self.socket, self.address)
                
                # stop listen if no file is opened, and any error/wrong_file message is received
                if self.conn.file == None and (message.kind != MessageType.ERROR or message.kind != MessageType.WRONG_FILE):
                    break
            

##########################################
##########################################
# serverSocket
# 
# interoperates with a cliebt using protocol
#
class serverSocket(Thread):
    socket : Socket.socket
    address : (str, int)
    connHandler = connectionHandler()

    #Constructor
    def __init__(self, args):
        
        # init thread
        super().__init__()
        
        # init address
        self.address = (args.ip, args.port)
        
        #Binding with udp socket
        self.socket = Socket.socket(Socket.AF_INET, Socket.SOCK_DGRAM)
        self.socket.setsockopt(Socket.SOL_SOCKET, Socket.SO_REUSEADDR, 1) 
        self.socket.bind(self.address)
       
        # catch forced interrupts
        signal.signal(signal.SIGINT, self.close)
        
        # parse args
        self.connHandler.setInputDir(args.input_DIR)
        self.connHandler.setOutputDir(args.output_DIR)
        self.connHandler.setMaxTries(args.max_tries)
        
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
    def run(self):
        
        print("Listening on", self.address,"\nReady for requests.")
        
        while True:
            
            # listen for client request
            try:
                data, address = self.socket.recvfrom(4096)
            except Exception:
                continue
            # decode
            message = self.connHandler.decodeMessage(data)
            
            #check integrity
            if not check_integrity(message):
                print("[Integrity ERROR]\n")
                # send error
                self.connHandler._sendTo(self.socket, address, self.connHandler.ERROR_message.raw())
                continue
                    
            #process
            self.connHandler.processMessage(message, self.socket, address)
                
    
            
    
##########################################
##########################################
# commandParser
# 
# parse options given to .py files
#
class commandParser(argparse.ArgumentParser):
    def __init__(self, descr:str):
        super().__init__(description=descr)
        self.add_argument('-ip',type=str,  dest='ip', default="127.0.0.1",
                            help='(server) set ip to bind to. (client) set ip to send to. Default is 127.0.0.1')
        self.add_argument('-p',type=int,  dest='port', default=10001,
                    help='(server) set port to bind to. (client) set port to send to. Default is 10001')
        self.add_argument('-in', type=str, dest='input_DIR', default=connectionHandler.input_DIR,
                            help='set the input directory, where files will be sent to the server. Default is current dir.')
        self.add_argument('-out', type=str, dest='output_DIR', default=connectionHandler.output_DIR,
                            help='set the output directory, where files will be received from the server. Default is current dir.')
        self.add_argument('-t',type=int,  dest='timeout', default=clientSocket.timeout,
                            help='set timeout for messages (in s). Default is 3s. ( only for clients )')
        self.add_argument('-tries',type=int,  dest='max_tries', default=connectionHandler.MAX_TRIES,
                            help='set max number of tries during reconnection. Default is 5.')

           