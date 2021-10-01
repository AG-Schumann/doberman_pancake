from Doberman import LANSensor, utils
import re  # EVERYBODY STAND BACK xkcd.com/208


class cryocon_26(LANSensor):
    """
    Cryogenic controller
    """
    def set_parameters(self):
        self._msg_end = ';\n'
        self.commands = {  # these are not case sensitive
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
        self.reading_pattern = re.compile(f'(?P<value>{utils.number_regex})'.encode())
        self.command_pattern = re.compile(f'set setpoint ({utils.number_regex})')

    def execute_command(self, command):
        """
        """
        if (m := self.command_pattern.match(command)):
            return self.commands['setSP'].format(ch=1, value=float(m[1]))
