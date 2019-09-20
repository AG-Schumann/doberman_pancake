import Doberman
import re
import revpimodio2 as rpi

class RevolutionPi(Doberman.RevPi):
    accepted_commands = [

            ]
    def SetParameters(self):
        
        self.commands = {
                'readInput' : 'r,{module},i,{ch}',
                'readOutput' : 'r,{module},o,{ch}',
                'readRTD' : 'r,{module},r,{ch}',
                'writeOutput' : 'w,{module},o,{ch},{value}'
                }
        self.reading_commands = {
                'T_env' : self.commands['readRTD'].format(module=0, ch=1)
                'InputValue_1' : self.commands['readInput'].format(module=0, ch=1) #rename in db
                'InputValue_2' : self.commands['readInput'].format(module=0, ch=2) #rename in db
                }
        self.reading_pattern = re.compile(('(?P<value>%s)' % Doberman.utils.number_regex).encode())
        self.command_patterns = [
                (re.compile(r'write module (?P<module>\d+) output (?P<ch>1|2): (?P<value>\d{1,5})'
                    %  Doberman.utils.number_regex),
                    lambda x: self.commands['writeOutput'].format(**x.groupdict())),

                 ]

    def ProcessOneReading(self, name, data):

        multiplier = {
                'T_env' : 1.,
                'InputValue_1' : 0.0004375
                'Inputvalue_2' : 0.0004375
                }

        offset = {
                'T_env' : 1.,
                'InputValue_1' : -1.75
                'InputValue_2' : -1.75
                }
        return float(self.reading_pattern.search(data).group('value'))*multiplier[name]+offset[name]
