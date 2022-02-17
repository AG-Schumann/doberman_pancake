from Doberman import LANDevice, utils
import re

class wut(LANDevice):
    """
    W&T Web-Thermometer (57708)
    """
    def set_parameters(self):
        self._msg_start = 'GET /Single'
        self.value_pattern = re.compile(f'(?P<value>{utils.number_regex})'.encode())
