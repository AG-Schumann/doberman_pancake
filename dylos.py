from Doberman import LANDevice, utils
import re

class dylos(LANDevice):
    """
    Plugin for the DYLOS DC1100 Air Quality Monitor. Connected via Serial-ETH converter.

    The device sends a value out every minute disregarding and received data.
    Format: b'<small>,<large>\r\n', where <small> (<large>) is the particle concentration 'in approximately .01 cubic
    foot of sampled air above 1µm (5µm) size, respectively.


    """
    eol = b'\r\n'
    msg_wait = 60

    def process_one_value(self, name=None, data=None):
        """
        Takes the raw data as returned by send_recv and parses
        it for the float. Only for the scales.
        """
        small, large = data.split(',')

        # let's convert to particles/m^3 already here
        conv = 0.01/0.3048**3  # 0.01/foot^3 to 1/m^3
        small = int(small) * conv
        large = int(large) * conv
        return [small, large]
