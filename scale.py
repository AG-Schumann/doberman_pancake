from Doberman import LANDevice, utils
import re

class scale(LANDevice):
    """
    Scale for nitrogen dewar in pancake.
    """

    def set_parameters(self):
        self.value_pattern = re.compile((f'(?P<value>{utils.number_regex})kg').encode())



