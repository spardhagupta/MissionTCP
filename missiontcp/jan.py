#UTA CN PROJECT 3
# Spardha Gupta - 1001642027
# Ankit Khanna - 1001553616

import datetime
import helper
import pickle
import random
import socket
import sys
import time
from socketserver import ThreadingMixIn, TCPServer, BaseRequestHandler
import threading
import time


MissionTimer = -1

# All ports should be under this IP.
localhost = helper.localHost

# Jan is listening to her (id+1000) portnumber.
listeningport = helper.namesAndPorts.get('Jan')

# Jan is sending messages to this port.
talkingport = helper.namesAndPorts.get('F')

# Communication path storage
jantochan_file = './Supplemental Text Files/Jan/Jan-Chan.txt'
jantoann_file = './Supplemental Text Files/Jan/Jan-Ann.txt'

# Log file storage
janchan_logfile = './Supplemental Text Files/Jan/Jan-ChanLog.txt'
janann_logfile = './Supplemental Text Files/Jan/Jan-AnnLog.txt'
janairforce_logfile = './Supplemental Text Files/Jan/Jan-AirForceLog.txt'

# Clearing log files
helper.WriteToLogFile(janchan_logfile, 'w', '')
helper.WriteToLogFile(janann_logfile, 'w', '')
helper.WriteToLogFile(janairforce_logfile, 'w', '')

# reading communication files.
jantochan_comm = helper.ReadFile(jantochan_file)
jantoann_comm = helper.ReadFile(jantoann_file)

threadingEvent = threading.Event()

# multithreaded server initiation
class ServerThread(ThreadingMixIn, TCPServer):
    """Handle requests in a separate thread."""

#request handler class
class RequestHandler(BaseRequestHandler):
    def handle(self):

        # socket connecting to client here.
        packetgoingin = self.request.recv(4096)
        packetgoingindecoded = pickle.loads(packetgoingin)

        messagereceivedfrom = helper.GetKeyFromValue(packetgoingindecoded.get('Source ID'))
        global MissionTimer

        if packetgoingindecoded.get('Fin Bit') == 1 and MissionTimer == 8:

            timeStamp = time.time()
            data = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S') + '\n'
            data = data + 'Acknowledgement recieved, Communication with Ann is Finished.This is the third step for the communication teardown.\n\n'
            helper.WriteToLogFile(janann_logfile, 'a', data)
            # exit Jan's event
            print('Fin Bit reveived....\n')
            print('Jan Ending Connection...')
            threadingEvent.set()

        elif MissionTimer == 6:

            # increment the next position
            MissionTimer = 8
