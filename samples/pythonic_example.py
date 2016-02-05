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

from clicrud.device.generic import generic
from attributes import _attributes

icx6610 = _attributes()

transport = generic(host="192.168.10.52", username="admin", enable="Passw0rd",
                    method="ssh", password="Passw0rd", attributes=icx6610)

print "===Configuration data and feedback:"
# Returns a dict with commands and responses as key/values
print transport.configure([
                           "vlan 100 name Bob",
                           "untagged eth 1/1/15"
                           ])

print "\r\n===Show VLAN 100:"
print transport.read("show vlan 100", return_type="string")

print "\r\n===Show Attributes:"
print icx6610.devices

# Note - no need to enter 'skip'. Pagination is turned off by code.

# print transport.protocol
# print transport.connected
transport.close()
