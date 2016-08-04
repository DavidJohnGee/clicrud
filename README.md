#clicrud
This Python library has been built by Brocade, specifically tuned for Brocade CLI (tested on ICX, MLX, CER_CES)

This Python Library takes a single, list or file based list of CLI commands and generates both programmatic
output as well as file based output. Output can be human readable or can be in JSON, where the key is the command
and the value is the string output of the command. Programmatic output can be a string, or a list, where each element
is a line with '\r\n' stripped out.

The newer 'configure' method on the generic class, allows users to insert configuration commands in blocks. It is stanza specific, so what this means is, if you configure a VLAN and know the configuration mode changes, then the next command in the list should be the tagging/untagging etc. When you invoke a new configure call, the block and state machine is reset. The object returned from this is a dictionary, with the key being the command and the value being possible returned values (sometimes there may be none!)

This library has clocked through 1200 CLI commands using Telnet in about 10 seconds. SSH is a little slower due to keying and
crypto functionality. Onboard CPUs can't handle the same data rates as un-encrypted Telnet.

This library when used in CLI Scripting mode (uses a helper class to setup a splash screen and take command line arguments) 
will provide a basic loop so the same commands can be collected over a time period in seconds.

####Generic
Generic is the device class. It is possible to copy this class and 'tweak it' for other usage.

####Attributes
Device attributes collected via a dictionary are arbitrary and not related per device.
They are entirely customisable, so have fun!

In order to use the attributes, create a copy of the attribute class in the same directory as your code. As long as you follow the pythonic example in the examples directory, you're good to go.

##Installation
```
pip install clicrud
```

##Usage

There are a number of ways to actually use this library. Check the samples directory for more examples.

There will be some YouTube videos to follow. Links will be posted here.

The test script below uses the 'library' aspect of CLICRUD. This means you can talk CLI easily to MLX, ICX and VDX devices without worrying about authentication steps or stages. Feed the information in and if the authentication sequence needs the information, it will be consumed. Therefore a device without any authentication can have empty fields. For automation consistency, please enter the fields.

```Python
from clicrud.device.generic import generic

MLX = "x.x.x.x"
ICX = "y.y.y.y"
VDX = "z.z.z.z"

transport = generic(host=VDX, username="admin", enable="password",
                    method="ssh", password="password")

print "\r\n===Show VLAN brief:"
print transport.read("show vlan brief", return_type="string")


print "===Configuration data and feedback:"
print transport.configure(["no protocol vrrp"])


print "\r\n===Show interface:"
print transport.read("show interface", return_type="string")



# print transport.protocol
# print transport.connected
transport.close()
```
##License
CLICRUD is released under the APACHE 2.0 license. See ./LICENSE for more
information.
