from socket import *
import sys
from select import *
import queue

serverName = sys.argv[1]
serverPort = int(sys.argv[2])
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind((serverName,serverPort))
serverSocket.listen(1)
print ('The server is ready to receive')

inputs = [serverSocket]
outputs = []

message_queues = {}

while inputs:
    readable, writable, exceptional = select(inputs, outputs, inputs)

    # Handle inputs
    for s in readable:
        if s is serverSocket:
            # A "readable" server socket is ready to accept a connection
            connectionSocket, addr = s.accept()
            print('Connected with client ', addr, sep='')
            
            connectionSocket.setblocking(0)
            inputs.append(connectionSocket)

            # Give the connection a queue for data we want to send
            message_queues[connectionSocket] = queue.Queue()
        else:
            expression = s.recv(1024).decode()

            if not expression:
                # Stop listening for input on the connection
                if s in outputs:
                    outputs.remove(s)
                inputs.remove(s)
                s.close()
                # Remove message queue
                del message_queues[s]

            else:
                # A readable client socket has data
                print('Client ', s.getpeername(), ' sent message: ',expression, sep='')

                try:
                    answer = eval(expression)
                except Exception as e:
                    answer = type(e).__name__ + ' - ' + str(e)

                message_queues[s].put(answer)
                # Add output channel for response
                if s not in outputs:
                    outputs.append(s)

    # Handle outputs
    for s in writable:
        try:
            message = message_queues[s].get_nowait()
        except queue.Empty:
            # No messages waiting so stop checking for writability.
            outputs.remove(s)
        else:
            print('Sending reply: ', message, sep='')
            s.send(str(message).encode())

    # Handle "exceptional conditions"
    for s in exceptional:
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()
        # Remove message queue
        del message_queues[s]