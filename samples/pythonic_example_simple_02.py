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

ICX = '192.168.10.52'
vR = '192.168.45.20'

icxTransport = generic(host=ICX, username="admin", enable="password",
                    method="ssh", password="password")

vRTransport = generic(host=vR, username="vyatta", method="ssh", b64password="dnlhdHRh")

print "===ICX Configuration data and feedback:"

# Returns a dict with commands and responses as key/values
if icxTransport.connected:
    print icxTransport.configure([
                               "vlan 100 name Bob",
                               "untagged eth 1/1/15"
                              ])


print "\r\n===ICX Show VLAN brief:"
if icxTransport.connected:
    print icxTransport.read("show vlan brief", return_type="string")
    icxTransport.close()
    # print icxTransport.protocol
    # print icxTransport.connected
    # Note - no need to enter 'skip'. Pagination is turned off by code.


print "\r\n===vRouter Show Version:"

if vRTransport.connected:
    print vRTransport.read("show version", return_type="string")
    vRTransport.close()
