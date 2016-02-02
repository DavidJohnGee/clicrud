#clicrud
This Python library has been built by Brocade, specifically tuned for Brocade CLI (tested on ICX, MLX, CER_CES)

This Python Library takes a single, list or file based list of CLI commands and generates both programmatic
output as well as file based output. Output can be human readable or can be in JSON, where the key is the command
and the value is the string output of the command. Programmatic output can be a string, or a list, where each element
is a line with '\r\n' stripped out.

This library has clocked through 1200 CLI commands using Telnet in about 10 seconds. SSH is a little slower due to keying and
crypto functionality. Onboard CPUs can't handle the same data rates as un-encrypted Telnet.

This library when used in CLI Scripting mode (uses a helper class to setup a splash screen and take command line arguments) 
will provide a basic loop so the same commands can be collected over a time period in seconds.

This library will also self version. What this means is, if you choose the specific device type, the device type driver will
try and figure out the software version and load the specific class. Below are the class types available currently:

####Generic
Generic is the device class. It is possible to copy this class and 'tweak it' for other usage.


##Installation
```
pip install clicrud
```

##Usage

There are a number of ways to actually use this library. Check the samples directory for more examples.

There will be some YouTube videos to follow. Links will be posted here.

##License
clicrud is released under the APACHE 2.0 license. See ./LICENSE for more
information.
