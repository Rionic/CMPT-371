from socket import *
import random
import time
serverName = 'localhost'
serverPort = 50007
clientSocket = socket(AF_INET, SOCK_STREAM)
packet = None
clientSocket.connect( (serverName, serverPort) )
seq = 0
ack = 0
delay = 0
sameState = False
print ("connected to: " + str(serverName) + str(serverPort) )

while True:

	# Build new packet. Enter new state. 
	if not sameState:
		seed1 = input('[Client] Input a number for the seed for the instance of the random number generator used for timing arrival of data from the application ')
		seed2 = input('[Client] Input a number for the seed for the instance of the random number generator used for determining if ACKs have been corrupted ')
		random.seed(seed2)
		corrupted = random.randint(0,100000) / 100000
		seed3 = input('[Client] Input a number for the seed for The seed for the instance of the random number generator for generating the data in the packet ')
		random.seed(seed3)
		data = round(random.uniform(25, 100))	
		numPackets = int(input('[Client] Input a number for the number of packets to send '))
		if numPackets <= 0:
			continue
		prob = input('[Client] Input a number between 0 and 99 as the probability ')
		rttt = input('[Client] Input a number for the round trip travel time ')
		print('A packet with sequence number', seq, 'is about to be sent')
		print('The sender is moving to state WAIT FOR CALL', seq, 'FROM ABOVE')

	# Move back to previous state.
	else:
		print('A packet with sequence number', seq, 'is about to be resent')
		print('The sender is moving back to state WAIT FOR CALL', seq, 'FROM ABOVE')
	time.sleep(delay)
	print('Packet to send contains: data =', data, 'seq =', seq, 'isack =', ack)

	# Start timer
	print(f'Starting timeout timer for ACK{ack}')
	start = time.time()
	
	# Send & receive packet
	packet = str(prob) + str(data) + str(seq) + str(ack)
	print('transmitting packet', packet)
	time.sleep(delay)
	clientSocket.send(packet.encode())
	print('The sender is moving to state WAIT FOR ACK', seq)
	newPacket = clientSocket.recv(1024).decode()
	
	# Generate delay
	random.seed(seed1)
	delay = random.randint(0,60) / 10

	ack = int(newPacket[-1])
	seq = int(newPacket[-2])
	if len(packet) == 6:
		data = int(newPacket[2:-2])
		prob = int(newPacket[:2])
	else:
		data = int(newPacket[1:-2])
		prob = int(newPacket[1])

	print(f'An ACK{ack} packet has just been received')
	print('Packet received contains: data =', data, 'seq =', seq, 'isack =', bool(ack))

	# Stop timer
	print(f'Stopping timeout timer for ACK{ack}')
	stop = time.time()

	# Corrupt / different ACKs / timer expiry. Stay in same state
	if corrupted < prob / 100 or (stop - start) > int(rttt) or seq != ack:
		print('The sender is moving back to state WAIT FOR ACK', seq)
		if (stop - start) > int(rttt):
			print(f'ACK{ack} timeout timer expired')
		if corrupted < prob / 100:
			print('A Corrupted ACK packet has just been received')
		else:
			seq ^= 1
		sameState = True

	# Check if we need to send more packets
	if numPackets > 1:
		numPackets = numPackets - 1
		sameState = True

	# Data is okay. Move to next state
	else:	
		sameState = False
		seq ^= 1

clientSocket.close()