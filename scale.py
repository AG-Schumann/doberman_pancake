from Doberman import LANDevice, utils
import re
import socket
import time
import threading

class scale(LANDevice):
    """
    Scale for nitrogen dewar in pancake.
    """
    eol = b'\r\x03'

    def send_recv(self, message):
        ret = {'retcode': 0, 'data': None}

        if not self._connected:
            self.logger.error(f'No device connected, can\'t send message {message}')
            ret['retcode'] = -1
            return ret
        message = str(message).rstrip()
        message = self._msg_start + message + self._msg_end
        try:
            self._device.sendall(message.encode())
        except socket.error as e:
            self.logger.fatal("Could not send message %s. Error: %s" % (message.strip(), e))
            ret['retcode'] = -2
            return ret

        starttime = time.time()
        try:
            # Read until we get the end-of-line character
            data = b''
            for i in range(int(self.msg_wait / self.recv_interval)+1):
                try:
                    data += self._device.recv(self.packet_bytes)
                except socket.timeout:
                    continue
                if data.endswith(self.eol):
                    break
            ret['data'] = re.sub('\s','',data)
            self.logger.debug('Unprocessed data : %s' % data)
        except socket.error as e:
            self.logger.fatal('Could not receive data from device. Error: %s' % e)
            ret['retcode'] = -2
        return ret
    
    
    value_pattern = re.compile((f'(?P<value>{utils.number_regex})kg').encode())
    
