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

transport = generic(host="10.18.254.67", username="admin", enable="password",
                    method="telnet", password="password")

# print "===Configuration data and feedback:"

# Returns a dict with commands and responses as key/values
"""print transport.configure([
                           "vlan 100 name Bob",
                           "untagged eth 1/1/15"
                           ])
"""

print "\r\n===Show VLAN brief:"
print transport.read("show vlan brief", return_type="string")

# Note - no need to enter 'skip'. Pagination is turned off by code.

# print transport.protocol
# print transport.connected
transport.close()
