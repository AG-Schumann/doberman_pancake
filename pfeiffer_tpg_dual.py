from Doberman import LANDevice, utils
import re  # EVERYBODY STAND BACK xkcd.com/208


class pfeiffer_tpg_dual(LANDevice):
    def set_parameters(self):
        self._msg_begin = ''
        self._msg_end = '\r\n\x05'
        self.commands = {
                'identify' : 'AYT',
                }
        self.value_pattern = re.compile(('(?P<status>[0-9]),(?P<value>%s)' %
                                                    utils.number_regex).encode())

    def setup(self):
        self.send_recv(self.commands['identify'])
        # stops the continuous flow of data

