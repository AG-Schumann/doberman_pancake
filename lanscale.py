from Doberman import LANDevice, utils
import re
import socket
import time

class lanscale(LANDevice):
    """
    Scale for nitrogen dewar in pancake.
    """
    eol = b'\n'
    xtrem_remotep = 5555
    msg_wait = 1.0
    recv_interval = 0.01
    commands = {
        'tare': '0001E01020000',
        'untare': '0001E11030000',
        'zero': '0001E10300000'
    }

    def process_one_value(self, name=None, data=None):
        """
        Takes the raw data as returned by send_recv and parses
        it for the float. Only for the scales.
        """
        return float(re.search('(?P<value>\-?[0-9]+(?:\.[0-9]+)?)kg', data).group('value'))


    def setup(self):
        self.packet_bytes = 1024
        self._device = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.logger.debug('Got somewhere')
        self._device.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self._device.settimeout(self.recv_interval)
        self.logger.debug('Got here first')
        self._device.bind(('0.0.0.0', self.xtrem_remotep))
        self.logger.debug('Got here')
        self._msg_start = '\u0002'
        self._msg_end = '\u0003\r\n'
        return True

    def shutdown(self):
        pass

    def execute_command(self, quantity, value):
        return quantity
        if quantity.startswith('0001R'):
            # Allow direct command input only for read commands
            return quantity
        else:
            # Otherwise look up from the command dictionary
            return self.commands[quantity]

    def send_recv(self, message):
        # UDP not TCP so need a special method
        ret = {'retcode': 0, 'data': None}

        message = str(message).rstrip()
        wrappedmessage = self._msg_start + message + self._msg_end
        try:
            self._device.sendto(wrappedmessage.encode(), (self.ip, self.port))
        except socket.error as e:
            self.logger.fatal("Could not send message %s. Error: %s" % (message.strip(), e))
            ret['retcode'] = -2
            return ret

        # Determine string we need to search for in return
        responsesearchpattern = message[2:4] + message[0:2] + message[4].lower() + message[5:9]
        starttime = time.time()
        try:
            # Read until we get the end-of-line character
            data = b''
            for i in range(int(self.msg_wait / self.recv_interval)+1):
                try:
                    data, fromaddress = self._device.recvfrom(self.packet_bytes)
                except socket.timeout:
                    continue
                # Got some data back but still need to check it came from the right device
                data = data.decode()
                if fromaddress == (self.ip, self.port) and responsesearchpattern in data:
                    break
            ret['data'] = data
            self.logger.debug(f'Got {data} from device')
        except socket.error as e:
            self.logger.fatal(f'Could not receive data from device. Error: {e}')
            ret['retcode'] = -2
        return ret
