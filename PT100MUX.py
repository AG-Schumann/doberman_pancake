from Doberman import Sensor
import time


class PT100MUX(Sensor):
    """
    Plug-in for PT100MUX multiplexer. This works together with a given RevPi and must be executed on this RevPi.
    The plugin sends a series of digital inputs to the Multiplexer (0-7) to change the channel and measures the output
    current for each channel.
    To save in additional parameters in DB:
        digital_start: offset of first digital channel
        analog_offset: offset of analog channel
    """

    def send_recv(self, message):
        ret = {'retcode': 0, 'data': []}
        for i in range(8):
            self.switch_channel(i)
            time.sleep(0.3)  # Let analog channel adjust to new value
            with open('/dev/piControl0', 'wb+', 0) as f:
                f.seek(self.analog_offset)
                ret.data.append(int.from_bytes(f.read(2), 'little'))
        return ret

    def switch_channel(self, i):
        bin_str = format(i, '03b')[::-1]  # 0='000', 1='100', 2='010', 3='110', ..., 7='111'
        with open('/dev/piControl0', 'wb+', 0) as f:
            for j in range(3):
                f.seek(int(self.digital_start) + j)
                f.write(int(bin_str[j]).to_bytes(2, 'little'))
