import socket as Socket
import signal,sys
from Utils.utils import *

##################################### test client 
client = clientSocket(("127.0.0.1", 10001))
client.start()
    
