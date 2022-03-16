import sys
print (sys.version)
from socket import *
import random
import time
serverHost = ''
serverPort = 50007
serverSocket = socket(AF_INET, SOCK_STREAM)
sameState = False
prevPacket = None
serverSocket.bind(( serverHost, serverPort))
serverSocket.listen(1)
print ( 'The server is ready to receive ' )

while True:
    connectionID, addr = serverSocket.accept()
    print ("The server connected to: " + str(addr), connectionID )
    packet = connectionID.recv(1024).decode()
    seed1 = input('[Server] Input a number for the seed for the instance of the random number generator used for determining if ACKs have been corrupted ')
    random.seed(seed1)
    corrupted = random.randint(0, 100000) / 100000
    seq = int(packet[-2])
    ack = int(packet[-1])
    if len(packet) == 6:
        data = int(packet[2:-2])
        prob = int(packet[:2])
    else:
        data = int(packet[1:-2])
        prob = int(packet[1])

    # Corrupted packet. Stay in same state
    # Send ACK matching with opposite number
    if corrupted < prob / 100 or seq != ack:
        print('The receiver is moving back to state WAIT FOR', ack, 'FROM BELOW')
        if corrupted < prob:
            print('A corrupted packet has just been received')
        else:	
            ack ^= 1
        packet = str(prob) + str(data) + str(seq) + str(ack)

    # Move to next state
    else:
        print('Packet received contains: data =', data, 'seq =', seq, 'isack = ', bool(ack))
        print('The receiver is moving to state WAIT FOR', ack, 'FROM BELOW')
        if packet == prevPacket:  # Duplicate detection
            print('A duplicate packet with sequence number', seq, 'has just been received')
        else:
            print('A packet with sequence number', seq, 'has just been received')
        ack = seq
        packet = str(prob) + str(data) + str(seq)*2

    print(f'An ACK{ack} is about to be sent')
    print('Packet to send contains: data =', data, 'seq =', seq, 'isack =', bool(ack))
    prevPacket = packet
    connectionID.send(packet.encode())

    connectionID.close()

serverSocket.close()