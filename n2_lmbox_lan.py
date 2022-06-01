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
        self.success_counter = 0
        self.salvage_counter = 0
        self.fail_counter = 0

    def process_one_value(self, name, data):
        """
        Data structure: 6 times 4 integers divided by the split character plus the EOL-character.
        """
        if data[-1] == self.eol:
            data = data[:-1]
            if len(data) != 54:
                self.logger.info(f'data legth is {len(data)} not 54. Trying to salvage...')
                self.logger.debug(data)
                data = self.salvage_input(data)
                if len(data) != 54:
                    self.logger.info(f'salvaging unsuccessful, length is {len(data)} not 54')
                    self.fail_counter += 1
                    return
                else:
                    self.salvage_counter += 1
                    self.logger.debug('salvaging successful')
        else:
            self.logger.debug('data does not end with EOL')
            self.logger.debug(data)
            self.fail_counter += 1
            return
        decoded = struct.unpack('<' + 6 * (4 * 'h' + 'c'), data)
        c_meas = []
        for i in range(6):
            lm_values = decoded[5 * i:5 * i + 4]
            offset_values = sorted(lm_values)[:2]
            n_off = sum(offset_values)
            index_min = lm_values.index(min(offset_values))
            index = (index_min + 2) % 4 if lm_values[(index_min + 1) % 4] in offset_values else (index_min + 1) % 4
            n_ref = lm_values[index]
            n_x = lm_values[(index + 1) % 4]
            c_meas.append(self.c_ref[i] * (n_x - n_off) / (n_ref - n_off))
        self.success_counter += 1
        self.logger.debug(f'success: {self.success_counter-self.salvage_counter}, salvaged: {self.salvage_counter}, failed: {self.fail_counter}')
        return c_meas


    def salvage_input(self, data):
        """
        This may or may not salvage some reading if the length of the data doesn't fit the normal 
        structure.
        """
        place_holder = b'\x02\x00\x02\x00\x05\x00\x03\x00'
        data_temp = data.split(self.split)[:-1]
        data_list = [p if len(p) == 8 else place_holder for p in data_temp]
        data = self.split.join(data_list) + self.split
        return data


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
        time.sleep(1) # Giving the device more time to respond than normal LAN device
        try:
            ret['data'] = self._device.recv(1024)
        except socket.error as e:
            self.logger.fatal('Could not receive data from device. Error: %s' % e)
            ret['retcode'] = -2
        return ret
