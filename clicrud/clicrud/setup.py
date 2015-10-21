#!/usr/bin/python

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

import os, sys, getpass, logging, psutil

from multiprocessing import Queue
from multiprocess import buildThread
from helpers import cls, getpid
from optparse import OptionParser
from time import sleep

_NAP = 1
# Default for sleep
_SLEEP_DEFAULT = 3

class setup(object):
    
    _pidfile = "/tmp/icx_collection.pid"
    _log = "/tmp/clicrud.log"
    
    def __init__(self, splash, getpasswords):
        # Entry point for __main__
        self._thread_list = []
        
        # PID List
        self._pid_list = []
        
        # Setup logging

        logging.basicConfig(filename=self._log,level=logging.DEBUG)
        
        # Deal with init args
        (self._options, self._args) = self.setup_options()
        self._splash = splash
        self._getpasswords = getpasswords
            # Location of PID file

        # Go and get the PID
        self.createPIDfile(self._pidfile, str(getpid()))
        logging.info("Created PID File %s" % self._pidfile)
        self._pid_list.append(os.getpid())
        
        # Now we deal with user facing splash screen    
        if self._splash:
            self.splash_screen()
        
        # From here we need to remove up until (prepare to launch)
        # and put in to (getpasswords())
        #if self._options.password == None and self._getpasswords:
        #    print "Input password for device: "
        #    self._options.password = getpass.getpass()
        #    if self._splash:
        #        self.splash_screen()
        #if self._options.enable == None and self._getpasswords:
        #    print "Input enable password for device: "
        #    self._options.enable = getpass.getpass()
        #    if self._splash:
        #        self.splash_screen()
        # If setup is complete, prepare to launch!  
        if self._splash:
            self.splash_prepare_to_launch()

            
    def createPIDfile(self, _pidfile, PIDInfo):
        try:
            _f = open(_pidfile, 'w')   
            _f.write(PIDInfo)   
            _f.close()
        except: 
            logging.error("Could not open file for PID")
            
    def getpasswords(self):
        
        for thread in self._thread_list:
            try:
                if thread._kwargs['password'] != None:
                    self._options.password = thread._kwargs['password']

            except:
                pass
            
            try:
                if thread._kwargs['enable'] != None:
                    self._options.enable = thread._kwargs['enable']
            except:
                pass
            
            if self._options.password == None and self._getpasswords:
                print "Input password for device: "
                self._options.password = getpass.getpass()
                if self._splash:
                    self.splash_screen()
            if self._options.enable == None and self._getpasswords:
                print "Input enable password for device: "
                self._options.enable = getpass.getpass()
                if self._splash:
                    self.splash_screen()

    
    def setup_options(self):
        parser = OptionParser(usage="python icx_diagnose --username=\"name\" --hostname=\"192.0.2.1\" --method=\"telnet|ssh\" OPTIONAL --runonce --password", version="alpha 1.0")
        parser.add_option("-n", "--node", dest="host", help="IP Address of ICX", metavar="Host IP", type="string")
        parser.add_option("-u", "--username", dest="username", help="Username of account with admin rights on ICX", metavar="Username", type="string")
        parser.add_option("-p", "--password", dest="password", help="Password for access to user account", metavar="Pass", type="string")
        parser.add_option("-t", "--timeperiod", dest="period", help="Time period between data collection in seconds", metavar="Time", type="string")
        parser.add_option("-e", "--enable", dest="enable", help="Enter the enable password for the device", metavar="Enable", type="string")
        parser.add_option("-c", "--continuous", dest="loop", help="If continous is set, then this library will execute in a loop governed by -t", metavar="Continous", action="store_true")
        return parser.parse_args()    
    
    def splash_screen(self):
        cls()
        print 80*"*"
        print "\t\tB R O C A D E\t\t C L I C R U D\t\tv0.1"
        print 80*"*"
        print "Please hit CTRL+C to terminate\n"
    
    def splash_prepare_to_launch(self):
        print "\n------Progress------\n"
    
    def start_processes(self):
        for _idx, _t in enumerate(self._thread_list):
            _t.start()
            self._pid_list.append(_t.getPID())
            logging.info("Run thread %s with pid %s with kwargs %s" % (_idx+1, _t.getPID(), _t))
            # Uncomment out if we want to block the main thread until at least one pass has completed.
            # _t.join()
    
    def run_processes(self):
        for _idx, _t in enumerate(self._thread_list):
            if _t.is_alive():
                _t.run()
                self._pid_list.append(_t.getPID())
                logging.info("Run thread %s with pid %s with kwargs %s" % (_idx+1, _t.getPID(), _t))
    
    def main_loop(self, continuous):
        if not self._options.period == None:
            _SLEEP =int(self._options.period)
        else:
            _SLEEP = _SLEEP_DEFAULT
        
        main_loop = True
        free_to_write = True
        while main_loop:
            try:
                # It is expected that we need to sleep post the run once
                _SLEEP_ACCUM = 0
                if continuous:
                    while _SLEEP_ACCUM < _SLEEP:
                        sleep(_NAP)
                        _SLEEP_ACCUM += _NAP
                # this is the loop that creates the threads and joins them together
                for _idx, _t in enumerate(self._thread_list):
                    #print "Run thread %s with pid %s with kwargs %s" % (_idx+1, _t.getPID(), _t)
                    _t.run()
    
                
            except KeyboardInterrupt:
                print "Ctrl C - Stopping server"
                print "Stopping jobs %s..." % (self._pid_list)
                #for p in self._thread_list:
                #    p._t.terminate()
                #sys.exit(1)
                main_loop = False
                
    def start(self, *args):
        for arg in args:
            self._thread_list.append(arg)       
            
        # We only need to do this if we're running a script
        self.getpasswords()
        
        # Start the multi-processing off!
        self.start_processes()
        
        ## If you only want to use library programming, then don't worry about this.
        if self._options.loop:
            print "Entering loop state"
            self.main_loop(True)
        
                
    def stop(self):
        StopCheck = True
        NumProcs = len(self._thread_list)
        ProcsStopped = 0
        while StopCheck:
            for _idx, _t in enumerate(self._thread_list):
                if _t.finq == 'completed_run':
                    _t.stop()
                    ProcsStopped += 1
                    logging.info("Stopped thread %s with pid %s with kwargs %s" % (_idx+1, _t.getPID(), _t))
            sleep(0.5)
            if NumProcs == ProcsStopped:
                StopCheck = False
        print "\n\nGoodbye..."
        for pid in self._pid_list:
            p = psutil.Process(pid)
            p.terminate()
        exit(0)