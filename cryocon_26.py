from Doberman import LANDevice, utils
import re  # EVERYBODY STAND BACK xkcd.com/208


class cryocon_26(LANDevice):
    """
    Cryogenic controller
    """
    eol = b'\n'
    _msg_end = ';\n'
    commands = {  # these are not case sensitive
        'identify': '*idn?',
        'getTempA': 'input? a:units k',
        'getTempB': 'input? b:units k',
        'getTempC': 'input? c:units k',
        'getTempD': 'input? d:units k',
        'getSP1': 'loop 1:setpt?',
        'getSP2': 'loop 2:setpt?',
        'getLp1Pwr': 'loop 1:htrread?',
        'getLp2Pwr': 'loop 2:htrread?',
        'setTempAUnits': 'input a:units k',
        'setTempBUnits': 'input b:units k',
        'setSP': 'loop {ch}:setpt {value}',
    }
    value_pattern = re.compile(f'(?P<value>{utils.number_regex})'.encode())

    def process_one_value(self, name, data):
        data = data.replace(b'OFF', b'0')
        data = data.replace(b'ON', b'1')
        return float(self.value_pattern.search(data).group('value'))

    def execute_command(self, quantity, value):
        if quantity == 'setpoint':
            return self.commands['setSP'].format(ch=1, value=value)
        if quantity == 'control_loop':
            if value == '0':
                return 'stop'
            elif value == '1':
                return 'control'
