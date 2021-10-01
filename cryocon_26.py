from Doberman import LANSensor, utils
import re  # EVERYBODY STAND BACK xkcd.com/208


class cryocon_26(LANSensor):
    """
    Cryogenic controller
    """
    accepted_commands = [
        'setpoint <channel> <value>: change the setpoint for the given channel',
        'loop stop: shut down both heaters'
    ]

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
        self.command_patterns = [
            (re.compile(rf'setpoint (?P<ch>1|2) (?P<value>{utils.number_regex})'),
             lambda x: self.commands['setSP'].format(**x.groupdict())),
        ]

    def execute_command(self, cmd):
        """
        Takes 'set setpoint value' and does something with it
        """
        if 'setpoint' in cmd:
            val = float(cmd.split(' ')[2])
            return self.commands['setSP'].format(ch=1, value=val)
