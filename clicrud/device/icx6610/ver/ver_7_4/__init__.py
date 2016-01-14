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

from clicrud.device.icx6610.ver.base import telnet as telnetBase
from clicrud.device.icx6610.ver.base import ssh as sshBase

# If any attribute gathering methods need to be changed, import the correct
# attribute version here and put the right code in to 'override'


class telnet(telnetBase):
    """This class extends the base version and calls attributes."""

    def __init__(self):
        """First call the inherited init() and then get attribs."""
        super(telnet, self).__init__(self)
        super(telnet, self).get_attributes()


class ssh(sshBase):
    """This class extends the base version and calls attributes."""

    def __init__(self):
        """First call the inherited init() and then get attribs."""
        super(ssh, self).__init__(self)
        super(ssh, self).get_attributes()
