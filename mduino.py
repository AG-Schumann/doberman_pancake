import Doberman


class mduino(Doberman.CheapSocketDevice):
    """
    IndustrialShield mduino. Use in conjunction with the .ino code
    """
    def set_parameters(self):
        self._msg_start = '*'
        self._msg_end = '\r\n'
        # reading command looks like 'RI0.12'
        # write command looks like 'WQ1.2 <value>'
        # <rw><type><zone>.<channel>[ <value>]
        # Q = digital out (incl pwm)
        # A = analog out
        # I = analog in
        # i = digital in
        # R = relay out

    def process_one_value(self, name, data):
        # data looks like "*OK;<value>\r\n"
        # value is an integer in [0,FF] because 8 bit
        return int(data.split(b';')[1])

    def execute_command(self, quantity, value):
        # quantity looks like 'R2.8' or 'Q0.7' or something
        value = max(min(value, 0xFF), 0)
        return f'W{quantity} {value}'

