from __future__ import print_function
import time
from psychopy import core, visual
from psychopy.iohub import launchHubServer

# Settings for serial port communication.
SERIAL_PORT = '/dev/null'
BAUDRATE = 38400

event_parser_info = dict(parser_function="psychopy.iohub.devices.serial_dummy.custom_dummy_parser")
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

io = launchHubServer(**iohubkwargs)
keyboard = io.devices.keyboard
serial_device = io.devices.serial
serial_device.enableEventReporting(True)

io.clearEvents('all')

# Check for keyboard and serial events.
# Exit on keyboard press event.
# Print any serial events.
#
while not keyboard.getPresses():
    serial_device.write("TEST")
    for serevt in serial_device.getEvents():
        print(serevt)
    io.wait(.500)

# Stop recording events from the PST box and switch off all lamps.
serial_device.close()
serial_device.enableEventReporting(False)

# Close the window and quit the program.
io.quit()
