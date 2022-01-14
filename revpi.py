from Doberman import Sensor, utils
import re


class revpi(Sensor):
    """
    Class for RevolutionPi sensors
    """

    def set_parameters(self):
        self.commands = {
            'readInput': 'r,{module},i,{ch}',
            'readOutput': 'r,{module},o,{ch}',
            'readRTD': 'r,{module},r,{ch}',
            'writeOutput': 'w,{module},o,{ch},{value}'
        }
        # self.reading_pattern = re.compile(('(?P<value>\d+)').encode())
        self.command_patterns = [
            (re.compile(r'write module (?P<module>\d+) output (?P<ch>1|2): (?P<value>\d{1,5})'),
             lambda x: self.commands['writeOutput'].format(**x.groupdict())),
        ]

    def execute_command(self, command):
        # command looks like "set <target> <value>"
        # this is wrapped in a try-except one call up so we don't
        # need to do it here. We rsplit with max here so "target"
        # can potentially have spaces in it and won't cause issues
        target, value = command[4:].rsplit(' ', maxsplit=1)
        if target == 'fast_cooling_valve':
            # "fast_cooling_valve open" or something
            module = 3
            ch = 13
            value = 1 if value == 'open' else 0
        return self.commands['writeOutput'].format(module=module, ch=output, value=value)

    def send_recv(self, message):
        self.bytes_per_module = 89
        self.bytes_per_channel = 2
        self.offset_by_type = {
            'i': 9,
            'o': 29,
            'r': 21
        }
        ret = {'retcode': 0, 'data': None}
        msg = message.split(',')  # msg = [<r|w>, <module>, <i|o|r>, <channel>, <value>]
        try:
            with open('/dev/piControl0', 'wb+', 0) as f:
                try:
                    f.seek(int(msg[1]) * self.bytes_per_module + int(msg[3]) * self.bytes_per_channel +
                           self.offset_by_type[msg[2]])
                except KeyError:
                    self.logger.error(f"Message Contains invalid type {msg[2]}. Allowed types: 'i', 'o', 'r'.")
                    ret['retcode'] = -1
                    return ret
                if msg[0] == 'r':
                    ret['data'] = int.from_bytes(f.read(self.bytes_per_channel), 'little')
                elif msg[0] == 'w':
                    if int(msg[4]) > (1 << 16):
                        pass
                    f.write(int(msg[4]).to_bytes(self.bytes_per_channel, 'little'))
                else:
                    self.logger.error(f"Message starts with invalid character {msg[0]}. Allowed characters: 'r' or 'w'")
                    ret['retcode'] = -1
                return ret
        except Exception as e:
            self.logger.error("Cannot open process image: %s" % type(e))
            ret['retcode'] = -1
            return ret

    def process_one_reading(self, name, data):
        """
        Convert from current|voltage to the correct unit: A[unit] = <multiplier> * (A[uA|mV] + <offset>)
        """
        multiplier = 1
        offset = 0
        try:
            multiplier = self.conversion[name]['multiplier']
        except Exception as e:
            self.logger.debug(f'Didn\'t find conversion values for {name} in the DB: {e}. Multiplier set to 1')
        try:
            offset = self.conversion[name]['offset']
        except Exception as e:
            self.logger.debug(f'Didn\'t find conversion values for {name} in the DB: {e}. Offset set to 0')
        ret = multiplier * (float(data) + offset)
        # to get rid of individual faulty temperature measurements (data = 63536)
        if name.startswith('temp'):
            if ret > 500:
                return
        return ret
