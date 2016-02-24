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

import os
import getpass
import logging
import psutil
import copy

from helpers import cls, getpid
from optparse import OptionParser
from time import sleep

_NAP = 1
# Default for sleep
_SLEEP_DEFAULT = 600


class _setup(object):
    """This class does nothing more than instantiate the setup() class
        and provide bound copies via the get_setup() method.
        Why do this you ask? Me too. It's a Windows issue.
        Pickling the setup instance for each multiprocess goes wrong.
    """

    def __init__(self, **kwargs):
        self.setup = setup(**kwargs)
        return

    def get_setup(self):
        return copy.deepcopy(self.setup)


class setup(object):
    # This is a little unixy. Make Windows happy.
    # _pidfile = "/tmp/icx_collection.pid"
    # _log = "/tmp/clicrud.log"

    _pidfile = "clicrud_collection.pid"
    _log = "clicrud.log"

    def __init__(self, splash):
        # Entry point for __main__
        self._thread_list = []

        # PID List
        self._pid_list = []

        # Parallel mode by default
        self.parallel = True

        # Setup logging
        logging.basicConfig(filename=self._log, level=logging.DEBUG)

        # Deal with init args
        (self._options, self._args) = self.setup_options()
        self._splash = splash

        # Go and get the PID
        self.createPIDfile(self._pidfile, str(getpid()))
        logging.info("Created PID File %s" % self._pidfile)
        self._pid_list.append(os.getpid())

        # Now we deal with user facing splash screen
        if self._splash:
            self.splash_screen()

        if self._options.period is not None:
            self._SLEEP = int(self._options.period)
        else:
            self._SLEEP = _SLEEP_DEFAULT

    def createPIDfile(self, _pidfile, PIDInfo):
        try:
            _f = open(_pidfile, 'w')
            _f.write(PIDInfo)
            _f.close()
        except:
            logging.error("Could not open file for PID")

    def getpasswords(self):

        for thread in self._thread_list:

            if thread._kwargs['password'] == "":
                print "Input password for device %s: " % thread._kwargs['host']
                thread._kwargs['password'] = getpass.getpass()
                if self._splash:
                    self.splash_screen()

            if thread._kwargs['enable'] == "":
                print "Input password for device %s: " % thread._kwargs['host']
                thread._kwargs['enable'] = getpass.getpass()
                if self._splash:
                    self.splash_screen()

    def setup_options(self):
        parser = OptionParser(usage="python icx_diagnose --username=\"name\" \
                                     --hostname=\"192.0.2.1\" \
                                     --method=\"telnet|ssh\" OPTIONAL \
                                     --runonce --password",
                              version="alpha 1.0")

        parser.add_option("-t", "--timeperiod", dest="period",
                          help="Time period between data \
                                collection in seconds",
                          metavar="Time", type="string")

        parser.add_option("-c", "--continuous", dest="loop",
                          help="If continous is set, then this library \
                                will execute in a loop governed by -t",
                          metavar="Continous", action="store_true")

        return parser.parse_args()

    def splash_screen(self):
        cls()
        print 80*"*"
        print "\t\tB R O C A D E\t\t C L I C R U D\t\tv0.1"
        print 80*"*"
        print "Please hit CTRL+C to terminate\n"

    def splash_prepare_to_launch(self):
        if not self.parallel:
            print "In non-parallel mode"
        print "\n------Progress------\n"

    def start_processes(self):
        for _idx, _t in enumerate(self._thread_list):
            _t.start()
            self._pid_list.append(_t.getPID())
            logging.info("Run thread %s with pid %s with kwargs %s" %
                         (_idx+1, _t.getPID(), _t))
            # Uncomment out if we want to block the main thread until
            # at least one pass has completed.
            if not self.parallel:
                _t.ranonce

    def run_processes(self):
        for _idx, _t in enumerate(self._thread_list):
            if _t.is_alive():
                _t.run()
                self._pid_list.append(_t.getPID())
                logging.info("Run thread %s with pid %s with kwargs %s" %
                             (_idx+1, _t.getPID(), _t))

    def main_loop(self, continuous):
        main_loop = True
        free_to_write = True
        _all_ran_once = False
        while main_loop:
            if self.parallel is False:
                try:

                    _SLEEP_ACCUM = 0
                    if continuous:
                        while _SLEEP_ACCUM < self._SLEEP:
                            sleep(_NAP)
                            _SLEEP_ACCUM += _NAP
                    # this is the loop that creates the threads and
                    # joins them together
                    for _idx, _t in enumerate(self._thread_list):
                        # print "Run thread %s with pid %s with kwargs %s" %
                        #      (_idx+1, _t.getPID(), _t)
                        _t.run()
                        while not _t.ranonce:
                            sleep(0.2)

                except KeyboardInterrupt:
                    print "\b\nCtrl C - Stopping server"
                    print "Stopping jobs %s..." % (self._pid_list)
                    # for p in self._thread_list:
                    #    p._t.terminate()
                    # sys.exit(1)
                    main_loop = False

            # PARALLEL OPERATION HERE
            # IF parallel = True
            if self.parallel is True:
                try:

                    # We only want to star the main timing cycle once the job
                    # has run at least once. Else we face overlapping jobs

                    if not _all_ran_once:
                        for _idx, _t in enumerate(self._thread_list):
                            # Wait until we've got our True signal from ranonce
                            _t.ranonce

                        _all_ran_once = True

                    # It is expected that we need to sleep post the run once
                    _SLEEP_ACCUM = 0
                    if continuous:
                        while _SLEEP_ACCUM < self._SLEEP:
                            sleep(_NAP)
                            _SLEEP_ACCUM += _NAP
                    # this is the loop that creates the threads and joins
                    # them together
                    for _idx, _t in enumerate(self._thread_list):
                        # print "Run thread %s with pid %s with kwargs %s"
                        #        % (_idx+1, _t.getPID(), _t)
                        _t.run()

                except KeyboardInterrupt:
                    print "\b\nCtrl C - Stopping server"
                    print "Stopping jobs %s..." % (self._pid_list)
                    # for p in self._thread_list:
                    #    p._t.terminate()
                    # sys.exit(1)
                    main_loop = False

    def start(self, *args):
        for arg in args:
            self._thread_list.append(arg)

        # We only need to do this if we're running a script
        self.getpasswords()

        if not self._options.loop:
            self.splash_prepare_to_launch()
            # Start the multi-processing off!
            self.start_processes()

        # If you only want to use library programming, then don't worry
        # about this.
        if self._options.loop:
            print "Entering periodic refresh loop of : %d seconds" \
                   % (self._SLEEP)
            self.splash_prepare_to_launch()
            # Start the multi-processing off!
            self.start_processes()
            self.main_loop(True)

    def stop(self):
        StopCheck = True
        NumProcs = len(self._thread_list)
        ProcsStopped = 0
        while StopCheck:
            for _idx, _t in enumerate(self._thread_list):
                _qmsg = _t.finq
                if _qmsg == 'completed_run':
                    _t.stop()
                    ProcsStopped += 1
                    logging.info("Stopped thread %s with pid %s with kwargs \
                                 %s" % (_idx+1, _t.getPID(), _t))
                if _qmsg == 'error':
                    _t.stop()
                    logging.info("Error on thread %s with pid %s with kwargs \
                                 %s" % (_idx+1, _t.getPID(), _t))
                    StopCheck = False

                if NumProcs == ProcsStopped:
                    StopCheck = False
            sleep(0.5)

        print "\n\nGoodbye..."
        for pid in self._pid_list:
            p = psutil.Process(pid)
            p.terminate()
        exit(0)
