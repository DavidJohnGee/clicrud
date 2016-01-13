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

from clicrud.device.icx6610.ver.base import telnet as baseTelnet
from clicrud.device.icx6610.ver.base import ssh as baseSSH
import clicrud.device.icx6610.ver.ver_7_4
import clicrud.device.icx6610.ver.ver_8_0


class icx6610(object):

    def __init__(self, **kwargs):
        METHODS = {
            '0': {
                'telnet': baseTelnet,
                'ssh': baseSSH,
                },
            '7.4': {
                'telnet': clicrud.device.icx6610.ver.ver_7_4.telnet,
                'ssh': clicrud.device.icx6610.ver.ver_7_4.ssh,
                },
            '8.0': {
                'telnet': clicrud.device.icx6610.ver.ver_8_0.telnet,
                'ssh': clicrud.device.icx6610.ver.ver_8_0.ssh,
                },
            }

        METHOD_ATTRS = ['telnet', 'ssh']

        self._device_version = '0'

        _args = kwargs

        if _args.get('method') == 'telnet' and\
                _args.get('method') in METHOD_ATTRS:

            transport = baseTelnet(**_args)
            if not transport._error:

                _ver = transport.read("show version | inc SW")
                for version in METHODS:
                    if any(version in ls for ls in _ver):
                        self._device_version = version
                transport.close()

        if _args.get('method') == 'ssh' and _args.get('method') \
                in METHOD_ATTRS:

            transport = baseSSH(**_args)
            if not transport._error:
                _ver = transport.read("show version | inc SW")
                for version in METHODS:
                    if any(version in ls for ls in _ver):
                        self._device_version = version
                transport.close()

        try:
            if not transport._error:
                self._transport = METHODS[self._device_version][
                                      _args.get('method')](**_args)
            else:
                self._transport = None

        except Exception, err:
            print "This might not be an ICX6110. Issue detecting and provisioning version."
            exit(1)

    @property
    def connected(self):
        if self._transport.connected:
            return True

    def read(self, command, **kwargs):
        _args = kwargs
        return self._transport.read(command, **_args)

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
        # PEP8 fix
        if self._transport is None:
            return True
        else:
            return self._transport._error


    @property
    def attributes(self):
        return self._transport.attributes.devices
