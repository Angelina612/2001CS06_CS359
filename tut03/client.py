from socket import *
import sys

serverName = sys.argv[1]
serverPort = int(sys.argv[2])
clientSocket = socket(AF_INET, SOCK_STREAM)

clientSocket.connect((serverName,serverPort))
print('Connected to server')

f = True
while f:
    expression = input('Please enter the message to the server: ')
    clientSocket.send(expression.encode())
    answer = clientSocket.recv(1024).decode()
    print ('Server replied: ',  answer, sep='')
    y = input('Do you wish to continue (Y/N)? ')
    
    while True:
        if y == 'N' or y == 'n':
            clientSocket.close()
            f = False
            break
        elif y == 'y' or y == 'Y':
            break
        y = input('Please enter Y or N: ')
