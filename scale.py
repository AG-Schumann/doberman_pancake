from Doberman import SerialSensor, utils
import re

class scale(SerialSensor):
    """
    Large scale. should update to right name for pancake. but now quick implementation for XeBra.
    """

    def set_parameters(self):
        self.reading_pattern = re.compile((f'(?P<value>{utils.number_regex})kg').encode())
