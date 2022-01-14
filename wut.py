from Doberman import LANSensor, utils
import re

class wut(LANSensor):
    """
    W&T Web-Thermometer (57708)
    """
    def set_parameters(self):
        self._msg_start = 'GET /Single'
        self.reading_pattern = re.compile(f'(?P<value>{utils.number_regex})'.encode())