#Three way handshake
            sourceid = listeningport  # The port listening to
            destinationid = helper.namesAndPorts.get(
                'Ann')  # The destination of the packet about to be sent is where the original packet came from
            sequenceno = packetgoingindecoded.get(
                'Acknowledgement Number')  # The  next byte you should be sending is the byte that the other party is expecting
            # Next byte of data that you want
            acknumber = packetgoingindecoded.get('Sequence Number') + len(
                packetgoingindecoded.get('Data'))
            packetData = 'Request for a finish mission?\n'  # Second step of three way handshake, hence no data
            urg = 0  
            syn = 0
            fin = 1
            rst = 0
            ter = 0

            # Create packet with above data
            responsePacket = helper.CreateTCPPacket(sourceid, destinationid, acknumber, sequenceno,
                                                    packetData, urg, syn, fin, rst, ter)

            # Send packet
            helper.SerializeAndSendPacket(responsePacket, talkingport)

            # Log what happened
            timeStamp = time.time()
            data = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S') + '\n'
            data = data + 'Received following line.\n'
            data = data + packetgoingindecoded.get('Data')
            data = data + 'Acknowledgement sent along with below line. This is the first step of the connection teardown.\n'
            data = data + packetData + '\n\n'
            helper.WriteToLogFile(janann_logfile, 'a', data)
            print('JanToAnn: sending Fin Bit to ann.\n')



        elif MissionTimer == 4 and \
                packetgoingindecoded.get('Data') == 'Success!':

            # increment the next position
            MissionTimer = 6
            sourceid = listeningport  # The port listening to
            destinationid = helper.namesAndPorts.get(
                'Ann')  # The destination of the packet about to be sent is where the original packet came from
            sequenceno = packetgoingindecoded.get(
                'Acknowledgement Number')  # The  next byte you should be sending is the byte that the other party is expecting
            # Next byte of data that you want
            acknumber = packetgoingindecoded.get('Sequence Number') + len(
                packetgoingindecoded.get('Data'))
            # confirm success by giving the code
            packetData = 'The authorization code:\n' + 'Congratulations we have fried dry green leaves\n'
            urg = 1  # Message is urgent
            syn = 0  # Syn bit is zero
            fin = 0  # Not trying to finish connection, hence 0
            rst = 0  # Not trying to reset connection, hence 0
            ter = 0  # Not trying to terminate connection, hence 0

            # Create packet with above data
            responsePacket = helper.CreateTCPPacket(sourceid, destinationid, acknumber, sequenceno,
                                                    packetData, urg, syn, fin, rst, ter)

            # Send packet
            helper.SerializeAndSendPacket(responsePacket, talkingport)

            # Log what happened
            timeStamp = time.time()
            data = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S') + '\n'
            data = data + 'Received following line.\n'
            data = data + packetgoingindecoded.get('Data')
            data = data + 'Acknowledgement sent along with below line.\n'
            data = data + packetData + '\n\n'
            helper.WriteToLogFile(janann_logfile, 'a', data)
            print('Recieved Success packet from Head Quarters.\n')
            print(
                'JanToAnn: Urg Pointer On: The authorization code:\n' + 'Congratulations we have fried dry green leaves\n')


        elif MissionTimer == 2 and packetgoingindecoded.get('Data') == 'PEPPER THE PEPPER\n':

            # increment the next position
            # need to see how to execute to router H

            sourceid = listeningport  # The port listening to
            destinationid = helper.namesAndPorts.get(
                'H')  # The destination of the packet about to be sent is where the original packet came from
            sequenceno = sequenceno = random.randint(10000,
                                                             99999)  # The  next byte you should be sending is the byte that the other party is expecting
            # Next byte of data that you want
            acknumber = -1
            # confirm success by giving the code
            packetData = 'Location of target: (32° 43 22.77 N,97° 9 7.53 W)\n' + 'The authorization code for the Airforce Headquarters:\n' + 'PEPPER THE PEPPER\n'
            urg = 1  # Message is urgent
            syn = 0  # Syn bit is zero
            fin = 0  # Not trying to finish connection, hence 0
            rst = 0  # Not trying to reset connection, hence 0
            ter = 0  # Not trying to terminate connection, hence 0

            # Create packet with above data
            responsePacket = helper.CreateTCPPacket(sourceid, destinationid, acknumber, sequenceno,
                                                    packetData, urg, syn, fin, rst, ter)

            # Send packet
            helper.SerializeAndSendPacket(responsePacket, helper.namesAndPorts.get('H'))

            # Log what happened

            timeStamp = time.time()
            data = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S') + '\n'
            data = data + 'Received following line.\n'
            data = data + packetgoingindecoded.get('Data')
            data = data + 'Acknowledgement sent along with below line.\n'
            data = data + packetData + '\n\n'
            helper.WriteToLogFile(janairforce_logfile, 'a', data)
            MissionTimer = 4
            print('Recieved Authorization code from Ann.\n')
            print(
                'JanToAirForce: Location of target: (32° 43 22.77 N,97° 9 7.53 W)\n' + 'The authorization code for the Airforce Headquarters:\n' + 'PEPPER THE PEPPER\n')



        elif packetgoingindecoded.get('Urgent Pointer') == 1:
            # increment the next position
            MissionTimer = 2
            sourceid = listeningport  # The port listening to
            destinationid = helper.namesAndPorts.get(
                'Ann')  # The destination of the packet about to be sent is where the original packet came from
            sequenceno = packetgoingindecoded.get(
                'Acknowledgement Number')  # The  next byte you should be sending is the byte that the other party is expecting
            # Next byte of data that you want
            acknumber = packetgoingindecoded.get('Sequence Number') + len(
                packetgoingindecoded.get('Data'))
            # confirm success by giving the code
            packetData = 'Location of target: (32° 43 22.77 N,97° 9 7.53 W)\n' + 'Request for a mission execution?\n'
            urg = 1  # Message is urgent
            syn = 0  # Syn bit is zero
            fin = 0  # Not trying to finish connection, hence 0
            rst = 0  # Not trying to reset connection, hence 0
            ter = 0  # Not trying to terminate connection, hence 0

            # Create packet with above data
            responsePacket = helper.CreateTCPPacket(sourceid, destinationid, acknumber, sequenceno,
                                                    packetData, urg, syn, fin, rst, ter)

            # Send packet
            helper.SerializeAndSendPacket(responsePacket, talkingport)

            # Log what happened
            timeStamp = time.time()
            data = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S') + '\n'
            data = data + 'Received following line.\n'
            data = data + packetgoingindecoded.get('Data')
            data = data + 'Acknowledgement sent along with below line.\n'
            data = data + packetData + '\n\n'
            helper.WriteToLogFile(janann_logfile, 'a', data)
            print('Urg pointer resived: ' + packetgoingindecoded.get('Data'))
            print(
                'JanToAnn: Urg Pointer On: Location of target: (32° 43 22.77 N,97° 9 7.53 W)\n' + 'Request for a mission execution?\n')


        elif MissionTimer < 0:
            # When someone else is trying to setup connection with us
            if packetgoingindecoded.get('Syn Bit') == 1 and packetgoingindecoded.get('Acknowledgement Number') == -1:

                # Send TCP packet with syn bit still one and acknowledgement number as 1 + sequence number. Also, create your own sequence number
                sourceid = listeningport  # The port listening to
                destinationid = packetgoingindecoded.get(
                    'Source ID')  # The destination of the packet about to be sent is where the original packet came from
                sequenceno = random.randint(10000,
                                                99999)  # First time talking to client, create new sequence number
                acknumber = packetgoingindecoded.get(
                    'Sequence Number') + 1  # Client wanted to connect, hence no data in the original packet, ack # will be one more than client seq #
                packetData = ''  # Second step of three way handshake, hence no data
                urg = 0  # Not urgent as this is connection setup
                syn = 1  # Syn bit has to be one for the second step of threeway handshake
                fin = 0  # Not trying to finish connection, hence 0
                rst = 0  # Not trying to reset connection, hence 0
                ter = 0  # Not trying to terminate connection, hence 0

                # Create packet with above data
                responsePacket = helper.CreateTCPPacket(sourceid, destinationid, acknumber, sequenceno,
                                                        packetData, urg,
                                                        syn, fin, rst, ter)

                # Send packet
                helper.SerializeAndSendPacket(responsePacket, talkingport)

                # Log what happened
                timeStamp = time.time()
                data = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S') + '\n'

                if messagereceivedfrom == 'Chan':
                    data = data + 'Chan as a client attempted to connect. Sent packet with Syn Bit as 1, which is the second step of the threeway handshake.\n\n'
                    helper.WriteToLogFile(janchan_logfile, 'a', data)
                elif messagereceivedfrom == 'Ann':
                    data = data + 'Ann as a client attempted to connect. Sent packet with Syn Bit as 1, which is the second step of the threeway handshake.\n\n'
                    helper.WriteToLogFile(janann_logfile, 'a', data)

                    # Your attempt to setup connection with someone else has been responded to
            elif packetgoingindecoded.get('Syn Bit') == 1:

                # Start sending data here and raise the flag to wait for acknowledgement
                sourceid = listeningport  # The port listening to
                destinationid = packetgoingindecoded.get(
                    'Source ID')  # The destination of the packet about to be sent is where the original packet came from
                sequenceno = packetgoingindecoded.get(
                    'Acknowledgement Number')  # The  next byte you should be sending is the byte that the other party is expecting
                acknumber = packetgoingindecoded.get(
                    'Sequence Number') + 1  # Just one more than the sequence number
                urg = 0  # Not urgent as this is connection setup
                syn = 0  # Threeway handshake third step, no need of this bit
                fin = 0  # Not trying to finish connection, hence 0
                rst = 0  # Not trying to reset connection, hence 0
                ter = 0  # Not trying to terminate connection, hence 0

                # Populate data field depending on who the connection is being established with
                if messagereceivedfrom == 'Chan':
                    try:
                        packetData = jantochan_comm.pop(0)  # Get the first element from list and delete it from there
                    except IndexError:
                        print('Jan-_Chan.txt is empty.\n\n')

                elif messagereceivedfrom == 'Ann':
                    try:
                        packetData = jantoann_comm.pop(0)  # Get the first element from list and delete it from there
                    except IndexError:
                        print('Jan-_Ann.txt is empty.\n\n')

                # Create packet with above data
                responsePacket = helper.CreateTCPPacket(sourceid, destinationid, acknumber, sequenceno,
                                                        packetData, urg,
                                                        syn, fin, rst, ter)

                # Send packet
                helper.SerializeAndSendPacket(responsePacket, talkingport)

                # Log what happened
                timeStamp = time.time()
                data = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S') + '\n'

                if messagereceivedfrom == 'Chan':
                    data = data + 'Connection with Chan as the server is successful. This is the third step of the threeway handshake. First, which is below line was sent.\n'
                    data = data + packetData + '\n\n'
                    helper.WriteToLogFile(janchan_logfile, 'a', data)
                elif messagereceivedfrom == 'Ann':
                    data = data + 'Connection with Ann as the server is successful. This is the third step of the threeway handshake. First, which is below line was sent.\n'
                    data = data + packetData + '\n\n'
                    helper.WriteToLogFile(janann_logfile, 'a', data)


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

                urg = 0  # Not urgent as this is connection setup
                syn = 0  # Syn bit has to be one for the second step of threeway handshake
                fin = 0  # Not trying to finish connection, hence 0
                rst = 0  # Not trying to reset connection, hence 0
                ter = 0  # Not trying to terminate connection, hence 0

                # Populate data field depending on who the connection is being established with
                if messagereceivedfrom == 'Chan':
                    try:
                        packetData = jantochan_comm.pop(0)  # Get the first element from list and delete it from there
                    except IndexError:
                        # Kick of connection tear down function here
                        pass

                elif messagereceivedfrom == 'Ann':
                    try:
                        packetData = jantoann_comm.pop(0)  # Get the first element from list and delete it from there
                    except IndexError:
                        # Kick of connection tear down function here
                        pass

                # Create packet with above data
                responsePacket = helper.CreateTCPPacket(sourceid, destinationid, acknumber, sequenceno,
                                                        packetData, urg,
                                                        syn, fin, rst, ter)

                # Send packet
                helper.SerializeAndSendPacket(responsePacket, talkingport)

                # Log what happened
                timeStamp = time.time()
                data = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S') + '\n'
                data = data + 'Received following line.\n'
                data = data + packetgoingindecoded.get('Data')
                data = data + 'Acknowledgement sent along with below line.\n'
                data = data + packetData + '\n\n'

                if messagereceivedfrom == 'Chan':
                    helper.WriteToLogFile(janchan_logfile, 'a', data)
                elif messagereceivedfrom == 'Ann':
                    helper.WriteToLogFile(janann_logfile, 'a', data)

        return


