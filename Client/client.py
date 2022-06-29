
import sys
import os

UTILS_DIR = os.path.relpath("../Utils/",".")
sys.path.append(os.path.dirname(UTILS_DIR))


from Utils.utils import clientSocket

##################################### test client 
client = clientSocket(("127.0.0.1", 10001))
client.start()

    
