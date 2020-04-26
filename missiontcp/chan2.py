from socketserver import ThreadingMixIn, TCPServer, BaseRequestHandler

import datetime
import helper
import pickle
import random
import sys
import threading
import time

# Localhost IP for Chan
localhost = helper.localHost

# Port number for Chan + 1000
listeningport = helper.namesAndPorts.get('Chan')

# Closest router Chan will be sending msgs to
talkingport = helper.namesAndPorts.get('E')

# Communication files path
chantojan_file = './Communication Files/Chan/Chan-Jan.txt'
chantoann_file = './Communication Files/Chan/Chan-Ann.txt'

# Communication Log files
chanjanlog_file = './Communication Files/Chan/Chan-JanLog.txt'
chanannlog_file = './Communication Files/Chan/Chan-AnnLog.txt'

# Traverse communication btw agents from the text files
chantojan_comm = helper.ReadFile(chantojan_file)
chantoann_comm = helper.ReadFile(chantoann_file)

# Make sure log files are empty first
helper.WriteToLogFile(chanjanlog_file, 'w', '')
helper.WriteToLogFile(chanannlog_file, 'w', '')


# Class can be instantiated to create a multi-threaded server
class ServerThread(ThreadingMixIn, TCPServer):
    """Handle requests in a separate thread."""


# Request handler for the server portion of the agents
class RequestHandler(BaseRequestHandler):
    def handle(self):
        incoming_pckt = self.request.recv(4096)
        decoded_pckt = pickle.loads(incoming_pckt)
        receiver = helper.GetKeyFromValue(decoded_pckt.get('Source ID'))

        if decoded_pckt.get('Ter Bit') == 1:
            print('Connection terminated by Ann.\n')
            threading.Event().set()

        elif decoded_pckt.get('Syn Bit') == 1 and decoded_pckt.get('Acknowledgement Number') == -1:
            source_id = listeningport  # The port listening to
            destination_id = decoded_pckt.get('Source ID')
            sequence_num = random.randint(10000, 99999)
            ack_num = decoded_pckt.get('Sequence Number') + 1
            packet_data = ''
            urg_pointer = 0
            syn_bit = 1
            fin_bit = 0
            rst_bit = 0
            ter_bit = 0

            # Create packet with above data
            resp_pckt = helper.CreateTCPPacket(source_id, destination_id, ack_num, sequence_num, packet_data,
                                               urg_pointer, syn_bit, fin_bit, rst_bit, ter_bit)
            # Send packet
            helper.SerializeAndSendPacket(resp_pckt, talkingport)
            # Maintain log
            current_time = time.time()
            shared_data = datetime.datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S') + '\n'

            if receiver == 'Ann':
                shared_data = shared_data + 'Connection request from Ann.\n\n'
                helper.WriteToLogFile(chanannlog_file, 'a', shared_data)
            elif receiver == 'Jan':
                shared_data = shared_data + 'Connection requested from Jan.\n\n'
                helper.WriteToLogFile(chanjanlog_file, 'a', shared_data)

        elif decoded_pckt.get('Syn Bit') == 1:
            # Send data and raise the flag to wait for acknowledgement
            source_id = listeningport
            destination_id = decoded_pckt.get('Source ID')
            sequence_num = decoded_pckt.get('Acknowledgement Number')
            ack_num = decoded_pckt.get('Sequence Number') + 1
            urg_pointer = 0
            syn_bit = 0
            fin_bit = 0
            rst_bit = 0
            ter_bit = 0

            # Populate data field depending on who the connection is being established with
            if receiver == 'Ann':
                try:
                    packet_data = chantoann_comm.pop(0)  # Traverse the text file line by line
                except IndexError:
                    print('Chan-Ann.txt is empty.\n\n')

            elif receiver == 'Jan':
                try:
                    packet_data = chantojan_comm.pop(0)
                except IndexError:
                    print('Chan-Jan.txt is empty.\n\n')

            # Create packet with above data
            resp_pckt = helper.CreateTCPPacket(source_id, destination_id, ack_num, sequence_num, packet_data,
                                               urg_pointer, syn_bit, fin_bit, rst_bit, ter_bit)

            # Send packet
            helper.SerializeAndSendPacket(resp_pckt, talkingport)

            # Log what happened
            current_time = time.time()
            shared_data = datetime.datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S') + '\n'

            if receiver == 'Ann':
                shared_data = shared_data + 'Connection established with Ann.\n'
                shared_data = shared_data + packet_data + '\n\n'
                helper.WriteToLogFile(chanannlog_file, 'a', shared_data)
            elif receiver == 'Jan':
                shared_data = shared_data + 'Connection established with Jan.\n'
                shared_data = shared_data + packet_data + '\n\n'
                helper.WriteToLogFile(chanjanlog_file, 'a', shared_data)

        # Receiving data
        else:
            source_id = listeningport
            destination_id = decoded_pckt.get('Source ID')
            sequence_num = decoded_pckt.get('Acknowledgement Number')
            ack_num = decoded_pckt.get('Sequence Number') + len(decoded_pckt.get('Data'))
            urg_pointer = 0
            syn_bit = 0
            fin_bit = 0
            rst_bit = 0
            ter_bit = 0

            if receiver == 'Ann':
                try:
                    packet_data = chantoann_comm.pop(0)
                except IndexError:
                    pass

            elif receiver == 'Jan':
                try:
                    packet_data = chantojan_comm.pop(0)
                except IndexError:
                    pass

            # Create packet with above data
            resp_pckt = helper.CreateTCPPacket(source_id, destination_id, ack_num, sequence_num, packet_data,
                                               urg_pointer, syn_bit, fin_bit, rst_bit, ter_bit)

            # Send packet
            helper.SerializeAndSendPacket(resp_pckt, talkingport)

            current_time = time.time()
            shared_data = datetime.datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S') + '\n'
            shared_data = shared_data + 'Received following line.\n'
            shared_data = shared_data + decoded_pckt.get('Data')
            shared_data = shared_data + 'Acknowledgement sent along with below line.\n'
            shared_data = shared_data + packet_data + '\n\n'

            if receiver == 'Ann':
                helper.WriteToLogFile(chanannlog_file, 'a', shared_data)
            elif receiver == 'Jan':
                helper.WriteToLogFile(chanjanlog_file, 'a', shared_data)
        return