def server_agent():
    try:
        server = ServerThread((localhost, listeningport), RequestHandler)

        server.timeout = 0.01  # Make sure not to wait too long when serving requests
        server.daemon_threads = True  # So that handle_request thread exits when current thread exits

        # Poll so that you see the signal to exit as opposed to calling server_forever
        while not threadingEvent.isSet():
            server.handle_request()

        server.server_close()
    except:
        print('Problem creating server for agent Jan.')

    sys.exit()


if __name__ == '__main__':
    try:
        # Make sure the evebt is clear initially
        threadingEvent.clear()

        # Create a seperate for Jan's server portion
        janServer = threading.Thread(target=server_agent, args=())

        # Start the Jan's server
        janServer.start()

        # Sleep to ensure that all agents are online
        time.sleep(10)
    except:
        print("Couldn't create thread for Jan's router.")

    try:

        # Start connection setup with Ann
        sourceid = listeningport  # The port listening to
        destinationid = helper.namesAndPorts.get(
            'Ann')  # Trying to setup connection with Jan, so send the packet to Jan
        sequenceno = random.randint(10000, 99999)  # First time talking to Ann, create new sequence number
        acknumber = -1  # Haven't recevied anything from Jan, hence -1
        packetData = ''  # Acknowledgment packets contain no data
        urg = 0  # Not urgent as this is connection setup
        syn = 1  # Syn bit has to be one since this is connection setup
        fin = 0  # Not trying to finish connection, hence 0
        rst = 0  # Not trying to reset connection, hence 0
        ter = 0  # Not trying to terminate connection, hence 0

        # Create packet with above data
        responsePacket = helper.CreateTCPPacket(sourceid, destinationid, acknumber, sequenceno,
                                                packetData, urg,
                                                syn, fin, rst, ter)

        # Send packet
        helper.SerializeAndSendPacket(responsePacket, talkingport)

        # Log it
        timeStamp = time.time()
        data = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S') + '\n'
        data = data + "Connection setup with Ann started. This is the first step of the threeway handshake.\n\n"
        helper.WriteToLogFile(janann_logfile, 'a', data)

        # Run till connection teardown or termination
        while not threadingEvent.isSet():
            pass

        # Wait for Jan's server to finish
        janServer.join()

        sys.exit()
    except KeyboardInterrupt:
        threadingEvent.set()  # Upon catching keyboard interrupt, let the threads know they have to exit

        # Wait for Jan's server to finish
        janServer.join()

        sys.exit()
