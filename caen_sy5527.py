from Doberman import  CheapSocketDevice, utils
import re


class caen_sy5527(CheapSocketDevice):
    """
    Driver for the CAEN high-voltage crate
    """
    def set_parameters(self):
        self.channel_status = [
                'on',
                'ramp_up',
                'ramp_down',
                'overcurrent',
                'overvoltage',
                'undervoltage',
                'external_trip',
                'max_v',
                'external_disable',
                'internal_error',
                'calibration_error',
                'unplugged',
                ]
        self.command_patterns = [(re.compile('set ch(?P<ch>[1-9]?[0-9]) sl3 (?P<task>rup|rdn|tripi|tript|setp|vset|pon|pdn|pw) (?P<value>%s)' % utils.number_regex),
            lambda m : m.group(0))]

        self.value_pattern = re.compile(f'OK;(?P<value>(?:{utils.number_regex},)*{utils.number_regex})\r\n'.encode())

    def process_one_reading(self, name, data):
        self.logger.debug(data)
        m = self.value_pattern.search(data)
        return list(map(float, m.group('value').decode().split(',')))[0]
