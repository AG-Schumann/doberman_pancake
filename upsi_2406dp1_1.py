from Doberman import SerialSensor, utils
import re

class upsi_2406dp1_1(SerialSensor):
 
    """
    Bicker uninteruptable power supply (UPS)
    """

    def set_parameters(self):
        self._msg_start = '\x01\x03\x01'
        self._msg_end = '\x04'

    def process_one_reading(self, name, data):
        if 'i_bat' in name:
            return int.from_bytes(data[4:-1], 'little', signed=True)
        return int.from_bytes(data[4:-1], 'little')
