from Doberman import LANSensor, utils
import re

class scale_pancake(LANSensor):
    """
    Scale for nitrogen dewar in pancake.
    """

    def set_parameters(self):
        self.reading_pattern = re.compile((f'(?P<value>{utils.number_regex})kg').encode())



