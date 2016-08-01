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

from clicrud.device.generic.ver.base import telnet as baseTelnet
from clicrud.device.generic.ver.base import ssh as baseSSH


class generic(object):

    def __init__(self, **kwargs):

        METHOD_ATTRS = ['telnet', 'ssh']
        _args = kwargs
        if _args.get('method') == 'telnet' and \
                _args.get('method') in METHOD_ATTRS:

            self._transport = baseTelnet(**_args)

        if _args.get('method') == 'ssh' and \
                _args.get('method') in METHOD_ATTRS:

            self._transport = baseSSH(**_args)

    @property
    def connected(self):
        if self._transport.connected:
            return True

    def read(self, command, **kwargs):
        _args = kwargs
        return self._transport.read(command, **_args)

    def configure(self, commands, **kwargs):
        _args = kwargs
        return self._transport.configure(commands, **_args)

    @property
    def protocol(self):
        return self._transport.protocol

    def close(self):
        self._transport.close()

    @property
    def hostname(self):
        return self._transport.hostname

    @property
    def err(self):
        return self._transport._error
