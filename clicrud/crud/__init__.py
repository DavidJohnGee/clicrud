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

import logging
import time
import json
import sys

from clicrud.device.generic import generic


def read(queue, finq, ranonceq, **kwargs):
    _cli_input = "['command', 'commands', 'listofcommands']"
    _command_list = []
    _kwargs = {}
    _kwargs = kwargs
    _output_dict = {}
    # _ranonce = False
    for key in _kwargs:
        if key in _cli_input:
            if key == 'command':
                _command_list.append(_kwargs.get(key))
            if key == 'commands':
                for key1 in _kwargs.get('commands'):
                    _command_list.append(key1)
            if key == 'listofcommands':
                try:
                    _command_file = open(_kwargs.get('listofcommands'), 'r')
                    _output = _command_file.readlines()
                    _command_file.close()
                    for line in _output:
                        line = line.translate(None, '\r\n')
                        _command_list.append(line)

                except:
                    logging.error("Could not open 'listofcommands' file")

    # Build transport
    _transport = generic(**_kwargs)

    if _transport.err:
        finq.put('error')
        _transport.close()
        return
    # Now we want to call each command and put the string output in a list
    for index, command in enumerate(_command_list):
        _output_dict[command] = _transport.read(command, return_type='string')
        if _kwargs['setup']._splash is True:
            sys.stdout.write("\r[%4s/%4s] Complete - " % (len(_command_list),
                                                          index+1) +
                             time.strftime("%d-%m-%Y") +
                             time.strftime("-%H:%M:%S"))
            sys.stdout.flush()
        # PEP8 Fix
        # if _kwargs.has_key('delay'):
        if "delay" in _kwargs:
            time.sleep(_kwargs['delay'])

    # Sets the ranonce bool if triggered once
    # if not _ranonce:
    #    _ranonce = True
    #    ranonceq.put(True)
    ranonceq.put(True)

    queue.put(_output_dict)

    # If we need to output to a file, let's do that.
    # PEP8 Fix
    # if _kwargs.has_key('fileoutput'):
    if "fileoutput" in _kwargs:
        # Create a filename on hostname+date
        # Output the _output_dict to it in the right format
        _filename = _transport.hostname
        _filename += time.strftime("%d-%m-%Y-") + time.strftime("-%H-%M-%S")

        try:
            f = open(_filename, 'w')
            if _kwargs.get('fileformat') == 'json':
                f.write(json.dumps(_output_dict))
            if _kwargs.get('fileformat') == 'string':
                for command in _command_list:
                    f.write("COMMAND: " + command + "--------------------\r\n")
                    f.write(_output_dict.get(command) + "\r\n\r\n")
            f.close()

        except:
            logging.error("Could not open/create file for output of commands")

    finq.put('completed_run')
    _transport.close()
    # print _command_list
