from scapy.all import *
import sys
import time
import math


# make sure to load the HTTP layer or your code wil silently fail
load_layer("http")


"""
input Arguments: a pcapng file, a destination server IP address and a destination port, as:
measure-webserver.py <input-file> <server-ip> <server-port>
"""

if len(sys.argv) != 4:
    print("Usage: python3 measure-webserver.py <input-file> <server-ip> <server-port>")
elif len(sys.argv) == 4:
    inputFile = sys.argv[1]
    serverIP = sys.argv[2]
    port = sys.argv[3]
    requests = {}
    requestTimes = []

    # example counters 
    number_of_packets_total = 0  
    number_of_tcp_packets = 0
    number_of_udp_packets = 0
    totalResponseTime = 0
    avgCounter = 0

    processed_file = rdpcap(inputFile)  # read in the pcap file 
    sessions = processed_file.sessions()    #  get the list of sessions 
    for session in sessions:      

        for packet in sessions[session]:    # for each packet in each session
            number_of_packets_total = number_of_packets_total + 1  #increment total packet count 

            if packet.haslayer(TCP):        # check is the packet is a TCP packet
                number_of_tcp_packets = number_of_tcp_packets + 1   # count TCP packets 
                source_ip = packet[IP].src   # note that a packet is represented as a python hash table with keys corresponding to 
                dest_ip = packet[IP].dst     # layer field names and the values of the hash table as the packet field values
                
                # print(currentTime)
                if (packet.haslayer(HTTP)):
                    if HTTPRequest in packet and str(dest_ip) == serverIP:   
                        arrival_time = packet.time
                        requests[(source_ip, dest_ip, packet[TCP].sport)] = {'arrival time': arrival_time}
                        # avgCounter = avgCounter + 1
                        # currentTime = time.time()
                        # currentTime = currentTime - arrival_time
                        # print(currentTime)
                        # print ("Got a TCP packet part of an HTTP request at time: %0.5f for server IP %s" % (arrival_time,dest_ip))
                        # packet.show()
                    elif HTTPResponse in packet and str(source_ip) == serverIP:
                        
                        response_time = packet.time
                        matchingRequest = requests.get((dest_ip, source_ip, packet[TCP].dport))
                        if matchingRequest:
                            requestLatency = response_time - matchingRequest['arrival time']
                            avgCounter = avgCounter + 1
                            totalResponseTime = totalResponseTime + requestLatency
                            requestTimes.append(requestLatency)
                            # print("Got a TCP packet part of an HTTP response at time: %0.5f for server IP %s" % (response_time, source_ip))
                            # print("Response time: %0.5f seconds" % requestLatency)
            else:
                if packet.haslayer(UDP):
                    number_of_udp_packets = number_of_udp_packets + 1
    # print(requests)
    # print(requestTimes)
    requestTimes = sorted(requestTimes)
    # print(requestTimes)
    percentileOne = int(avgCounter * .25)
    percentileTwo = int(avgCounter * .5)
    percentileThree = int(avgCounter * .75)
    percentileFour = int(avgCounter * .95)
    percentileFive  = int(avgCounter * .99)
    if avgCounter != 0:
        print("AVERAGE LATENCY: %0.5f" % (totalResponseTime/avgCounter))
        # print("PERCENTILES: %0.5f 25% ," % totalResponseTime)
        # print(" %0.5f 50%," % totalResponseTime)
        # print(" %0.5f 75%," % totalResponseTime)
        print("PERCENTILES: %0.5f, %0.5f, %0.5f, %0.5f, %0.5f" % (requestTimes[percentileOne], requestTimes[percentileTwo], requestTimes[percentileThree], requestTimes[percentileFour], requestTimes[percentileFive]))

'''
The code must produce 2 lines of output:
AVERAGE LATENCY: <float>
PERCENTILES: <float-25%> , <float-50%>, <float-75%>, <float-95%>, <float-99%>
'''

