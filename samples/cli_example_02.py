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

from clicrud.clicrud.setup import setup
from clicrud.clicrud.multiprocess import buildThread
from clicrud.crud import read

if __name__ == '__main__':

    # Let's do some setting up
    # splash = True (for scripting - makes a pretty CLI
    # getpasswords = True - the CLI will prompt you for what's missing
    # getpasswords = False - more for library usage and you must include
    # password and enable in the kwargs for the call

    # The below would suite a scripting scenario
    # clicrud = setup(splash=False, getpasswords=False)

    # This one suites an interactive script
    clicrud = setup(splash=True)

    # This is where you build your threads
    # Options for read:
    # read = target function in crud
    # clicrud = instance of clicrud underlying library
    # listofcommands = list of commands in a file (one per line)
    # method = telnet/ssh
    # fileoutput = True/False (based on device-date naming)
    # fileformat =  json/string
    # enable = enable password (insert "", the script will prompt)
    # password = password (insert "", the script will prompt)
    # username = user name of account
    # host = ip address or DNS lookup
    # port = port of service (telnet = 23, ssh = 22)

    # read = buildThread(read, clicrud, commands=["show version", "show x"],
    #        method='telnet', fileoutput=True, fileformat='string',
    #        username="admin", host="192.168.10.52", enable="Passw0rd",
    #        password="Passw0rd")

    # Usage specific to ICX6610. 'Telnet' and 'ssh' methods exist
    # To override the port defaults of 22 & 23, add port=NUMBER to each KWARG

    # read = buildThread(read, clicrud, listofcommands="commands.txt",
    #        method='telnet', fileoutput=True, fileformat='string',
    #        username="admin", host="192.168.10.52", enable="Passw0rd",
    #        password="Passw0rd",type='icx6610')

    # Generic usage - this works for MLX, CER_CES. Change ports and methods
    # between 'telnet' and 'ssh'.

    # read = buildThread(read, clicrud, command="show version", method='ssh',
    #    fileoutput=True, fileformat='string',username="admin",
    #    host="192.0.2.2", enable="Passw0rd", password="Passw0rd")

    # read = buildThread(read, clicrud, command="show version", method='ssh',
    #    username="admin", host="192.0.2.2", enable="Passw0rd",
    #    password="Passw0rd")

    read1 = buildThread(read, clicrud, command="show version", fileoutput=True,
                        fileformat='string', method='ssh',
                        username="admin", host="192.0.2.1",
                        password="Passw0rd", enable="Passw0rd")

    read2 = buildThread(read, clicrud, command="show version", fileoutput=True,
                        fileformat='string', method='ssh',
                        username="admin", host="192.0.2.2",
                        password="Passw0rd", enable="Passw0rd")

    # Start does multiple things. Adds the function to the thread list, start
    # processes and enters a loop state if one has been called for via useage
    # of the CLI script
    clicrud.start(read1, read2)

    # This one returns a dict where key = command and output= list of
    # output lines
    # print read.output()
    # This one returns a decorated prettier string
    # print read.prettyOutput()

    # This does not immediately stop anything. It stops if the CLI loop exits
    clicrud.stop()
