import Doberman
import re


class CommandDict(dict):
    def __missing__(self, key):
        return key

class caen_sy5527(Doberman.LANSensor):
    """
    Driver for the CAEN high-voltage crate
    """
    def SetParameters(self):
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
        self.command_pattern = re.compile('(?P<action>get|set) ch(?P<ch>[1-9]?[0-9]) sl3 (?P<task>rup|rdn|tripi|tript|setp|stat|vset|imon|vmon|pon|pdn)(?: (?P<value>%s))?' % Doberman.utils.number_regex)
        self.reading_pattern = re.compile(('OK;(?P<value>%s)\r\n' % Doberman.utils.number_regex).encode())

    def ProcessOneReading(self, name, data):
        if 'pon' in name or 'pdn' in name or 'pw' in name or 'stat' in name:
            return int(self.reading_pattern.search(data).group('value'))
        return float(self.reading_pattern.search(data).group('value'))
