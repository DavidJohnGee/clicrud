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


class vdx1(object):
    ve1 = {'veint': '100',
           'vrf': '100',
           'ipaddr': '10.10.10.1/24',
           'static_routes':

           [{'prefix': '192.168.2.0/24',
             'nexthop': 'next-hop-vrf 101 ve 101'},

            {'prefix': '172.17.17.0/24',
             'nexthop': 'next-hop-vrf 3999 ve 3999'},

            {'prefix': '192.168.10.0/24',
             'nexthop': 'next-hop-vrf 3999 172.17.17.254'},

            {'prefix': '0.0.0.0/0',
             'nexthop': '10.10.10.254'},
            ]}

    ve2 = {'veint': '101',
           'vrf': '101',
           'ipaddr': '192.168.2.1/24',
           'static_routes':

           [{'prefix': '10.10.10.0/24',
             'nexthop': 'next-hop-vrf 100 ve 100'},

            {'prefix': '0.0.0.0/0',
             'nexthop': '192.168.2.254'},
            ]}

    ve3 = {'veint': '3999',
           'vrf': '3999',
           'ipaddr': '172.17.17.1/24',
           'static_routes':

           [{'prefix': '10.10.10.0/24',
             'nexthop': 'next-hop-vrf 100 ve 100'}
            ]}
