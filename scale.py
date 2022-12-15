from Doberman import LANDevice, utils
import re

class scale(LANDevice):
    """
    Scale for nitrogen dewar in pancake.
    """

    value_pattern = re.compile((f'(?P<value>{utils.number_regex})kg').encode())
    eol = b'\r\x03'

