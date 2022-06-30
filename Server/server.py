import os, sys

## dependencies
UTILS_DIR = os.path.relpath("../Utils/",".")
sys.path.append(os.path.dirname(UTILS_DIR))

from Utils.utils import serverSocket, commandParser

## start server
server = serverSocket(("127.0.0.1", 10001), commandParser('A Server for UDP data transfer').parse_args())
server.start()