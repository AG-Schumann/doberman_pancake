import fcntl
import struct
from Doberman import Sensor
import re


class revpi(Sensor):
    """
    Class for RevolutionPi sensors
    """

    def set_parameters(self):
        self.commands = {
            'read': 'r {name}',
            'write': 'w {name} {value}'
        }
        self.command_patterns = [
            (re.compile(r'set (?P<name>\w+) (?P<value>\d{1,5})'),
             lambda x: self.commands['write'].format(**x.groupdict())),
        ]
        self.positions = {}
        self.img = open('/dev/piControl0', 'wb+', 0)
        self.targets = {'fast_cooling_valve': 'O_13', }
        self.keywords = {'open': 1, 'close': 0, }

    def get_position(self, name):
        prm = (b'K'[0] << 8) + 17
        struct_name = struct.pack('37s', name.encode())
        ret = fcntl.ioctl(self.img, prm, struct_name)
        return ret

    def write(self, name, value):
        """
        Set the value of a variable (most likely an output)
        :param name: name of the variable as defined in the Pictory
        :param value: value to be set
        """
        if name not in self.positions:
            self.positions[name] = self.get_position(name)
        offset = struct.unpack_from('>H', self.positions[name], 32)[0]
        length = struct.unpack_from('>H', self.positions[name], 35)[0]
        prm = (b'K'[0] << 8) + 16
        byte_array = bytearray([0, 0, 0, 0])
        if length == 1:  # single bit
            if value in [0, 1]:
                bit = struct.unpack_from('B', self.positions[name], 34)[0]
                struct.pack_into('>H', byte_array, 0, offset)
                struct.pack_into('B', byte_array, 2, bit)
                struct.pack_into('B', byte_array, 3, value)
                fcntl.ioctl(self.img, prm, byte_array)
            else:
                self.logger.debug(f'Invalid value {value}. choose 0 or 1')
        else:  # writing 2 bytes
            self.img.seek(int(offset >> 8))
            self.img.write(int(value).to_bytes(2, 'little'))

    def read(self, name):
        """
        Read value of a variable
        :param name: name of the variable as defined in the Pictory
        """
        if name not in self.positions:
            self.positions[name] = self.get_position(name)
        value = bytearray([0, 0, 0, 0])
        offset = struct.unpack_from('>H', self.positions[name], 32)[0]
        length = struct.unpack_from('>H', self.positions[name], 35)[0]
        prm = (b'K'[0] << 8) + 15
        if length == 1:  # single bit
            bit = struct.unpack_from('B', self.positions[name], 34)[0]
            struct.pack_into('>H', value, 0, offset)
            struct.pack_into('B', value, 2, bit)
            fcntl.ioctl(self.img, prm, value)
            ret = value[3]
        else:  # two bytes
            self.img.seek(int(offset >> 8))
            ret = int.from_bytes(self.img.read(2), 'little')
        return ret

    def execute_command(self, command):
        # command looks like "set <target> <value>"
        # this is wrapped in a try-except one call up so we don't
        # need to do it here. We rsplit with max here so "target"
        # can potentially have spaces in it and won't cause issues
        target, value = command[4:].rsplit(' ', maxsplit=1)
        if target in self.targets:
            # "fast_cooling_valve open" or something
            target = self.targets[target]
            if value in self.keywords:
                value = self.keywords[value]
        return self.commands['write'].format(name=target, value=value)

    def send_recv(self, message):
        ret = {'retcode': 0, 'data': None}
        msg = message.split()  # msg = <r|w> <name> [<value>]
        if msg[0] == 'r':
            ret['data'] = self.read(msg[1])
        elif msg[0] == 'w':
            if int(msg[2]) > (1 << 16):
                pass
            self.write(msg[1], msg[2])
        else:
            self.logger.error(f"Message starts with invalid character {msg[0]}. Allowed characters: 'r' or 'w'")
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
