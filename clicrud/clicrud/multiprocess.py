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

from multiprocessing import Process, Queue
import logging
import sys


class buildThread(object):

    def __init__(self, target, clicrud, **kwargs):
        self._kwargs = kwargs
        self._kwargs['setup'] = clicrud
        self._q = Queue()
        self._finq = Queue()
        self._ranonceq = Queue()
        self._target = target
        self._clicrud = clicrud
        self._ranonce = False

    def __str__(self):
        return str(self._kwargs)

    def output(self):
        return self._q.get()

    def prettyOutput(self):
        _output = self._q.get()
        _return = ""
        for k, v in _output.iteritems():
            _return += "\n\nCOMMAND: " + k + "--------------------\r\n\n"
            _return += v + "\n"
        return _return

    @property
    def finq(self):
        return self._finq.get(timeout=600)

    def start(self):
        self._t = Process(target=self._target,
                          args=(self._q,
                                self._finq,
                                self._ranonceq),
                          kwargs=self._kwargs,)

        self._t.start()

    def stop(self):
        self._t.terminate()

    def join(self):
        self._t.join()

    def run(self):
        self._t.run()

    @property
    def ranonce(self):
        return self._ranonceq.get(timeout=1800)

    def getPID(self):
        return self._t.pid

    def test(self):
        return self._t._bootstrap()
