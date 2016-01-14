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
from attributes import _attributes


class telnet(object):
    def __init__(self, **kwargs):
        _args = {}
        _opts = {}
        self.attributes = _attributes()
        self._error = False
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

        # PEP8 fix
        # if _args.has_key('port'):
        if "port" in _args:
            pass
        else:
            _args['port'] = 23

        # Make these global per instance
        self._args = _args
        self._temp_data = ""

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

        # Let's detect whether authentication or
        # enable modes for auth are configured
        _detect = True
        _detect_buffer = ""
        _timer = 0
        self._send_username = False
        self._send_enable = False
        try:
            while _detect:
                _detect_buffer += self.client.read_some()
                if "Name:" in _detect_buffer:
                    self._send_username = True
                    _detect = False
                    logging.info*("[icx6610/ver/base/__init__.py] Detected username in authentication sequence")
                if ">" in _detect_buffer:
                    self._send_enable = True
                    _detect = False
                    logging.info*("[icx6610/ver/base/__init__.py] Priv mode required")
                time.sleep(0.1)
                _timer += 1
                if _timer >= 30:
                    _detect = False

        except Exception, err:
            sys.stderr.write('\nERROR for host: %s - %s\n' %
                             (_args['host'], str(err)))

            logging.error('ERROR for host %s - %s\n:' % (_args['host'], err))
            self._error = True
            return

        # Now we know whether we need to send a username or enable password
        if self._send_username:
            self.client.write("%s\r" % _args['username'])
            self.client.read_until("Password:")
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
                        logging.info*("[icx6610/ver/base/__init__.py] Priv mode required")
                    if "#" in _detect_buffer:
                        self._send_enable = False
                        _detect = False
                        # Takes in to account exec banner
                        self.client.read_until("#", timeout=1)
                        # Do this to get a clean prompt
                        self.client.write("\r")
                        self._hostname = self.client.read_until("#")
                        self._hostname = self._hostname.translate(None, '\r\n')
                        self.client.write("skip\r")
                        self.client.read_until("mode")
                        self.client.read_until(self._hostname)
                        logging.info*("[icx6610/ver/base/__init__.py] Entered priv mode")
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
            self.client.write("en\r")
            try:
                while _detect:
                    _detect_buffer += self.client.read_some()
                    if "#" in _detect_buffer:
                        # Takes in to account exec banner
                        self.client.read_until("#", timeout=1)
                        # Do this to get a clean prompt
                        self.client.write("\r")
                        self._hostname = self.client.read_until("#")
                        self._hostname = self._hostname.translate(None, '\r\n')
                        _detect = False
                        logging.info*("[icx6610/ver/base/__init__.py] Entered priv mode")
                        break
                    if "Password:" in _detect_buffer:
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
                        # self.client.write("skip\r")
                        # self.client.read_until("mode")
                        # self.client.read_until(self._hostname)
                        logging.info*("[icx6610/ver/base/__init__.py] Entered priv mode")

                    time.sleep(0.1)
                    _timer += 1
                    if _timer >= 30:
                        _detect = False
                        # self.client.close()\

                if _detect is False:
                    self.client.write("skip\r")
                    self.client.read_until("mode")
                    self.client.read_until(self._hostname)

            except Exception, err:
                sys.stderr.write('\nERROR for host: %s - %s\n' %
                                 (_args['host'], str(err)))

                logging.error('ERROR for host %s - %s\n:' %
                              (_args['host'], err))

                self._error = True
                return

    def get_attributes(self):
        try:
            # Here we do the attribute stuff and pass the
            # self.client across to the routine so it can retrieve
            # useful values (nom noms)
            self.attributes.get_attributes(transport='telnet',
                                           instance=self)

        except Exception, err:
            sys.stderr.write('\nERROR for host: %s - %s\n' %
                             (_args['host'], str(err)))

            logging.error('ERROR for host %s - %s\n:' %
                          (_args['host'], err))

            self._error = True
            return

    @property
    def hostname(self):
        return self._hostname

    def read(self, command, **kwargs):
        """
        Returns a list with each entry representing one line of output,
        or a string if the kwarg 'return_type' = 'string'.
        """
        _string = ""
        _args = kwargs
        self.client.write("%s\r" % command)
        self._read_data = self.client.read_until(self._hostname)
        self._temp_data = io.BytesIO(self._read_data)
        self._lines = self._temp_data.readlines()
        return_list = []
        for line in self._lines:
            if line != '\r\n' and line != self._hostname:
                line = line.translate(None, '\r\n')
                if line != command:
                    return_list.append(line)
        # PEP8 fix
        # if _args.has_key('return_type'):
        if "return_type" in _args:
            if _args.get('return_type') == 'string':
                for line in return_list:
                    _string += line + '\n'
            return _string[:-1]
        else:
            return return_list

    def configure(self, command, **kwargs):
        """
        This configuration method inputs a command and waits until it reads
        it's configuration mode hostname.
        It also changes mode from priv to conf then back again to priv
        on exit.

        If kwarg 'save=True' is passed, then it will also commit config
        changes to memory.

        Returs nothing.
        """

        _args = kwargs
        # This allows us to change our read marker for conf mode.
        self._config_hostname = self._hostname + ' (conf)'
        # Enter configuration mode
        self.client.write("conf t\r\n" % command)
        self._read_data = self.client.read_until(self.config_hostname)
        self.client.write("%s\r\n" % command)
        self._read_data = self.client.read_until(self.config_hostname)
        # and now to return to priv mode
        self.client.write("exit\r\n" % command)
        self._read_data = self.client.read_until(self._hostname)
        # at this point, we can save if the kwarg has been passed.
        if _args.get('save') and _args.get('save') is True:
            self.client.write("write\r\n" % command)
            self._read_data = self.client.read_until(self._hostname)
        return

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
        # This is unixy code. Make Windows happy.
        # paramiko.util.log_to_file('/tmp/clicrud.log')
        paramiko.util.log_to_file('clicrud.log')
        _args = {}
        _opts = {}
        self.attributes = _attributes()
        self._error = False
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

        # Check for port value. If it doesn't exist,
        # default to 22

        # PEP8 foxq
        # if _args.has_key('port'):
        if "port" in _args:
            pass
        else:
            _args['port'] = 22

        # Make these global per instance
        self._args = _args

        self._temp_data = ""
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
            time.sleep(0.1)
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
                self.client_conn.send("skip\n")
                self.output = self.blocking_recv()

        except Exception, err:
            sys.stderr.write('\nERROR for host: %s - %s\n' %
                             (_args['host'], str(err)))

            logging.error('ERROR for host %s - %s\n:' % (_args['host'], err))
            self._error = True
            return

    def get_attributes(self):
        try:
            # Here we do the attribute stuff and pass the
            # self.client across to the routine so it can retrieve
            # useful values (nom noms)
            self.attributes.get_attributes(transport='ssh',
                                           instance=self)

        except Exception, err:
            sys.stderr.write('\nERROR for host: %s - %s\n' %
                             (_args['host'], str(err)))

            logging.error('ERROR for host %s - %s\n:' %
                          (_args['host'], err))

            self._error = True
            return

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
            self.client_conn.send(command + "\n")
            self.output = self.blocking_recv(self._hostname)
            stream = io.BytesIO(self.output)
            self.count = 0
            while self.count < 2:
                stream.readline()
                self.count += 1
            # At this point, we're to the top of the stream and beyond
            # the hostname and \r\n\r\n mess

            _lines = stream.readlines()
            for line in _lines:
                if line != '\r\n' and line != self._hostname:
                    line = line.translate(None, '\r\n')
                    if line != command:
                        _returnlist.append(line)
            # PEP8 fix
            # if _args.has_key('return_type'):
            if "return_type" in _args:
                if _args.get('return_type') == 'string':
                    for line in _returnlist:
                        _string += line + '\n'
                return _string[:-1]
            else:
                return _returnlist

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
