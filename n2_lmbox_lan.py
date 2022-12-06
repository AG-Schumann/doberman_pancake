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
        self.msg_sleep = 2

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

