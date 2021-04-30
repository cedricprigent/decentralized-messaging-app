from app import app
import socket
import network_details

host_address = network_details.get_ip_address_2()

app.run(host=host_address)