from Doberman import Device


class revpi(Device):
    """
    Class for RevolutionPi sensors
    """

    def set_parameters(self):
        self.commands = {
            'readInput': 'r,{module},in,{ch}',
            'readOutput': 'r,{module},out,{ch}',
            'readRTD': 'r,{module},rtd,{ch}',
            'readMuxer': 'r,{module},mux,{ch}',
            'writeOutput': 'w,{module},,{ch},{value}'
        }
        # which lines are the muxers connected to? The last in each list is the RTD line,
        # the others are the digital controls, all with the format (module, ch)
        self.muxer_ctl = [
                [(),(),()],
                [(),(),()],
                [(),(),()]
                ] # TODO this should probably make it into the db
        self.bytes_per_module = 89
        self.bytes_per_channel = 2
        self.offset_by_type = {
            'in': 9,
            'out': 29,
            'rtd': 21,
        }

    def shutdown(self):
        self.f.close()

    def setup(self):
        self.f = open('/dev/piControl0', 'wb+')

    def execute_command(self, quantity, value):
        # this is wrapped in a try-except one call up so we don't
        # need to do it here.
        if quantity == 'fast_cooling_valve':
            module = 3
            ch = 13
            value = 1 if value == 'open' else 0
            return self.commands['writeOutput'].format(module=module, ch=ch, value=value)

    def offset(module, ch, _type):
        return module * self.bytes_per_module + ch * self.bytes_per_channel + self.offset_by_type[_type]

    def read_muxer(self, muxer, ch):
        """
        Reading from the custom muxers is a two-step operation
        """
        muxer_lines = self.muxer_ctl[muxer]
        mask = bin(ch)[2:]
        for (module, line), value in zip(muxer_lines, mask):
            self.set_output(module, line, int(value))
        time.sleep(0.001) # TODO update when we know the actual timing
        return self.read(*muxer_lines[-1], 'rtd')

    def read(self, module, ch, _type):
        if _type == 'mux':
            return self.read_muxer(module, ch)
        self.f.seek(self.offset(module, ch, _type))
        return int.from_bytes(f.read(self.bytes_per_channel), 'little')

    def set_output(self, module, ch, value):
        value = int(value) & ((1 << (8*self.bytes_per_channel))-1) # bitmask 2 lsb
        self.f.seek(self.offset(module, ch, 'out'))
        self.f.write(value.to_bytes(self.bytes_per_channel, 'little'))

    def send_recv(self, message):
        ret = {'retcode': -1, 'data': None}
        msg = message.split(',')  # msg = [<r|w>, <module>, <in|out|rtd|mux>, <channel>, <value>]
        if len(msg) == 5 and msg[0] == 'w':
            rw, module, _type, ch, value = msg
        elif len(msg) == 4 and msg[0] == 'r':
            rw, module, _type, ch = msg
        else:
            self.logger.error(f'Received bad input: {message}')
            return ret
        try:
            if rw == 'r':
                if _type in 'in mux out rtd'.split():
                    ret['data'] = self.read(module, ch, _type)
                    ret['retcode'] = 0
                else:
                    self.logger.error(f'Received bad action: {_type}')
            elif rw == 'w':
                self.set_output(module, ch, value)
                ret['retcode'] = 0
            else:
                self.logger.error(f'Received bad command: {rw}')
        except Exception as e:
            self.logger.error(f'Caught a {type(e)}: {e}')
            ret['retcode'] = -2
        return ret

    def process_one_reading(self, name, data):
        """
        Drops faulty temperature measurements, otherwise leaves the conversion from DAC units to something sensible
        to a later function
        """
        data = float(data)
        # skip faulty temperature measurements
        return None if name[0] == 'T' and data > 63000 else data

