from socket import *
import sys

# serverName = '127.0.0.1' 
# serverPort = 12000
# 192.168.59.213
serverName = sys.argv[1]
serverPort = int(sys.argv[2])
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))
print('Connected to server')
expression = input('Please enter the message to the server: ')
clientSocket.send(expression.encode())
modifiedSentence = clientSocket.recv(1024).decode()
print ('From Server: ',  modifiedSentence)
clientSocket.close()