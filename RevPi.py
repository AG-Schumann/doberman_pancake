from Doberman import Sensor, utils
import re

class RevPi(Sensor):
    """
    Class for RevolutionPi sensors
    """
    
    def SendRecv(self, message):
        self.bytes_per_module = 89
        self.bytes_per_channel = 2
        self.offset_by_type = {
            'i': 9,
            'o': 29,
            'r': 21
            }
        ret = {'retcode' : 0, 'data' : None}        
        msg = message.split(',') # msg = [<r|w>, <module>, <i|o|r>, <channel>, <value>]
        try:
            with open('/dev/piControl0', 'wb+', 0) as f:
                try:
                    f.seek(int(msg[1]) * self.bytes_per_module + int(msg[3]) * self.bytes_per_channel +
                            self.offset_by_type[msg[2]])
                except KeyError:
                    self.logger.error(
                            "Message Contains invalid type %s. Allowed types: 'i', 'o', 'r'. " % msg[2])
                    ret['retcode'] = -2
                if msg[0] == 'r':
                    ret['data'] = int.from_bytes(f.read(self.bytes_per_channel), 'little')
                    self.logger.debug("Sent %s got %s" % (message, ret['data']))
                elif msg[0] == 'w':
                    if int(msg[4]) > (1 << 16):
                        pass
                    f.write(int(msg[4]).to_bytes(self.bytes_per_channel, 'little'))
                else:
                    self.logger.error(
                            "Message starts with invalid character %s. Allowed characters: 'r' or 'w'"
                            % msg[0])
                    ret['retcode'] = -3    
                return ret
        except Exception as e:
            self.logger.error("Cannot open process image: %s" % type(e))
            ret['retcode'] = -1
            return ret
    
    def SetParameters(self):
        
        self.commands = {
                'readInput' : 'r,{module},i,{ch}',
                'readOutput' : 'r,{module},o,{ch}',
                'readRTD' : 'r,{module},r,{ch}',
                'writeOutput' : 'w,{module},o,{ch},{value}'
                }
        self.reading_pattern = re.compile(('(?P<value>%s)' % utils.number_regex).encode())
        self.command_patterns = [
                (re.compile(r'write module (?P<module>\d+) output (?P<ch>1|2): (?P<value>\d{1,5})'),
                    lambda x: self.commands['writeOutput'].format(**x.groupdict()))
                 ]

    def ProcessOneReading(self, name, data):

        multiplier = {
                'T_env' : 1.,
                'Pressure_1' : 0.0004375,
                'Pressure_2' : 0.0004375
                }

        offset = {
                'T_env' : 1.,
                'Pressure_1' : -1.75,
                'Pressure_2' : -1.75
                }
        return float(self.reading_pattern.search(data).group('value'))*multiplier[name]+offset[name]
