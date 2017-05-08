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

import paramiko
import time
import telnetlib
import io
import logging
import sys
import re
import base64


class telnet(object):

    def __init__(self, **kwargs):
        _args = {}
        _opts = {}
        self._error = False
        self.output = ""
        self._NOS_present = False
        self._VYATTA_present = False
        self._clean_ansi = re.compile(r'((\x9B |\x1B\[)[0 -?]*[-\ /]*[ @ -~])|=')
        self._hostname = ""
        _t_args = kwargs
        if _t_args.get('setup'):
            if kwargs['setup'] is not None:
                _opts = kwargs['setup']._options
                _args['splash'] = kwargs['setup']._splash
                _args['period'] = _opts.period
                _args['loop'] = _opts.loop
        else:
            _args['splash'] = False

        _args.update(_t_args)

        if 'b64password' in _args:
            _args['password'] = base64.b64decode(_args['b64password'])

        if 'b64enable' in _args:
            _args['enable'] = base64.b64decode(_args['b64enable'])

        # Check for port value. If it doesn't exist, or is None, default to 23
        if _args.get('port'):
            if _args['port'] is None:
                _args['port'] = 23
        else:
            _args['port'] = 23

        # Make these global per instance
        self._args = _args

        try:
            self.client = telnetlib.Telnet(str(_args['host']),
                                           _args['port'], 10)

        except Exception, err:
            sys.stderr.write('\nERROR for host: %s - %s\n' %
                             (_args['host'], str(err)))

            logging.error('ERROR for host %s - %s\n:' %
                          (_args['host'], err))

            self._error = True
            return

        # Let's detect whether authentication or enable modes
        # for auth are configured
        _detect = True
        _vdxTrickery = False
        _detect_buffer = ""
        _timer = 0
        self._send_username = False
        self._send_enable = False
        try:
            while _detect:
                _detect_buffer += self.client.read_some()
                _detect_buffer = _detect_buffer.lower()
                if "password:" in _detect_buffer:
                    self.client.write("null\r\n")
                    time.sleep(1)
                    _detect_buffer = ""
                    continue
                if "name:" in _detect_buffer:
                    self._send_username = True
                    _detect = False
                    continue
                if "login:" in _detect_buffer:
                    self._send_username = True
                    _detect = False
                    continue
                if "login" in _detect_buffer:
                    self._send_username = True
                    _detect = False
                    continue
                if ">" in _detect_buffer:
                    self._send_enable = True
                    _detect = False
                    continue
                time.sleep(0.1)
                _timer += 1
                if _timer >= 240:
                    _detect = False

        except Exception, err:
            sys.stderr.write('\nERROR for host: %s - %s\n' % (_args['host'],
                                                              str(err)))

            logging.error('ERROR for host %s - %s\n:' % (_args['host'], err))
            self._error = True
            return

        # Now we know whether we need to send a username or enable password
        if self._send_username:
            if self._VYATTA_present:
                self.client.write("%s\n" % _args['username'])
            else:
                self.client.write("%s\r\n" % _args['username'])
            _detect_buffer = ""
            _detect_buffer += self.client.read_some()
            _detect_buffer = _detect_buffer.lower()

            # To deal with spurious VDX Telnet issues
            if 'password' and 'login' in _detect_buffer:
                self.client.write("null\r\n")
                time.sleep(0.5)
                _detect = True
                while _detect:
                    _detect_buffer = ""
                    _detect_buffer += self.client.read_some()
                    _detect_buffer = _detect_buffer.lower()

                    if "login" in _detect_buffer:
                        self.client.write("%s\r\n" % _args['username'])
                        _detect = False
                        _detect_buffer = ""
                        _detect_buffer += self.client.read_some()
                        _detect_buffer = _detect_buffer.lower()
                        continue
                    if "name" in _detect_buffer:
                        self.client.write("%s\r\n" % _args['username'])
                        _detect_buffer = ""
                        _detect_buffer += self.client.read_some()
                        _detect_buffer = _detect_buffer.lower()
                        _detect = False
                        continue
                    if _detect:
                        time.sleep(0.1)
                        _timer += 1
                        if _timer >= 240:
                            _detect = False

            # To deal with spurious VDX Telnet issues
            if 'password' in _detect_buffer:
                self.client.write(_args['password'] + "\r")

            _detect = True

            while _detect:
                _detect_buffer = ""
                _detect_buffer += self.client.read_some()
                _detect_buffer = _detect_buffer.lower()

                # VDX CLI trickery I tell ye
                if "warning: the default password of" in _detect_buffer:
                    _detect = False
                    _vdxTrickery = True
                    continue

                # Just in case password is located
                if "password" in _detect_buffer:
                    _detect = False
                    continue

                if _detect:
                    time.sleep(0.1)
                    _timer += 1
                    if _timer >= 240:
                        _detect = False

            if self._VYATTA_present:
                self.client.write(_args['password'] + "\n")

            if _vdxTrickery:
                _error_check = self.client.read_until("accounts have not been changed", timeout=2)

            if not self._VYATTA_present and not _vdxTrickery:
                self.client.write(_args['password'] + "\r")
            # Now we need to read some until we get > or #
            # to determine enable requirement
            _detect = True
            _detect_buffer = ""
            _timer = 0
            self._send_username = False
            self._send_enable = False
            try:
                self.client.write("\r")
                while _detect:
                    _detect_buffer += self.client.read_some()
                    if "failure" in _detect_buffer:
                        raise Exception('Incorrect authentication details')
                    if ">" in _detect_buffer:
                        self._send_enable = True
                        _detect = False
                        continue
                    if "#" in _detect_buffer:
                        self._send_enable = False
                        _detect = False
                        # Takes in to account exec banner
                        self.client.read_until("#", timeout=1)
                        # Do this to get a clean prompt
                        self.client.write("\r")
                        self._hostname = self.client.read_until("#")
                        self._hostname = self._hostname.translate(None, '\r\n')

                        vercheck = self.read("show version | inc NOS", return_type="string")

                        # Need this to clear the receive buffer
                        self.client.write("\n\r")
                        self.output = self.client.read_until(self._hostname)

                        if 'NOS' in vercheck:
                            self._NOS_present = True

                        if self._NOS_present is True:
                            self.client.write("terminal length 0\r\n")
                            self.output = self.client.read_until(self._hostname)
                            _detect = False
                            # continue

                        if self._NOS_present is False and self._VYATTA_present is False:
                            self.client.write("skip\r\n")
                            self.output = self.client.read_until(self._hostname)
                            _detect = False

                    if "$" in _detect_buffer:
                        self._send_enable = False
                        _detect = False
                        # Takes in to account exec banner
                        self.client.read_until("$", timeout=1)
                        # Do this to get a clean prompt
                        self.client.write("\r")
                        self._hostname = self.client.read_until("$")
                        self._hostname = self._hostname.translate(None, '\r\n ')
                        self._VYATTA_present = True

                    if _detect:
                        time.sleep(0.1)
                        _timer += 1
                        if _timer >= 10:
                            _detect = False

            except Exception, err:
                sys.stderr.write('\nERROR for host: %s - %s\n' %
                                 (_args['host'], str(err)))

                logging.error('ERROR for host %s - %s\n:' %
                              (_args['host'], err))

                self._error = True
                return

        if self._send_enable:
            _detect = True
            _detect_buffer = ""
            _timer = 0
            self.client.write("en\n\r")
            try:
                while _detect:
                    _detect_buffer += self.client.read_some()
                    _detect_buffer = _detect_buffer.lower()
                    if "#" in _detect_buffer:
                        # Takes in to account exec banner
                        self.client.read_until("#", timeout=1.5)
                        # Do this to get a clean prompt
                        self.client.write("\r")
                        self._hostname = self.client.read_until("#")
                        self._hostname = self._hostname.translate(None, '\r\n')
                        _detect = False
                        continue

                    if "no password has been assigned" in _detect_buffer:
                        self._send_enable = False
                        _detect = False
                        # Takes in to account exec banner
                        _error_check = self.client.read_until("#", timeout=1)

                        # Do this to get a clean prompt
                        self.client.write("\r")
                        self._hostname = self.client.read_until("#")
                        self._hostname = self._hostname.translate(None, '\r\n')
                        continue

                    if "password" in _detect_buffer:
                        self._send_enable = False
                        _detect = False
                        self.client.write(_args['enable'] + "\r")
                        # Takes in to account exec banner
                        _error_check = self.client.read_until("#", timeout=1)

                        if "incorrect" in _error_check:
                            raise Exception('Incorrect authentication details')

                        # Do this to get a clean prompt
                        self.client.write("\r")
                        self._hostname = self.client.read_until("#")
                        self._hostname = self._hostname.translate(None, '\r\n')
                        continue

                    if _detect:
                        time.sleep(0.1)
                        _timer += 1
                        if _timer >= 30:
                            _detect = False

                if _detect is False:

                    # Clear the buffer 'not quite empty' scenario.
                    _error_check = self.client.read_until("#", timeout=2)
                    tmp = self.read("show version | inc NOS", return_type="string")

                    # Need this to clear the receive buffer
                    self.client.write("\n\r")
                    self.output = self.client.read_until(self._hostname)
                    _error_check = self.client.read_until("#", timeout=2)

                    if 'NOS' in tmp:
                        self._NOS_present = True

                    if self._NOS_present:
                        self.client.write("terminal length 0\r\n")
                        self.output = self.client.read_until(self._hostname)
                        _detect = False

                    if self._NOS_present is False:
                        self.client.write("skip\r")
                        self.output = self.client.read_until(self._hostname)
                        _detect = False


            except Exception, err:
                sys.stderr.write('\nERROR for host: %s - %s\n' %
                                 (_args['host'], str(err)))
                logging.error('ERROR for host %s - %s\n:' %
                              (_args['host'], err))

                self._error = True
                return

        self.client.write("\r")
        self.output = self.client.read_until(self._hostname)
        # self.output = self.client.read_until(self._hostname)

        logging.info("Telnet class instantiated")

        # Clean up the buffer
        _error_check = self.client.read_until("#", timeout=2)

        logging.info("Checking for attributes")
        if "attributes" in _args:
            _args['attributes'].get_attributes(transport="telnet",
                                               instance=self)

    @property
    def hostname(self):
        return self._hostname

    def read(self, command, **kwargs):
        """
        Executes operational command on the device.

        Arguments:
            command  = a string command
            **kwargs = return_type = string

        Returns:
            A string if requested, or a list if not

        Throws:
            Nothing

        Notes:
            Do not try and frak with this. If you want
            to run config, do it with the configure method.
        """
        # _detect_buffer += self.client.read_some()
        # _detect_buffer = _detect_buffer.lower()

        _string = ""
        _args = kwargs
        if self._NOS_present is True:
            self.client.write("%s\r\n" % command)
            # Bug fix for no response on VDXs.
            # The first line of output was actually the hostname :( Oops
            self._read_data = self.client.read_until(self._hostname.strip())

        if self._VYATTA_present is True:
            self.client.write("%s | no-more\n" % command)
            self._read_data = self.client.read_until(self._hostname.strip())

        if self._NOS_present is False and self._VYATTA_present is False:
            self.client.write("%s\r\n" % command)
            self._read_data = self.client.read_until(self._hostname.strip())

        self._temp_data = io.BytesIO(self._read_data)
        self._lines = self._temp_data.readlines()
        return_list = []


        if self._NOS_present:
            self.client.write("\r\n")
            _error_check = self.client.read_until(self._hostname, timeout=2)

        for line in self._lines:
            if line != '\r\n' and line != self._hostname:
                line = line.translate(None, '\r\n')
                line = line.strip()
                line = self._clean_ansi.sub('', line)
                if command not in line and self._hostname not in line:
                    return_list.append(line)

        if "return_type" in _args:
            if _args.get('return_type') == 'string':
                for line in return_list:
                    _string += line + '\n'
            return _string[:-1]
        else:
            return return_list

    def configure(self, commands, **kwargs):
        """
        Executes configuration on the device.
        Might not return anything (probably will not)

        Arguments:
            commands = a list of commands
            **kwargs = none

        Returns:
            a dictionary, with KV values of command
            and returned values

        Throws:
            Nothing

        Notes:
            This method takes care of mode switching
            between config and operational. Do not worry!
        """

        _args = kwargs
        _commands = commands
        _dict_response = {}

        for _command in _commands:
            _dict_response[_command] = ''

        # Lets get the latest hostname. It could have changed
        self.client.write("\r\n")
        if self._VYATTA_present:
            self._hostname = self.client.read_until("$")
        else:
            self._hostname = self.client.read_until("#")
        self._hostname = self._hostname.translate(None, '\r\n ')
        self._hostname = self._hostname.strip()

        # Let's figure out what our new prompt looks like
        if self._VYATTA_present:
            self.client.write("%s\n" % "configure")
        else:
            self.client.write("%s\r\n" % "conf t")

        self.client.read_until("#")
        self.client.write("\r\n")
        self.client.read_until("#")
        self.client.write("\r\n")
        self._config_hostname = self.client.read_until("#")
        self._config_hostname = self._config_hostname.translate(None, '\r\n ')
        self._config_hostname = self._config_hostname.strip()
        if self._VYATTA_present:
            self._config_hostname = self._config_hostname.replace('[edit]', '')


        # At this point we should be in config mode. Let's send the commands
        # Also - the prompt can change (thanks devs). Let's ignore the prompt
        # only save the actual output.

        if not self._VYATTA_present:
            self._mass_data = ""
            for _command in _commands:
                self.client.write("\r\n")
                self._temp_line = self.client.read_until(")#")
                self.client.write("%s\r\n" % _command)
                time.sleep(0.5)
                self._temp_line = self.client.read_until(")#")

                _tmp = io.BytesIO(self._temp_line)
                self.count = 0

                while self.count < 1:
                    _tmp.readline()
                    self.count += 1

                self._config_hostname = _tmp.readline()

                self._response = self._temp_line
                self._temp_data = io.BytesIO(self._response)
                self._lines = self._temp_data.readlines()

                # Let's strip out the whitespace
                for _val, _line in enumerate(self._lines):

                    if _command not in _line and ')#' not in _line:
                        _dict_response[_command] = _line



            self.client.write("%s\r\n" % "end")
            self.client.read_until("#")
            if self._NOS_present:
                self.client.write("\r\n")
                self.client.write("\r\n")
                self.client.read_until(self._hostname)

        if self._VYATTA_present:
            self._mass_data = ""
            for _command in _commands:
                self.client.write("\n")
                self._temp_line = self.client.read_until(self._config_hostname)
                self.client.write("%s\n" % _command)
                time.sleep(0.1)
                self._temp_line = self.client.read_until(self._config_hostname)

                _tmp = io.BytesIO(self._temp_line)
                self.count = 0

                while self.count < 1:
                    _tmp.readline()
                    self.count += 1

                self._response = self._temp_line
                self._temp_data = io.BytesIO(self._response)
                self._lines = self._temp_data.readlines()

                # Let's strip out the whitespace
                _tmplines = ""
                _tmpline = ""
                for _val, _line in enumerate(self._lines):
                    if _command not in _line and self._config_hostname not in _line and '[edit]' not in _line:
                        _tmpline = _line.translate(None, '\r\n')
                        _tmpline = _tmpline.strip()
                        if _tmpline != '':
                            _tmplines = _tmplines + _tmpline + "\r\n"


                _dict_response[_command] = _tmplines

            self.client.write("%s\n" % "commit")
            self.client.read_until(self._config_hostname)

            # Clean up any dodgy buffer remains

        _error_check = self.client.read_until("#", timeout=2)
        _error_check = self.client.read_until("#", timeout=2)

        return _dict_response

    def close(self):
        self.client.close()

    @property
    def connected(self):
        if self.client.sock:
            return True

    @property
    def protocol(self):
        return self._args.get('method')


