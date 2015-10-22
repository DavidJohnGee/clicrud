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
    # getpasswords = False - more for library usage and you must include password and enable in the kwargs for the call
    
    # The below would suite a scripting scenario
    # clicrud = setup(splash=False, getpasswords=False)
    
    # This one suites an interactive script
    clicrud = setup(splash=True)

    # This is where you build your threads.
    # Options for read:
    # read = target function in crud
    # clicrud = instance of clicrud underlying library
    # listofcommands = list of commands in a file (one per line)
    # method = telnet/ssh
    # fileoutput = True/False (based on device-date naming)
    # fileformat =  json/string
    # enable = enable password (If you insert "", the script will ask you for it)
    # password = user account password (If you insert "", the script will ask you for it)
    # username = user name of account
    # host = ip address or DNS lookup
    # port = port of service (telnet = 23, ssh = 22)

    #read = buildThread(read, clicrud, commands=["show version", "show stack"], method='telnet', fileoutput=True, fileformat='string',\
    #                   username="admin", host="192.168.10.52", port="23", enable="Passw0rd", password="Passw0rd")
    
    #read = buildThread(read, clicrud, listofcommands="commands.txt", method='ssh', fileoutput=True, fileformat='string',\
    #                   username="admin", host="192.168.10.52", port=22, enable="Passw0rd", password="Passw0rd",return_type="string")


    #read = buildThread(read, clicrud, command="show version", method='telnet', fileoutput=True, fileformat='string',\
    #                   username="admin", host="192.168.10.52", port=23, enable="Passw0rd", password="Passw0rd")



    # Usage specific to ICX6610
    #read = buildThread(read, clicrud, listofcommands="commands.txt", method='ssh', fileoutput=True, fileformat='string',\
    #                   username="admin", host="192.168.10.52", port=22, enable="Passw0rd", password="Passw0rd",return_type="string",type='icx6610')

    # Generic usage - this works for MLX, CER_CES
    cer_ces_1 = buildThread(read, clicrud, command="show version", method='ssh', fileoutput=True, fileformat='string',\
                       username="admin", host="192.0.2.1", port=22, enable="Passw0rd", password="Passw0rd", return_type="string")


    cer_ces_2 = buildThread(read, clicrud, command="show version", method='ssh', fileoutput=True, fileformat='string',\
                       username="admin", host="192.0.2.2", port=22, enable="Passw0rd", password="Passw0rd", return_type="string")
    
    # Start does multiple things. Adds the function to the thread list, start processes and enters a loop state
    # if one has been called for via useage of the CLI script    
    clicrud.start(cer_ces_1, cer_ces_2)
    
    
    # This one returns a dict where key = command and output= list of output lines
    #print read.output()
    # This one returns a decorated prettier string
    #print read.prettyOutput()
    
    # This does not immediately stop anything. It stops if the CLI loop exits
    clicrud.stop()
    