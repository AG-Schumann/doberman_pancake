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
    def SetParameters(self):
        self._msg_end = ';\n'
        self.commands = { # these are not case sensitive
                'identify' : '*idn?',
                'getTempA' : 'input? a:units k',
                'getTempB' : 'input? b:units k',
                'getTempC' : 'input? c:units k',
                'getTempD' : 'input? d:units k',
                'getSP1' : 'loop 1:setpt?',
                'getSP2' : 'loop 2:setpt?',
                'getLp1Pwr' : 'loop 1:htrread?',
                'getLp2Pwr' : 'loop 2:htrread?',
                'setTempAUnits' : 'input a:units k',
                'settempBUnits' : 'input b:units k',
                'setSP' : 'loop {ch}:setpt {value}',
                }
        self.reading_pattern = re.compile(('(?P<value>%s)' % utils.number_regex).encode())
        self.command_patterns = [
                (re.compile(r'setpoint (?P<ch>1|2) (?P<value>%s)' % utils.number_regex),
                    lambda x : self.commands['setSP'].format(**x.groupdict())),
                (re.compile('(shitshitfirezemissiles)|(loop stop)'),
                    self.FireMissiles),
                ]

    def FireMissiles(self, m):  # worth it for an entire function? Totally
        if 'missiles' in m.group(0):
            self.logger.warning('But I am leh tired...')
        return 'stop'