# Function for the router threads to execute
def server_agent():
    try:
        chan_server = ServerThread((localhost, listeningport), RequestHandler)
        chan_server.timeout = 0.01
        chan_server.daemon_threads = True

        # Poll so that you see the signal to exit as opposed to calling server_forever
        while not threading.Event().isSet():
            chan_server.handle_request()

        chan_server.server_close()
    except IOError:
        print('Problem creating server for agent Chan.')
    sys.exit()


if __name__ == '__main__':
    try:
        threading.Event().clear()
        # Chan server thread
        chanServer = threading.Thread(target=server_agent, args=())
        # Initiate server for Chan
        chanServer.start()
        # To bring all other nodes in sync
        time.sleep(10)
    except IOError:
        print("Couldn't create thread for Chan's router.")

    try:
        # Connection setup with Jan
        source_id = listeningport
        destination_id = helper.namesAndPorts.get('Jan')
        sequence_num = random.randint(1000, 9999)
        ack_num = -1
        packet_data = ''
        urg_pointer = 0
        syn_bit = 1
        fin_bit = 0
        rst_bit = 0
        ter_bit = 0

        # Create packet with above data
        resp_pckt = helper.CreateTCPPacket(source_id, destination_id, ack_num, sequence_num, packet_data,
                                           urg_pointer, syn_bit, fin_bit, rst_bit, ter_bit)
        # Send packet
        helper.SerializeAndSendPacket(resp_pckt, talkingport)
        # Log it
        current_time = time.time()
        shared_data = datetime.datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S') + '\n'
        shared_data = shared_data + "Establishing connection with server Jan initiated.\n\n"
        helper.WriteToLogFile(chanjanlog_file, 'a', shared_data)

        # Execute until connection termination
        while not threading.Event().isSet():
            pass

        # Wait for Chan's server to finish
        chanServer.join()
        sys.exit()
    except KeyboardInterrupt:
        print('Keyboard interrupt\n')
        threading.Event().set()
        chanServer.join()
        sys.exit()
