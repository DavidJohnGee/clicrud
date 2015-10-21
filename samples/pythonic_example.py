from clicrud.device.icx6610 import icx6610
from clicrud.device.generic import generic

# Telnet version - port doesn't have to be included. It will default to 23.
#transport = icx6610(host="192.168.10.52", username="admin", enable="Passw0rd", port=23, method="telnet", password="Passw0rd", setup=None)

# SSH Version - port doesn't have to be included. It will default to 22.
#transport = icx6610(host="192.168.10.52", username="admin", enable="Passw0rd", port=22, method="ssh", password="Passw0rd")
transport = generic(host="192.0.2.1", username="admin", enable="Passw0rd", port=22, method="ssh", password="Passw0rd")

# Note - no need to enter 'skip'. Pagination is turned off by code. Just worry about the command!
print transport.read("show version", return_type="string")

#print transport.protocol
#print transport.connected
transport.close()
