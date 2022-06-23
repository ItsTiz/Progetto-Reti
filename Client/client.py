import socket as Socket
import signal,sys
from Utils.messageType import *

def signal_handler(signal, frame):
    print( 'Exiting client (Ctrl+C pressed)')
    try:
      if(sock):
        sock.close()
    finally:
      sys.exit(0)
      
def splitCommand(inputString):
    result = inputString.split()
    
    if(len(result) == 0 or len(inputString) == 0):
        return ("","")
    if(len(result) == 1):
        return (inputString.split()[0], "")
    else:
        return (inputString.split()[0],inputString.split()[1])
    
def decodeCommand(command, args):
   #def decode(mess: Message) -> Response
       
    if command == "LIST":
        sendLIST()
    if command == "GET":
        sendGET(args)
    if command == "PUT":
        sendPUT(args)
    
def sendLIST():
    print("-LIST-")
    return

def sendGET(args):
    print("-GET-",args)
    return

def sendPUT(args):
    print("-PUT-",args)
    return
    
    
def run():
    print("Welcome!\n")

    # Create il socket UDP

    sock = Socket.socket(Socket.AF_INET, Socket.SOCK_DGRAM)
    print("Socket has been created.\n")
    

    #ásignal.signal(signal.SIGINT, signal_handler)    
    
    
    while True:
        
        input_command = input('Type in your command:')
        
        (command, args) = splitCommand(input_command)
        
        while (command, args) == ("",""):
            input_command = input('Type in your command:')
            (command, args) = splitCommand(input_command)
       
    
        decodeCommand(command, args)
        print("No command found for" + "\""+ command +"\"\n")
    
run()
    
