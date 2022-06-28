
from utils import serverSocket

           
##################################### test server 
server = serverSocket(("127.0.0.1", 10001))
server.start()
