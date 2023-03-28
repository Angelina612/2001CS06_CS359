from socket import *
import sys

serverName = sys.argv[1]
serverPort = int(sys.argv[2])
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind((serverName,serverPort))
serverSocket.listen(1)
print ('The server is ready to receive')

while True:
    connectionSocket, addr = serverSocket.accept()
    print('Connected with client')
    while True:
        expression = connectionSocket.recv(1024).decode()

        if not expression:
            break

        print('Client socket ',addr, 'sent message: ',expression, sep='')

        try:
            message = eval(expression)
        except Exception as e:
            message = type(e).__name__ + ' - ' + str(e)

        print('Sending reply: ', message, sep='')
        connectionSocket.send(str(message).encode())
    connectionSocket.close()