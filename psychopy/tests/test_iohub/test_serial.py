from __future__ import print_function
import time
from psychopy import core, visual
from psychopy.iohub import launchHubServer
from psychopy.iohub.devices import serial_dummy
from pymedx.core import serial_parser_ati

# Settings for serial port communication.
SERIAL_PORT = '/dev/null'
BAUDRATE = 38400

# event_parser_info dict:
#
# parser_function key value can be a str giving the module.function path,
# or it can be the actual function object to be run by the iohub process.
#
# *Important:* The function provided should be in a file that can be imported
# as a module without causing unwanted behavior on the iohub process.
# Some options:
#     1) Put the function in a file that contains only the function,
#        as is done in this example.
#     2) Ensure any script logic that will be run when the file is called by
#        a user ( i.e. python.exe filewithfunc.py ) is inside a:
#            if __name__ == '__main__':
#        condition so it is not run when the file is only imported.

event_parser_info = dict(parser_function="serial_dummy.custom_dummy_parser")
# configure iohub
exp_code = 'serial_demo'
sess_code = 'S_{0}'.format(int(time.mktime(time.localtime())))
iohubkwargs = {'experiment_code': exp_code,
               'session_code': sess_code,
               'serial_dummy.SerialDummy': dict(
                   name='serial',
                   port=SERIAL_PORT,
                   baud=BAUDRATE,
                   parity='NONE',
                   bytesize=8,
                   event_parser=event_parser_info)}

# start the iohub server and set up display and PST box devices
io = launchHubServer(**iohubkwargs)
serial_device = io.devices.serial
keyboard = io.devices.keyboard

# Start collecting data from the PST box in the background.
serial_device.enableEventReporting(True)
