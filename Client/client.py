from clientUtils import clientSocket

##################################### test client 
client = clientSocket(("127.0.0.1", 10001))
client.start()
    
