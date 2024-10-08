from Doberman import SerialDevice, utils
import re  # EVERYBODY STAND BACK xkcd.com/208
from itertools import product


class caen_n1470(SerialDevice):
    """
    Connects to the CAEN N1470. Command syntax:
    '$BD:<board number>,CMD:<MON,SET>,CH<channel>,PAR:<parameter>[,VAL:<%.2f>]\\r\\n'
    Return syntax:
    error:
    '#BD:<board number>,<error type>:ERR'
    correct:
    '#BD:<board number>,CMD:OK[,VAL:<value>[,<value>...]]'
    """
    accepted_commands = [
        '<anode|cathode|screen> <on|off>',
        '<anode|cathode|screen> <value>',
    ]

    def set_parameters(self):
        self._msg_start = '$'
        self._msg_end = '\r\n'
        self.setcommand = f'BD:{self.params["board"]},CMD:SET,' + 'CH:{ch},PAR:{par},VAL:{val}'
        self.powercommand = f'BD:{self.params["board"]},CMD:SET,' + 'CH:{ch},PAR:{par}'
        self.value_pattern = re.compile(f'OK,VAL:(?P<value>{utils.number_regex})'.encode())

    def execute_command(self, quantity, value):
        if quantity in self.params['channel_map']:
            if value in ['on', 'off']:
                return self.powercommand.format(ch=self.params['channel_map'][quantity], par=value.upper())
            else:
                return self.setcommand.format(ch=self.params['channel_map'][quantity], par='VSET', val=value)

