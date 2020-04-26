#UTA CN PROJECT 3
# Spardha Gupta - 1001642027
# Ankit Khanna - 1001

import helper
import random
import datetime
import time
from socketserver import ThreadingMixIn, TCPServer, BaseRequestHandler
import threading
import sys
import time
import socket
import pickle

# All ports should be under this IP.
localhost = helper.localHost

# Chan is listening to her (id +1000) portnumber.
listeningport = helper.namesAndPorts.get('Chan')

# Chan is sending messages to this port
talkingport = helper.namesAndPorts.get('E')

# Communication path storage
chantojan_file = './Supplemental Text Files/Chan/Chan-_Jan.txt'
chantoann_file = './Supplemental Text Files/Chan/Chan-_Ann.txt'

# Log file storage
chanjan_logfile = './Supplemental Text Files/Chan/ChanJanLog.txt'
chanann_logfile= './Supplemental Text Files/Chan/ChanAnnLog.txt'

# Clearing log files
helper.WriteToLogFile(chanjan_logfile, 'w', '')
helper.WriteToLogFile(chanann_logfile, 'w', '')

# Reading communication files
chantojan_comm = helper.ReadFile(chantojan_file)
chantoann_comm = helper.ReadFile(chantoann_file)

exitEvent = threading.Event()

#multithreaded server initiation
class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    """Handle requests in a separate thread."""

#request handler class
class TCPRequestHandler(BaseRequestHandler):
    def handle(self):

# socket connecting to client here
        packetgoingin = self.request.recv(4096)
        packetgoingindecoded = pickle.loads(packetgoingin)

        messagereceivedfrom = helper.GetKeyFromValue(packetgoingindecoded.get('Source ID'))

        if packetgoingindecoded.get('Ter Bit') == 1:
            print('Ann has ordered the termination of the connection.\n')
            exitEvent.set()

        # To check if someone else is trying to corrupt the connection.
        elif packetgoingindecoded.get('Syn Bit') == 1 and packetgoingindecoded.get('Acknowledgement Number') == -1:

            # ack +1 and creating own sequence number.
            #Three way handshake
            sourceid = listeningport
            destinationid = packetgoingindecoded.get(
                'Source ID')
            sequenceno = random.randint(10000, 99999)  # First time talking to client, create new sequence number
            acknumber = packetgoingindecoded.get(
                'Sequence Number') + 1  # Client wanted to connect, hence no data in the original packet, ack # will be one more than client seq #
            packetData = ''
            urgentPointer = 0
            synBit = 1  # Syn bit has to be one for the second step of threeway handshake
            finBit = 0  # Not trying to finish connection, hence 0
            rstBit = 0  # Not trying to reset connection, hence 0
            terBit = 0  # Not trying to terminate connection, hence 0

            # Create packet with above data
            responsePacket = helper.CreateTCPPacket(sourceid, destinationid, acknumber, sequenceno,
                                                    packetData, urgentPointer,
                                                    synBit, finBit, rstBit, terBit)

            # Send packet
            helper.SerializeAndSendPacket(responsePacket, talkingport)

            # Log what happened
            timeStamp = time.time()
            data = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S') + '\n'

            if messagereceivedfrom == 'Jan':
                data = data + 'Jan as a client attempted to connect. Sent packet with Syn Bit as 1, which is the second step of the threeway handshake.\n\n'
                helper.WriteToLogFile(chanjan_logfile, 'a', data)
            elif messagereceivedfrom == 'Ann':
                data = data + 'Ann as a client attempted to connect. Sent packet with Syn Bit as 1, which is the second step of the threeway handshake.\n\n'
                helper.WriteToLogFile(chanann_logfile, 'a', data)

                # Connection setup response.
        elif packetgoingindecoded.get('Syn Bit') == 1:

            # Start sending data here and raise the flag to wait for acknowledgement
            sourceid = listeningport  # The port listening to
            destinationid = packetgoingindecoded.get(
                'Source ID')  # The destination of the packet about to be sent is where the original packet came from
            sequenceno = packetgoingindecoded.get(
                'Acknowledgement Number')  # The  next byte you should be sending is the byte that the other party is expecting
            acknumber = packetgoingindecoded.get(
                'Sequence Number') + 1  # One more than the sequence number
            urgentPointer = 0
            synBit = 0  # Threeway handshake third step, no need of this bit
            finBit = 0  # Not trying to finish connection, hence 0
            rstBit = 0  # Not trying to reset connection, hence 0
            terBit = 0  # Not trying to terminate connection, hence 0

            # Populate data field depending on who the connection is being established with
            if messagereceivedfrom == 'Jan':
                try:
                    packetData = chantojan_comm.pop(0)  # Get the first element from list and delete it from there
                except IndexError:
                    print('Chan-_Jan.txt is empty.\n\n')

            elif messagereceivedfrom == 'Ann':
                try:
                    packetData = chantoann_comm.pop(0)  # Get the first element from list and delete it from there
                except IndexError:
                    print('Chan-_Ann.txt is empty.\n\n')

            # Create packet with above data
            responsePacket = helper.CreateTCPPacket(sourceid, destinationid, acknumber, sequenceno,
                                                    packetData, urgentPointer,
                                                    synBit, finBit, rstBit, terBit)

            # Send packet
            helper.SerializeAndSendPacket(responsePacket, talkingport)

            # Log what happened
            timeStamp = time.time()
            data = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S') + '\n'

            if messagereceivedfrom == 'Jan':
                data = data + 'Connection with Jan as the server is successful. This is the third step of the threeway handshake. First, which is below line was sent.\n'
                data = data + packetData + '\n\n'
                helper.WriteToLogFile(chanjan_logfile, 'a', data)
            elif messagereceivedfrom == 'Ann':
                data = data + 'Connection with Ann as the server is successful. This is the third step of the threeway handshake. First, which is below line was sent.\n'
                data = data + packetData + '\n\n'
                helper.WriteToLogFile(chanann_logfile, 'a', data)


        # Any other case, is receiving data
        else:
            # Send acknowledgement
            sourceid = listeningport  # The port listening to
            destinationid = packetgoingindecoded.get(
                'Source ID')  # The destination of the packet about to be sent is where the original packet came from
            sequenceno = packetgoingindecoded.get(
                'Acknowledgement Number')  # The  next byte you should be sending is the byte that the other party is expecting

            # Next byte of data that you want
            acknumber = packetgoingindecoded.get('Sequence Number') + len(
                packetgoingindecoded.get('Data'))

            urgentPointer = 0  # Not urgent as this is connection setup
            synBit = 0  # Syn bit has to be one for the second step of threeway handshake
            finBit = 0  # Not trying to finish connection, hence 0
            rstBit = 0  # Not trying to reset connection, hence 0
            terBit = 0  # Not trying to terminate connection, hence 0

            # Populate data field depending on who the connection is being established with
            if messagereceivedfrom == 'Jan':
                try:
                    packetData = chantojan_comm.pop(0)  # Get the first element from list and delete it from there
                except IndexError:
                    # Kick of connection tear down function here
                    pass

            elif messagereceivedfrom == 'Ann':
                try:
                    packetData = chantoann_comm.pop(0)  # Get the first element from list and delete it from there
                except IndexError:
                    # Kick of connection tear down function here
                    pass

            # Create packet with above data
            responsePacket = helper.CreateTCPPacket(sourceid, destinationid, acknumber, sequenceno,
                                                    packetData, urgentPointer,
                                                    synBit, finBit, rstBit, terBit)

            # Send packet
            helper.SerializeAndSendPacket(responsePacket, talkingport)

            # Log what happened
            timeStamp = time.time()
            data = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S') + '\n'
            data = data + 'Received following line.\n'
            data = data + packetgoingindecoded.get('Data')
            data = data + 'Acknowledgement sent along with below line.\n'
            data = data + packetData + '\n\n'

            if messagereceivedfrom == 'Jan':
                helper.WriteToLogFile(chanjan_logfile, 'a', data)
            elif messagereceivedfrom == 'Ann':
                helper.WriteToLogFile(chanann_logfile, 'a', data)

        return


