#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ioHub
.. file: ioHub/devices/serial/__init__.py

Copyright (C) 2012-2014 iSolver Software Solutions
Distributed under the terms of the GNU General Public License (GPL version 3 or any later version).

.. moduleauthor:: Sol Simpson <sol@isolver-software.com> + contributors, please see credits section of documentation.
.. fileauthor:: Sol Simpson <sol@isolver-software.com>
"""

from ..serial import Serial, SerialInputEvent, SerialByteChangeEvent
import multiprocessing
import time
from psychopy.iohub import print2err


class SerialDummy(Serial):

    def __init__(self, *args, **kwargs):
        self._input_buffer = multiprocessing.Queue()
        self._output_buffer = multiprocessing.Queue()
        self.worker = None
        Serial.__init__(self, *args, **kwargs)

    #def setConnectionState(self, enable):
    #    return enable

    def _connectSerial(self):
        self.worker = multiprocessing.Process(
            target=self.dummy_worker,
            args=(self._input_buffer, self._output_buffer)
        )
        self.worker.start()
        self._serial = True

    def flushInput(self):
        pass

    def flushOutput(self):
        pass

    def write(self, bytestring):
        self._input_buffer.put(bytestring)

    def read(self):
        if not self._output_buffer.empty():
            msg = self._output_buffer.get()
            return msg
        return None

    def closeSerial(self):
        print2err('closing serial')
        if self.worker and self._serial:
            self.worker.terminate()
            self.worker = None
            self._serial = None
            print2err('serial closed')
            return True
        return False

    def dummy_worker(self, input_buffer, output_buffer):
        while True:
            if not input_buffer.empty():
                msg = input_buffer.get()
                if msg != "STREAM":
                    output_buffer.put(
                        b'{}'.format(msg)
                    )
            time.sleep(.01)


def custom_dummy_parser(read_time, rx_data, parser_state, **kwargs):
    serial_events = []
    if len(rx_data):
        serial_events.append({'data': rx_data})
    return(serial_events)
