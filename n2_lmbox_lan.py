from Doberman import LANDevice
import struct
import time
import socket


class n2_lmbox_lan(LANDevice):
    """
    Custom level meter box for pancake. The device is read out through an RS485 to ETH adapter, that's why
    it inherits from LANSensor. send_recv() is modified to sleep longer since the device reacts slower than
    a standard LAN sensor.
    """

    def set_parameters(self):
        self.eol = 13
        self.split = b'\x06'

    def process_one_value(self, name, data):
        """
        Data structure: 6 times 4 integers divided by the split character plus the EOL-character.
        """
        if data[-1] != self.eol:
            self.logger.info(f'Data does not end with EOL but with {data[-1]}')
        data = data.split(self.split)[:-1] # Remove EOL

        c_meas = []
        for i, readingdata in enumerate(data):
            try:
                lm_values = struct.unpack('<hhhh', readingdata) # Each packet is four shorts

                # The two smallest values are the offsets
                # Order always the same, but starting value changes
                offset_values = sorted(lm_values)[:2]
                n_off = sum(offset_values)
                index_min = lm_values.index(min(offset_values))
                index = (index_min + 2) % 4 if lm_values[(index_min + 1) % 4] in offset_values else (index_min + 1) % 4
                n_ref = lm_values[index]
                n_x = lm_values[(index + 1) % 4]
                if (self.params['c_ref'][i] * (n_x - n_off) / (n_ref - n_off) > 350):
                    self.logger.debug(f"High capacitance {i}. Readings: {', '.join(lm_values)}")

                c_meas.append(self.params['c_ref'][i] * (n_x - n_off) / (n_ref - n_off))
            except Exception as e:
                self.logger.warning(f'Problem interpreting capacitance value {i}, {e}')
                c_meas.append(None)
        return c_meas

    def send_recv(self, message):
        ret = {'retcode': 0, 'data': None}

        if not self._connected:
            self.logger.error('No device connected, can\'t send message %s' % message)
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
        time.sleep(2) # Giving the device more time to respond than normal LAN device
        try:
            ret['data'] = self._device.recv(1024)
            self.logger.debug(f'data: {ret["data"]}')
        except socket.error as e:
            self.logger.fatal('Could not receive data from device. Error: %s' % e)
            ret['retcode'] = -2
        return ret
