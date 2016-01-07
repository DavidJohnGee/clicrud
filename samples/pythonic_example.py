#!/usr/bin/env python
"""
Copyright 2015 Brocade Communications Systems, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from clicrud.device.icx6610 import icx6610
from clicrud.device.generic import generic

# Telnet version: port doesn't have to be included. It will default to 23
# transport = icx6610(host="192.168.10.52", username="admin",
#                     enable="Passw0rd", port=23, method="telnet",
#                     password="Passw0rd", setup=None)

# SSH Version: port doesn't have to be included. It will default to 22
#                     enable="Passw0rd", port=22, method="ssh",
# transport = icx6610(host="192.168.10.52", username="admin",
#                     password="Passw0rd")

transport = icx6610(host="192.168.10.52", username="admin", enable="Passw0rd",
                    method="ssh", password="Passw0rd")

# Note - no need to enter 'skip'. Pagination is turned off by code.
# Just worry about the command!



print transport.read("show version", return_type="string")

print "\nATTRIBUTES\n" + str(transport.attributes)

# print transport.protocol
# print transport.connected
transport.close()
