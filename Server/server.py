
import sys
import os

UTILS_DIR = os.path.relpath("../Utils/",".")
sys.path.append(os.path.dirname(UTILS_DIR))

from Utils.utils import serverSocket
    
##################################### test server 
server = serverSocket(("127.0.0.1", 10001))
server.start()