# ------------------------------------------
# Function for the router threads to execute
# ------------------------------------------
def AgentServer():
    try:
        server = ThreadedTCPServer((localhost, listeningport), TCPRequestHandler)

        server.timeout = 0.01  # Make sure not to wait too long when serving requests
        server.daemon_threads = True  # So that handle_request thread exits when current thread exits

        # Poll so that you see the signal to exit as opposed to calling server_forever
        while not exitEvent.isSet():
            server.handle_request()

        server.server_close()
    except:
        print('Problem creating server for agent Chan.')

    sys.exit()


if __name__ == '__main__':
    try:
        # Make sure the evebt is clear initially
        exitEvent.clear()

        # Create a seperate for Chan's server portion
        chanServer = threading.Thread(target=AgentServer, args=())

        # Start the Chan's server
        chanServer.start()

        # Sleep to ensure that all agents are online
        time.sleep(10)
    except:
        print("Couldn't create thread for Chan's router.")

    try:
        # Start connection setup with Jan
        sourceid = listeningport  # The port listening to
        destinationid = helper.namesAndPorts.get(
            'Jan')  # Trying to setup connection with Jan, so send the packet to Jan
        sequenceno = random.randint(10000, 99999)  # First time talking to Jan, create new sequence number
        acknumber = -1  # Haven't recevied anything from Jan, hence -1
        packetData = ''  # Acknowledgment packets contain no data
        urgentPointer = 0  # Not urgent as this is connection setup
        synBit = 1  # Syn bit has to be one since this is connection setup
        finBit = 0  # Not trying to finish connection, hence 0
        rstBit = 0  # Not trying to reset connection, hence 0
        terBit = 0  # Not trying to terminate connection, hence 0

        # Create packet with above data
        responsePacket = helper.CreateTCPPacket(sourceid, destinationid, acknumber, sequenceno,
                                                packetData, urgentPointer,
                                                synBit, finBit, rstBit, terBit)

        # Send packet
        helper.SerializeAndSendPacket(responsePacket, talkingport)

        # Log it
        timeStamp = time.time()
        data = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S') + '\n'
        data = data + "Connection setup with Jan started. This is the first step of the threeway handshake.\n\n"
        helper.WriteToLogFile(chanjan_logfile, 'a', data)

        # Run till connection teardown or termination
        while not exitEvent.isSet():
            pass

        # Wait for Chan's server to finish
        chanServer.join()

        sys.exit()
    except KeyboardInterrupt:
        print('Keyboard interrupt\n')
        exitEvent.set()  # Upon catching keyboard interrupt, let the threads know they have to exit

        # Wait for Jan's server to finish
        chanServer.join()

        sys.exit()
