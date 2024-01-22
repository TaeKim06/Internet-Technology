#!/usr/bin/env python
'''
CS352 Assignment 1: Network Time Protocol
You can work with 1 other CS352 student
DO NOT CHANGE ANY OF THE FUNCTION SIGNATURES BELOW
'''

from socket import socket, AF_INET, SOCK_DGRAM
import struct
from datetime import datetime

def getNTPTimeValue(server="time.apple.com", port=123):
    # Create an NTP packet (48 bytes with all fields set to 0)
    ntp_packet = bytearray(48)
    ntp_packet[0] = 0x1B

    # Get the current time as a timestamp (T1)
    T1 = datetime.now().timestamp()

    # Create a UDP socket
    client_socket = socket(AF_INET, SOCK_DGRAM)
    
    # Send the NTP packet to the server
    client_socket.sendto(ntp_packet, (server, port))

    # Receive the response packet
    pkt, _ = client_socket.recvfrom(48)

    # Get the current time as a timestamp (T4)
    T4 = datetime.now().timestamp()

    return (pkt, T1, T4)
    

def ntpPktToRTTandOffset(pkt: bytes, T1: float, T4: float) -> (float, float):
    
    # unpack entire packet
    ntp_data = struct.unpack("!12I", pkt)
    
    # set variables equal to the place in the packet
    T2_sec = ntp_data[8]
    T2_frac = ntp_data[9]
    T3_sec = ntp_data[10]
    T3_frac = ntp_data[11]
    
    
    # Extract T2 and T3 bytes from the NTP packet
    # 2208988800 subtracted for the start date
    T2 = (T2_sec + T2_frac / 2**32) - 2208988800
    T3 = (T3_sec + T3_frac / 2**32) - 2208988800

    # Calculate RTT and offset
    rtt = (T4 - T1) - (T3 - T2)
    offset = ((T2 - T1) + (T3 - T4)) / 2
    # print(rtt, offset)
    return (rtt, offset)

def getCurrentTime(server="time.apple.com", port=123, iters=20):
    total_offset = 0
    
    # Perform multiple iterations to get a more accurate time
    for _ in range(iters):
        pkt, T1, T4 = getNTPTimeValue(server, port)
        rtt, offset = ntpPktToRTTandOffset(pkt, T1, T4)
        total_offset += offset
    
    # Calculate the average offset and add it to the current time
    average_offset = total_offset / iters
    currentTime = datetime.now().timestamp() + average_offset
    
    return currentTime

if __name__ == "__main__":
    print(getCurrentTime())