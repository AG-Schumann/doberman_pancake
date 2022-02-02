from Doberman import LANDevice
import re

class scale_pancake(LANDevice):
    """
    Scale for nitrogen dewar in pancake.
    """

    def set_parameters(self):
        self.reading_pattern = re.compile((f'(?P<value>{utils.number_regex})kg').encode())



