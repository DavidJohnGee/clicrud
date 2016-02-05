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

from clicrud.device.generic import generic
from jinja2 import Environment, FileSystemLoader
from clicrud.clicrud.templatehelpers import return_config_list_from_template

# Import variables from the variables.py file
from variables import vdx1

# Setup the template loading system
templateLoader = FileSystemLoader(searchpath="./templates")
env = Environment(loader=templateLoader)

# Load the templates
template = env.get_template('harti.j2')

# Render the template and return the list
_config_list = return_config_list_from_template(
    template.render(ve1=vdx1.ve1, ve2=vdx1.ve2, ve3=vdx1.ve3))


# transport = generic(host="10.18.254.43", username="admin", enable="Passw0rd",
#                    method="telnet", password="Passw0rd")


# print "===show version"
# print transport.read("show version", return_type="string")


# transport.close()
