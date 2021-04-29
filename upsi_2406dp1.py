from Doberman import SerialSensor, utils
import re

class upsi_2406DP1(SerialSensor):
 
    """
    Bicker uninteruptable power supply (UPS)
    """

    def set_parameters(self):
        self._msg_start = '\x01'
        self._msg_end = '\x04'

    def process_one_reading(self, name, data):

        return int.from_bytes(data[4:-1], 'little')
