from __future__ import print_function

from builtins import object
import pytest
import time
from psychopy.iohub import launchHubServer


class TestSerial(object):
    @classmethod
    def setup(cls):
        event_parser_info = {
            'parser_function': "psychopy.iohub.devices.serial_dummy.custom_dummy_parser"
        }
        cls.iohubkwargs = {
            'experiment_code': 'serial_dummy_test',
            'session_code': 'serial_dummy_test',
            'serial_dummy.SerialDummy': dict(
                name='serial_dummy',
                port='/dev/null',
                baud=38400,
                parity='NONE',
                bytesize=8,
                event_parser=event_parser_info)}

    def test_launch_quit_hub_server(self):
        import psychopy
        io = launchHubServer(**self.iohubkwargs)
        assert isinstance(io, psychopy.iohub.client.ioHubConnection)
        io.quit()

    def test_serial_device(self):
        io = launchHubServer(**self.iohubkwargs)
        serial_device = io.devices.serial_dummy
        assert serial_device.getName() == 'serial_dummy', 'incorrect device name'
        assert serial_device.isConnected() is True, 'device is not connected'
        assert serial_device.isReportingEvents() is False, 'device reporting events'
        serial_device.close()
        io.quit()

    def test_event_reporting(self):
        io = launchHubServer(**self.iohubkwargs)
        serial_device = io.devices.serial_dummy
        serial_device.enableEventReporting(True)
        io.clearEvents('all')
        assert serial_device.isReportingEvents() is True, 'device not reporting events'

        serial_device.write("TEST")
        time.sleep(.1)
        events = serial_device.getEvents()
        assert len(events) == 1, 'incorrect number of events'

        event = events[0]
        assert event.data == "TEST", 'incorrect response'
        assert event.port == '/dev/null', 'incorrect port'
        assert event.time - event.device_time < 0.001, 'time mismatch'
        assert event.time - event.logged_time < 0.001, 'time mismatch'
        #assert event.time < 0.1, 'time mismatch'
        serial_device.close()
        io.quit()

    def test_close_serial(self):
        io = launchHubServer(**self.iohubkwargs)
        serial_device = io.devices.serial_dummy
        serial_device.close()
        serial_device.enableEventReporting(False)
        assert serial_device.isConnected() is False
        assert serial_device.isReportingEvents() is False
        io.quit()


if __name__ == "__main__":
    pytest.main()
