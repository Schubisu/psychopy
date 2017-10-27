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
from builtins import chr
from builtins import str
from builtins import range
from psychopy.iohub import OrderedDict, print2err, printExceptionDetailsToStdErr, Computer, EXP_SCRIPT_DIRECTORY
import serial
#from ..serial import Serial
from .. import Device, DeviceEvent
from ...constants import DeviceConstants, EventConstants
import numpy as N
getTime = Computer.getTime
import multiprocessing
import time
from psychopy.iohub import print2err


class SerialDummy(Device):

    _bytesizes = {
        5: serial.FIVEBITS,
        6: serial.SIXBITS,
        7: serial.SEVENBITS,
        8: serial.EIGHTBITS,
        }

    _parities = {
        'NONE': serial.PARITY_NONE,
        'EVEN': serial.PARITY_EVEN,
        'ODD': serial.PARITY_ODD,
        'MARK': serial.PARITY_MARK,
        'SPACE': serial.PARITY_SPACE
    }

    _stopbits = {
        'ONE': serial.STOPBITS_ONE,
        'ONE_AND_HALF': serial.STOPBITS_ONE_POINT_FIVE,
        'TWO': serial.STOPBITS_TWO
    }

    DEVICE_TIMEBASE_TO_SEC = 1.0
    _newDataTypes = [('port', N.str, 32), ('baud', N.str, 32),]
    EVENT_CLASS_NAMES = ['SerialInputEvent','SerialByteChangeEvent']
    DEVICE_TYPE_ID = DeviceConstants.SERIAL
    DEVICE_TYPE_STRING = "SERIAL"
    _serial_slots = [
        'port', 'baud', 'bytesize', 'parity', 'stopbits', '_serial',
        '_timeout', '_rx_buffer', '_parser_config', '_parser_state',
        '_event_count', '_byte_diff_mode', '_custom_parser',
        '_custom_parser_kwargs'
    ]
    __slots__ = [e for e in _serial_slots]

    def __init__(self, *args, **kwargs):
        Device.__init__(self, *args, **kwargs['dconfig'])
        self._input_buffer = multiprocessing.Value('s', '')
        self._output_buffer = multiprocessing.Value('s', '')
        self.worker = None

        self._serial = None
        self.port = self.getConfiguration().get('port')
        self.baud = self.getConfiguration().get('baud')
        self.bytesize = self._bytesizes[self.getConfiguration().get('bytesize')]
        self.parity = self._parities[self.getConfiguration().get('parity')]
        self.stopbits = self._stopbits[self.getConfiguration().get('stopbits')]

        self._parser_config = self.getConfiguration().get('event_parser')
        self._byte_diff_mode = None
        self._custom_parser = None
        self._custom_parser_kwargs = {}
        custom_parser_func_str = self._parser_config.get('parser_function')

        import importlib, sys
        try:
            if EXP_SCRIPT_DIRECTORY not in sys.path:
                sys.path.append(EXP_SCRIPT_DIRECTORY)
            mod_name, func_name = custom_parser_func_str.rsplit('.', 1)
            mod = importlib.import_module(mod_name)
            self._custom_parser = getattr(mod, func_name)
        except Exception:
            print2err(
                "ioHub Serial Device Error: could not load "
                "custom_parser function: ", custom_parser_func_str)
            printExceptionDetailsToStdErr()

        if self._custom_parser:
            self._custom_parser_kwargs = self._parser_config.get('parser_kwargs', {})

        self._event_count = 0
        self._timeout = None
        self._serial = None
        self.setConnectionState(True)

    def setConnectionState(self, enable):
        return enable

    def _connectSerial(self):
        self.worker = multiprocessing.process(
            target=self.dummy_worker,
            args=(self._input_buffer, self._output_buffer, )
        )
        self.worker.start()
        self._serial = True

    def flushInput(self):
        pass

    def flushOutput(self):
        pass

    def write(self, bytestring):
        self._input_buffer.append(bytestring)

    def read(self):
        msg = self._output_buffer
        self._output_buffer = ''
        return msg

    def closeSerial(self):
        if self.worker:
            self.worker.terminate()
            self.worker = None
        if self._serial:
            self._serial = False
            return True
        return False

    def dummy_worker(self, input_buffer, output_buffer):
        while True:
            if input_buffer.value:
                if input_buffer.value != "STREAM":
                    output_buffer.value.append(
                        b'found input: {}'.format(input_buffer.value)
                    )
                    input_buffer.value = b''
            time.sleep(.01)


class SerialInputEvent(DeviceEvent):
    _newDataTypes = [
            ('port', N.str, 32),
            ('data', N.str, 256)
            ]
    EVENT_TYPE_ID = EventConstants.SERIAL_INPUT
    EVENT_TYPE_STRING = 'SERIAL_INPUT'
    IOHUB_DATA_TABLE = EVENT_TYPE_STRING
    __slots__ = [e[0] for e in _newDataTypes]

    def __init__(self, *args, **kwargs):
        DeviceEvent.__init__(self, *args, **kwargs)


class SerialByteChangeEvent(DeviceEvent):
    _newDataTypes = [
            ('port', N.str, 32),
            ('prev_byte', N.uint8),
            ('current_byte', N.uint8)
            ]
    EVENT_TYPE_ID = EventConstants.SERIAL_BYTE_CHANGE
    EVENT_TYPE_STRING = 'SERIAL_BYTE_CHANGE'
    IOHUB_DATA_TABLE = EVENT_TYPE_STRING
    __slots__ = [e[0] for e in _newDataTypes]

    def __init__(self, *args, **kwargs):
        DeviceEvent.__init__(self, *args, **kwargs)


def custom_dummy_parser(read_time, rx_data, parser_state, **kwargs):
    if len(rx_data):
        print2err(rx_data)
