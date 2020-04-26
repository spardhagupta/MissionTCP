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

# Track number of messages sent by Chan. Chan cannot send more than 5 messages.
chan_count = 0

MissionTimer = -1

# All ports should be under this IP.
localhost = helper.localHost

# Ann is listening to her (id +1000)portnumber.
listeningport = helper.namesAndPorts.get('Ann')

# Ann is sending messages to this port
talkingport = helper.namesAndPorts.get('A')

# Communication path storage
anntochan_file = './Supplemental Text Files/Ann/Ann-Chan.txt'
anntojan_file = './Supplemental Text Files/Ann/Ann-Jan.txt'

# Log file storage
annchan_logfile = './Supplemental Text Files/Ann/Ann-ChanLog.txt'
annjan_logfile = './Supplemental Text Files/Ann/Ann-JanLog.txt'

# Clearing log files
helper.WriteToLogFile(annchan_logfile, 'w', '')
helper.WriteToLogFile(annjan_logfile, 'w', '')

# reading communication files
anntojan_comm = helper.ReadFile(anntojan_file)
anntochan_comm = helper.ReadFile(anntochan_file)

threadingEvent = threading.Event()

# multithreaded server initiation
class ServerThread(ThreadingMixIn, TCPServer):
    """Handle multiple requests separately."""

# request handler class
class RequestHandler(BaseRequestHandler):
    def handle(self):

        # socket connecting to client here
        packetgoingin = self.request.recv(4096)
        packetgoingindecoded = pickle.loads(packetgoingin)

        messagereceivedfrom = helper.GetKeyFromValue(packetgoingindecoded.get('Source ID'))

        global MissionTimer

        if packetgoingindecoded.get('Fin Bit') == 1 and MissionTimer == 7:
#Three way handshake
            sourceid = listeningport
            destinationid = helper.namesAndPorts.get(
                'Jan')
            sequenceno = packetgoingindecoded.get(
                'Acknowledgement Number')  # The  next byte you should be sending is the byte that the other party is expecting
            # Next byte of data that you want
            acknumber = packetgoingindecoded.get(
                'Sequence Number') + 1
            packetData = ''
            urgentPointer = 0
            synBit = 0  # Syn bit is zero
            finBit = 1  # Finish connection
            rstBit = 0  # Not trying to reset connection, hence 0
            terBit = 0  # Not trying to terminate connection, hence 0

            # Create packet with above data
            responsePacket = helper.CreateTCPPacket(sourceid, destinationid, acknumber, sequenceno,
                                                    packetData, urgentPointer, synBit, finBit, rstBit, terBit)

            # Send packet
            helper.SerializeAndSendPacket(responsePacket, talkingport)

            # Log what happened
            timeStamp = time.time()
            data = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S') + '\n'
            data = data + 'Mission Complete, Communication with Jan is Finished. This is the second step of the connection teardown.\n\n'
            helper.WriteToLogFile(annjan_logfile, 'a', data)
            print('Fin Bit reveived.... sending Fin Bit to Jan....\n')
            print('Ann Ending Connection...')
            # exit Ann's event
            threadingEvent.set()


        elif packetgoingindecoded.get('Urgent Pointer') == 1 and MissionTimer == 5:

            MissionTimer = 7
            sourceid = listeningport
            destinationid = helper.namesAndPorts.get(
                'Jan')
            sequenceno = packetgoingindecoded.get(
                'Acknowledgement Number')
            # Next byte of data
            acknumber = packetgoingindecoded.get('Sequence Number') + len(
                packetgoingindecoded.get('Data'))
            packetData = 'Meeting Location: 32.76 N, -97.07 W\n'  # Sending the coordinates.
            urgentPointer = 0  # Not urgent as this is connection setup
            synBit = 0  # Syn bit is zero
            finBit = 0  # Not trying to finish connection, hence 0
            rstBit = 0  # Not trying to reset connection, hence 0
            terBit = 0  # Not trying to terminate connection, hence 0

            # Create packet with above data
            responsePacket = helper.CreateTCPPacket(sourceid, destinationid, acknumber, sequenceno,
                                                    packetData, urgentPointer, synBit, finBit, rstBit, terBit)

            # Send packet
            helper.SerializeAndSendPacket(responsePacket, talkingport)

            # Log what happened
            timeStamp = time.time()
            data = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S') + '\n'
            data = data + 'Received following line.\n'
            data = data + packetgoingindecoded.get('Data')
            data = data + 'Acknowledgement sent along with below line.\n'
            data = data + packetData + '\n\n'
            helper.WriteToLogFile(annjan_logfile, 'a', data)
            print('Urg pointer resived: ' + packetgoingindecoded.get('Data'))
            print('\nAnnToJan: Meeting Location: 32.76 N, -97.07 W\n')

        elif packetgoingindecoded.get('Urgent Pointer') == 1 and MissionTimer == 1:

            # increment the next position
            MissionTimer = 5

            sourceid = listeningport  # The port listening to
            destinationid = helper.namesAndPorts.get(
                'Jan')  # The destination of the packet about to be sent is where the original packet came from
            sequenceno = packetgoingindecoded.get(
                'Acknowledgement Number')
            # Next byte of data that you want
            acknumber = packetgoingindecoded.get('Sequence Number') + len(
                packetgoingindecoded.get('Data'))
            # authorize to execute and give code
            packetData = 'PEPPER THE PEPPER\n'
            urgentPointer = 0  # Not urgent as this is connection setup
            synBit = 0  # Syn bit is zero
            finBit = 0  # Not trying to finish connection, hence 0
            rstBit = 0  # Not trying to reset connection, hence 0
            terBit = 0  # Not trying to terminate connection, hence 0

            # Create packet with above data
            responsePacket = helper.CreateTCPPacket(sourceid, destinationid, acknumber, sequenceno,
                                                    packetData, urgentPointer, synBit, finBit, rstBit, terBit)

            # Send packet
            helper.SerializeAndSendPacket(responsePacket, talkingport)

            # Log what happened
            timeStamp = time.time()
            data = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S') + '\n'
            data = data + 'Received following line.\n'
            data = data + packetgoingindecoded.get('Data')
            data = data + 'Acknowledgement sent along with below line.\n'
            data = data + packetData + '\n\n'
            helper.WriteToLogFile(annjan_logfile, 'a', data)
            print('Urg pointer resived: ' + packetgoingindecoded.get('Data'))
            print(
                '\nAnnToJan: Execute\n' + 'The authorization code for the Airforce Headquarters:\n' + 'PEPPER THE PEPPER\n')

        # When someone else is trying to setup connection with us
        elif MissionTimer < 0:
            if packetgoingindecoded.get('Syn Bit') == 1 and packetgoingindecoded.get('Acknowledgement Number') == -1:

                # Send TCP packet with syn bit still one and acknowledgement number as 1 + sequence number.
                # Also, create your own sequence number
                sourceid = listeningport  # The port listening to
                destinationid = packetgoingindecoded.get(
                    'Source ID')  # The destination of the packet about to be sent is where the original packet came from
                sequenceno = random.randint(10000,
                                                99999)  # First time talking to client, create new sequence number
                acknumber = packetgoingindecoded.get(
                    'Sequence Number') + 1  # Client wanted to connect, hence no data in the original packet, ack # will be one more than client seq #
                packetData = ''  # Second step of three way handshake, hence no data
                urgentPointer = 0  # Not urgent as this is connection setup
                synBit = 1  # Syn bit has to be one for the second step of threeway handshake
                finBit = 0  # Not trying to finish connection, hence 0
                rstBit = 0  # Not trying to reset connection, hence 0
                terBit = 0  # Not trying to terminate connection, hence 0

                # Create packet with above data
                responsePacket = helper.CreateTCPPacket(sourceid, destinationid, acknumber, sequenceno,
                                                        packetData, urgentPointer, synBit, finBit, rstBit, terBit)

                # Send packet
                helper.SerializeAndSendPacket(responsePacket, talkingport)

                # Log what happened
                timeStamp = time.time()
                data = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S') + '\n'

                if messagereceivedfrom == 'Jan':
                    data = data + 'Jan as a client attempted to connect. Sent packet with Syn Bit as 1, ' \
                                  'which is the second step of the threeway handshake.\n\n'
                    helper.WriteToLogFile(annjan_logfile, 'a', data)
                elif messagereceivedfrom == 'Chan':
                    data = data + 'Chan as a client attempted to connect. Sent packet with Syn Bit as 1, ' \
                                  'which is the second step of the threeway handshake.\n\n'
                    helper.WriteToLogFile(annchan_logfile, 'a', data)

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

                urgentPointer = 0  # Not urgent as this is connection setup
                synBit = 0  # Threeway handshake third step, no need of this bit
                finBit = 0  # Not trying to finish connection, hence 0
                rstBit = 0  # Not trying to reset connection, hence 0
                terBit = 0  # Not trying to terminate connection, hence 0

                # Populate data field depending on who the connection is being established with
                if messagereceivedfrom == 'Jan':
                    try:
                        packetData = anntojan_comm.pop(0)  # Get the first element from list and delete it from there
                    except IndexError:
                        print('Ann-_Jan.txt is empty.\n\n')

                elif messagereceivedfrom == 'Chan':
                    try:
                        packetData = anntochan_comm.pop(0)  # Get the first element from list and delete it from there
                    except IndexError:
                        print('Ann-_Chan.txt is empty.\n\n')

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
                    data = data + 'Connection with Jan as the server is successful. This is the third step of the threeway handshake. First line, which is below was sent.\n'
                    data = data + packetData + '\n\n'
                    helper.WriteToLogFile(annjan_logfile, 'a', data)
                elif messagereceivedfrom == 'Chan':
                    data = data + 'Connection with Chan as the server is successful. This is the third step of the threeway handshake. First line, which is below was sent.\n'
                    data = data + packetData + '\n\n'
                    helper.WriteToLogFile(annchan_logfile, 'a', data)

            # Any other case, is receiving data
            else:
                global chan_count
                # terminate communication with Chan and inform Jan about compromise
                if chan_count == 5:
                    chan_count = chan_count + 1
                    MissionTimer = 1
                    print("Terminating Connection With Agent Chan since Chan is compromised.\n")

                    # send jan a packet with urgbit 1 with Chan being compromised
                    sourceid = listeningport  # The port listening to
                    destinationid = helper.namesAndPorts.get(
                        'Jan')  # The destination of the packet about to be sent is where the original packet came from
                    sequenceno = random.randint(10000,
                                                    99999)  # First time talking to client, create new that the other party is expecting
                    # Next byte of data that you want
                    acknumber = packetgoingindecoded.get('Sequence Number') + 1
                    packetData = 'Communication with Chan has been Compromised'  # Termination packet contain no data
                    urgentPointer = 1  # Urgent pointer is 1 to tell Jan that Chan has been compromised
                    synBit = 0  # Syn bit has to be one for the second step of
                    finBit = 0  #
                    rstBit = 0  # Not trying to reset connection, hence 0
                    terBit = 0
                    responsePacket = helper.CreateTCPPacket(sourceid, destinationid, acknumber,
                                                            sequenceno, packetData, urgentPointer, synBit, finBit,
                                                            rstBit, terBit)
                    # Send packet
                    helper.SerializeAndSendPacket(responsePacket, talkingport)
                    # log in the termination
                    timeStamp = time.time()
                    data = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S') + '\n'
                    data = data + 'Communication with Chan has been Terminated.\n\n'
                    helper.WriteToLogFile(annjan_logfile, 'a', data)
                    print('AnnToJan: Urg Pointer On: Communication with Chan has been compromised.')

                    # send chan a packet with terbit 1
                    sourceid = listeningport  # The port listening to
                    destinationid = helper.namesAndPorts.get(
                        'Chan')  # The destination of the packet about to be sent is where the original packet came from
                    sequenceno = packetgoingindecoded.get(
                        'Acknowledgement Number')  # The  next byte you should be sending is the byte that the other party is expecting
                    # Next byte of data that you want
                    acknumber = packetgoingindecoded.get('Sequence Number') + len(
                        packetgoingindecoded.get('Data'))
                    packetData = ''  # Termination packet contain no data
                    urgentPointer = 0  # Not urgent as this is connection setup
                    synBit = 0  # Syn bit has to be one for the second step of
                    finBit = 0  #
                    rstBit = 1  # reset communication flag on to terminate communication
                    terBit = 1  # make terbit 1 to start termination with chan
                    responsePacket = helper.CreateTCPPacket(sourceid, destinationid, acknumber,
                                                            sequenceno, packetData, urgentPointer, synBit, finBit,
                                                            rstBit, terBit)
                    # Send packet
                    helper.SerializeAndSendPacket(responsePacket, talkingport)
                    # log in the termination
                    timeStamp = time.time()
                    data = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S') + '\n'
                    data = data + 'Communication with Chan has been Terminated.\n\n'
                    helper.WriteToLogFile(annchan_logfile, 'a', data)

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
                            packetData = anntojan_comm.pop(
                                0)  # Get the first element from list and delete it from there
                        except IndexError:
                            # send jan a packet with urgbit 1 with Chan being compromised
                            sourceid = listeningport  # The port listening to
                            destinationid = helper.namesAndPorts.get(
                                'Jan')  # The destination of the packet about to be sent is where the original packet came from
                            sequenceno = random.randint(10000,
                                                            99999)  # First time talking to client, create new that the other party is expecting
                            # Next byte of data that you want
                            acknumber = packetgoingindecoded.get('Sequence Number') + 1
                            packetData = 'Communication with Chan has been Compromised'  # Termination packet contain no data
                            urgentPointer = 1  # Urgent pointer is 1 to tell Jan that Chan has been compromised
                            synBit = 0  # Syn bit has to be one for the second step of
                            finBit = 0  #
                            rstBit = 0  # Not trying to reset connection, hence 0
                            terBit = 0
                            responsePacket = helper.CreateTCPPacket(sourceid, destinationid, acknumber,
                                                                    sequenceno, packetData, urgentPointer, synBit,
                                                                    finBit, rstBit, terBit)
                            # Send packet
                            helper.SerializeAndSendPacket(responsePacket, talkingport)
                            # log in the termination
                            timeStamp = time.time()
                            data = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S') + '\n'
                            data = data + 'Communication with Chan has been Terminated.\n\n'
                            helper.WriteToLogFile(annjan_logfile, 'a', data)

                    elif messagereceivedfrom == 'Chan':
                        try:
                            packetData = anntochan_comm.pop(0)  # Get the first element from list and delete it from there
                        except IndexError:
                            # Kick of connection tear down function here
                            pass

                    # Create packet with above data
                    responsePacket = helper.CreateTCPPacket(sourceid, destinationid, acknumber,
                                                            sequenceno, packetData, urgentPointer,
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
                        helper.WriteToLogFile(annjan_logfile, 'a', data)

                    elif messagereceivedfrom == 'Chan':
                        helper.WriteToLogFile(annchan_logfile, 'a', data)
                        chan_count = chan_count + 1

        return


# ------------------------------------------
# Function for the router threads to execute
# ------------------------------------------
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
        print('Problem creating server for agent Ann.')

    sys.exit()


if __name__ == '__main__':
    try:
        # Make sure the event is clear initially
        threadingEvent.clear()

        # Create a separate for Ann's server portion
        annserver = threading.Thread(target=server_agent, args=())

        # Start the Ann's server
        annserver.start()

        # Sleep to ensure that all agents are online
        time.sleep(10)
    except IOError:
        print("Couldn't create thread for Ann's router.")

    try:
        # Start connection setup with Chan
        sourceid = listeningport  # The port listening to
        destinationid = helper.namesAndPorts.get(
            'Chan')  # Trying to setup connection with Jan, so send the packet to Jan
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
        data = data + "Connection setup with Chan started. This is the first step of the threeway handshake.\n\n"
        helper.WriteToLogFile(annchan_logfile, 'a', data)

        # Run till connection teardown or termination
        while not threadingEvent.isSet():
            pass

        # Wait for ann's server to finish
        annserver.join()

        sys.exit()
    except KeyboardInterrupt:
        threadingEvent.set()  # Upon catching keyboard interrupt, let the threads know they have to exit

        # Wait for Ann's server to finish
        annserver.join()

        sys.exit()
