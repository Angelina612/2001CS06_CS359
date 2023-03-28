from socket import *
import sys
from _thread import *


# thread function
def threaded(connectionSocket, addr):
    while True:
        expression = connectionSocket.recv(1024).decode()

        if not expression:
            break
        print('Client ',addr, ' sent message: ',expression, sep='')

        try:
            message = eval(expression)
        except Exception as e:
            message = type(e).__name__ + ' - ' + str(e)

        print('Sending reply: ', message, sep='')
        connectionSocket.send(str(message).encode())
    connectionSocket.close()


def Main():
    serverName = sys.argv[1]
    serverPort = int(sys.argv[2])
    serverSocket = socket(AF_INET,SOCK_STREAM)
    serverSocket.bind((serverName,serverPort))
    serverSocket.listen(1)
    print ('The server is ready to receive')

    while True:
        connectionSocket, addr = serverSocket.accept()
        print('Connected with client ', addr, sep='')
        
        # Start a new thread and return its identifier
        start_new_thread(threaded, (connectionSocket, addr, ))
    serverSocket.close()


if __name__ == '__main__':
	Main()