class ssh(object):

    def __init__(self, **kwargs):
        paramiko.common.logging.basicConfig(level=paramiko.common.WARNING, filename='clicrud-paramiko.log')
        paramiko.util.log_to_file('clicrud.log')

        _args = {}
        _opts = {}
        self._error = False
        self._NOS_present = False
        self._VYATTA_present = False
        self._clean_ansi = re.compile(r'((\x9B |\x1B\[)[0 -?]*[-\ /]*[ @ -~])|=')

        _t_args = kwargs
        if _t_args.get('setup'):
            if kwargs['setup'] is not None:
                _opts = kwargs['setup']._options
                _args['splash'] = kwargs['setup']._splash
                _args['period'] = _opts.period
                _args['loop'] = _opts.loop
        else:
            _args['splash'] = False

        _args.update(_t_args)

        if 'b64password' in _args:
            _args['password'] = base64.b64decode(_args['b64password'])

        if 'b64enable' in _args:
            _args['enable'] = base64.b64decode(_args['b64enable'])

        # Check for port value. If it doesn't exist, default to 22
        if _args.get('port'):
            if _args['port'] is None:
                _args['port'] = 22
        else:
            _args['port'] = 22

        # Make these global per instance
        self._args = _args

        self.client = paramiko.SSHClient()
        self.client.load_system_host_keys()
        # Added 4th Jan 2016
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # self.client.get_host_keys().add(_args['host'], 'ssh-rsa', key)
        try:
            self.client.connect(_args['host'],
                                username=_args['username'],
                                password=_args['password'],
                                port=_args['port'],
                                timeout=10)

            self.client_conn = self.client.invoke_shell()
            # Check for mode (enable/no-enable)

            time.sleep(0.5)
            self.output = self.blocking_recv()



            if ">" in self.output:
                self.client_conn.send("en\n")
                self.output = self.blocking_recv()
                self.client_conn.send(_args['enable'] + "\n")
                self.output = self.blocking_recv()

            # Check for error
            if "incorrect" in self.output:
                raise Exception('Incorrect authentication details')

            # We should be in enable at this point
            if "#" in self.output:
                self.client_conn.send("\n")
                self.output = self.blocking_recv()
                self._hostname = self.output.translate(None, '\r\n')

                self.client_conn.sendall("show version | inc NOS\n")

                tmp = self.read("show version | inc NOS", return_type="string")

                if 'NOS' in tmp:
                    self._NOS_present = True

                if self._NOS_present:
                    self.client_conn.send("terminal length 0\r\n")
                else:
                    self.client_conn.send("skip\r\n")

                self.output = self.blocking_recv()
                # self.client.close()

            # vRouter add in
            if "$" in self.output:
                self.client_conn.send("\n")
                self.output = self.blocking_recv()
                self._hostname = self.output.translate(None, '\r\n')
                self.client_conn.send("\n")
                self.output = self.blocking_recv()
                self._hostname = self.output.translate(None, '\r\n')
                self._VYATTA_present = True

        except Exception, err:
            sys.stderr.write('\nERROR for host: %s - %s\n' %
                             (_args['host'], str(err)))

            logging.error('ERROR for host %s - %s\n:' % (_args['host'], err))
            self._error = True
            return

        logging.info("SSH class instantiated")

        logging.info("Checking for attributes")
        if "attributes" in _args:
            _args['attributes'].get_attributes(transport="ssh",
                                               instance=self)

    @property
    def hostname(self):
        return self._hostname

    def blocking_recv(self, *args):
        _output = ""
        _block = True

        while _block:
            if not args:
                _block = False
            while not self.client_conn.recv_ready():
                time.sleep(0.1)
            while self.client_conn.recv_ready():
                time.sleep(0.1)
                _output += self.client_conn.recv(1000000)
            if args:
                for _arg in args:
                    if _arg in _output:
                        _block = False
        return _output

    def read(self, command, **kwargs):
            _args = kwargs
            _returnlist = []
            _string = ""

            if self._VYATTA_present:
                self.client_conn.send(command + " | no-more \n")
            else:
                self.client_conn.send(command + "\n")

            self.output = self.blocking_recv(self._hostname)
            stream = io.BytesIO(self.output)
            self.count = 0

            while self.count < 1:
                stream.readline()
                self.count += 1
            # At this point, we're to the top of the stream and
            # beyond the hostname and \r\n\r\n mess
            _lines = stream.readlines()
            for line in _lines:
                if line != '\r\n' and line != self._hostname:
                    line = line.translate(None, '\r\n')
                    if line != command:
                        # remove ANSI escape sequences :(
                        line = self._clean_ansi.sub('', line)

                        if self._hostname not in line:
                            _returnlist.append(line)



            if "return_type" in _args:
                if _args.get('return_type') == 'string':
                    for line in _returnlist:
                        _string += line + '\n'
                return _string[:-1]
            else:
                return _returnlist

    def configure(self, commands, **kwargs):
        """
        Executes configuration on the device.
        Might not return anything (probably will not)

        Arguments:
            commands = a list of commands
            **kwargs = none

        Returns:
            a dictionary, with KV values of command
            and returned values

        Throws:
            Nothing

        Notes:
            This method takes care of mode switching
            between config and operational. Do not worry!
        """

        _args = kwargs
        _commands = commands
        _dict_response = {}

        for _command in _commands:
            _dict_response[_command] = ''

        if not self._VYATTA_present:
            # Lets get the latest hostname. It could have changed
            self.client_conn.send("\r\n")
            # print("DEBUG: Hostname is \n%s" % self._hostname)
            self.blocking_recv('#')
            # self._hostname = self.blocking_recv('#')
            # self._hostname = self._hostname.translate(None, '\r\n')
            # print("DEBUG: Hostname is \n%s" % self._hostname)

            # Let's figure out what our new prompt looks like
            self.client_conn.send("%s\r\n" % "conf t")
            self._config_hostname = self.blocking_recv("#")
            self.client_conn.send("\r\n")
            self._config_hostname = self.blocking_recv('#')
            self._config_hostname = self._config_hostname.translate(None, '\r\n')

            # At this point we should be in config mode. Let's send the commands
            # Also - the prompt can change (thanks devs). Let's ignore the prompt
            # only save the actual output.

            self._mass_data = ""
            for _command in _commands:
                self.client_conn.send("%s\r\n" % _command)
                time.sleep(0.5)
                self._temp_line = self.blocking_recv(")#")
                self._response = self._temp_line
                self._temp_data = io.BytesIO(self._response)
                self._lines = self._temp_data.readlines()

                # Let's strip out the whitespace
                for _val, _line in enumerate(self._lines):
                    _line = _line.strip()
                    _line = _line.translate(None, '\r\n')
                    if _line == '':
                        continue

                    if _command not in _line and ")#" not in _line:
                        _dict_response[_command] = _line

            self.client_conn.send("%s\r\n" % "end")
            self.blocking_recv("#")

            return _dict_response

        if self._VYATTA_present:
            # Lets get the latest hostname. It could have changed
            self.client_conn.send("\n")
            # print("DEBUG: Hostname is \n%s" % self._hostname)
            self.blocking_recv('$')
            # self._hostname = self.blocking_recv('#')
            # self._hostname = self._hostname.translate(None, '\r\n')
            # print("DEBUG: Hostname is \n%s" % self._hostname)

            # Let's figure out what our new prompt looks like
            self.client_conn.send("%s\n" % "configure")
            self._config_hostname = self.blocking_recv("#")
            self.client_conn.send("\n")
            self._config_hostname = self.blocking_recv('#')
            self._config_hostname = self._config_hostname.translate(None, '\r\n ')
            self._config_hostname = self._config_hostname.replace('[edit]', '')

            # At this point we should be in config mode. Let's send the commands
            # Also - the prompt can change (thanks devs). Let's ignore the prompt
            # only save the actual output.

            self._mass_data = ""
            for _command in _commands:
                self.client_conn.send("%s\n" % _command)
                time.sleep(0.1) # Let things breathe
                self._temp_line = self.blocking_recv(self._config_hostname)
                self._response = self._temp_line
                self._temp_data = io.BytesIO(self._response)
                self._lines = self._temp_data.readlines()
                _tmplines = ""

                # Let's strip out the whitespace
                for _val, _line in enumerate(self._lines):
                    _line = _line.strip()
                    _line = _line.translate(None, '\r\n')

                    _line = self._clean_ansi.sub('', _line)

                    if _line == '':
                        continue

                    if '[edit]' not in _line and _command not in _line and self._config_hostname not in _line:
                        _tmplines = _tmplines + _line + "\r\n"

                if _tmplines == "":
                    _dict_response[_command] = 'ok'
                else:
                    _dict_response[_command] = _tmplines

            self.client_conn.send("%s\n" % "commit")
            self.blocking_recv(self._config_hostname)

            return _dict_response

    def close(self):
        self.client.close()

    @property
    def connected(self):
        if self.client.get_transport().is_active() and \
                self.client.get_transport() is not None:

            return True
        else:
            return False

    @property
    def protocol(self):
        return self._args.get('method')
