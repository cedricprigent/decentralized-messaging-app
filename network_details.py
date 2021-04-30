import socket
import os

def get_ip_address_1():
    """
    Function to get ip address of the local network
    """
    ipaddr = socket.gethostbyname(socket.gethostname())
    if ipaddr.startswith('127'):
        #Cas specifique pour les cartes raspberry
        gw = os.popen("ip -4 route show default").read().split()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((gw[2], 0))
        ipaddr = s.getsockname()[0]
    return ipaddr

def get_ip_address_2():
    return ([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] 
    if ip.startswith("192.168.0")][:1], [[(s.connect(('8.8.8.8', 53)), 
    s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, 
    socket.SOCK_DGRAM)]][0][1]]) if l][0][0])