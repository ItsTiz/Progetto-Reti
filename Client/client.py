import os, sys

## dependencies
UTILS_DIR = os.path.relpath("../Utils/",".")
sys.path.append(os.path.dirname(UTILS_DIR))

from Utils.utils import clientSocket, commandParser

## start client
client = clientSocket(commandParser('A client for UDP data transfer').parse_args())
client.start()

    

