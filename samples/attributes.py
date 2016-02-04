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
import logging


class _attributes(dict):
    def __init__(self):

        # This is the dictionary that is generated with the attributes
        self.devices = {}

    def get_attributes(self, **kwargs):
        """This method gets all attributes in the associated list.
           I've tried to avoid 'custom' work, but it's CLI. Tough.
           If you want to have more attributes, build it in to this method.
        """
        # Figure out how many devices in the stack and what
        _tmp = self._transport_converter(
                                    kwargs.get('transport'),
                                    kwargs.get('instance'),
                                    'show version | inc Management Module')

        # Get the count of devices
        _ndevices = len(_tmp)
        logging.info("[attributes.py] Detected stack devices %s" % _ndevices)

        # This section fills in the device type and number
        _devcount = 1
        for dev in (_tmp):
            _tmp2 = dev.strip()
            _tmp2 = _tmp2.split(" ")
            self.devices[_devcount] = {'model': _tmp2[4]}
            if _devcount < _ndevices:
                _devcount += 1

        # This section fills in the version of code
        _tmp = self._transport_converter(
                                    kwargs.get('transport'),
                                    kwargs.get('instance'),
                                    'show version | inc SW: Version')

        _devcount = 1
        for dev in (_tmp):
            _tmp2 = dev.strip()
            _tmp2 = _tmp2.split(" ")
            self.devices[_devcount].update({'version': _tmp2[2]})
            if _devcount < _ndevices:
                _devcount += 1

        logging.info("[attributes.py] Detected version of code %s" % _tmp2)

        # This section fills in the uptime per device
        _tmp = self._transport_converter(
                                    kwargs.get('transport'),
                                    kwargs.get('instance'),
                                    'show version | inc uptime')

        _devcount = 1
        for dev in (_tmp):
            _tmp2 = dev.strip()
            _tmp2 = _tmp2.split(" ")
            _tmp3 = ' '.join(_tmp2[6:])
            self.devices[_devcount].update({'uptime': _tmp3})
            if _devcount < _ndevices:
                _devcount += 1

        logging.info("[attributes.py] Detected uptime %s" % _tmp3)

        # This section fills in the hostname
        _tmp = self._transport_converter(
                                    kwargs.get('transport'),
                                    kwargs.get('instance'),
                                    'show running-config | inc hostname')

        if _tmp:
            _devcount = 1
            _tmp2 = str(_tmp)
            _tmp2 = _tmp2.strip()
            _tmp2 = _tmp2.split(" ")
            for dev in range(_ndevices):
                self.devices[_devcount].update({'hostname': _tmp2[1]})
                if _devcount < _ndevices:
                    _devcount += 1

            logging.info("[attributes.py] Detected hostname %s" % _tmp2[1])

        if not _tmp:
            self.devices[_devcount].update({'hostname': 'Not set'})
            logging.info("[attributes.py] No hostname detected")

        # This section fills in the serial
        _tmp = self._transport_converter(
                                    kwargs.get('transport'),
                                    kwargs.get('instance'),
                                    'show version | inc Serial')
        _devcount = 1
        for dev in (_tmp):
            _tmp2 = dev.strip()
            _tmp2 = _tmp2.split(" ")
            self.devices[_devcount].update({'serial': _tmp2[3]})
            if _devcount < _ndevices:
                _devcount += 1
            logging.info("[attributes.py] Detected serial number %s"
                         % _tmp2[3])

    def set_attribute(self, **kwargs):
        """This method sets and can override each attribute.
           Requires KWs:    device (integer)
                            parameter (string)
                            value (anything)
        """
        _device = kwargs.get('device')
        _parameter = kwargs.get('parameter')
        _value = kwargs.get('value')
        self.devices[_device].update({_parameter: _value})

        logging.info("[attributes.py] Manually set attribute: %s: %s",
                     _parameter, _value)

    def _transport_converter(self, transport, instance, command):
        """This method converts between SSH and Telnet.
            Ultimately abstracting away the differences between the two.
        """
        if transport is 'telnet':
            _output = instance.read(command)
            return _output

        if transport is 'ssh':
            _output = instance.read(command)
            return _output
