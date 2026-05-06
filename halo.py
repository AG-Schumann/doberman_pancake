from Doberman import LANDevice, utils
import re

class halo(LANDevice):
    """
    Plugin for the Tiger optics HALO+ purity monitor. Connected via Serial-ETH converter.
    Relavant command: CONC\r\n  Reply 1.23\r\n

    """
    eol = b'\r\n'
    value_pattern = re.compile(f'(?P<value>{utils.number_regex})'.encode())

