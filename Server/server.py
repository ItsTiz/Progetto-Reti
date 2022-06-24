
from serverUtils import serverSocket

##################################### test read file with func for blocks
#def processFileBlock(block : bytes):
#    print(block)
#readFile("prova.mp4", processFileBlock, 20)
import time
           
##################################### test server 
server = serverSocket(("127.0.0.1", 10001))
server.start()

##################################### TODO
#def decode(mess: Message) -> Response:
#    if Message.kind == MessageType.GET:
#        return processGET(mess)
#    if Message.kind == MessageType.PUT:
#        return processPUT(mess)
#    return processResponse(mess)
#

#def processGET(mess: Message) -> Response:
#    # check file existance
#    if not exists(mess.payload):
#        return Response.ERROR
#    # send PUT
#    sendPUT(filename)
#    
#    # file exists
#    return Response.OK
   

#def processPUT(mess: Message) -> Response:

#def processRESPONSE(mess: Message) -> Response:
    
    
#def sendGET(request:str) -> Response:
    
#    request.encode(encoding='utf-8')
    
#def sendPUT(file_block:bytes) -> Response:
    # send file

#def send(payload:bytes)
    
#def sendResponse() -> Response:
#    mess = Message(MessageType.RESPONSE, )
