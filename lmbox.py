from Doberman import SerialSensor

class lmbox(SerialSensor):
    """
    Custom level meter box for pancake
    """

    def SetParameters(self):
        self._msg_start = ''
        self._msg_end = '\r\n'

    def ProcessOneReading(self, name, data):
        values = data.decode().rstrip().split()
        values = list(map(lambda x : int(x,16), values))
        c_off = values[0]
        div = values[1] - values[0]
        self.logger.debug(f'Measured values: {values}')
        if div: # evals to (value[cde] - valuea)/(valueb - valuea)
            resp = [(v-c_off)/div*self.c_ref for v in values[2:]]
            self.logger.debug(f'Calculated response: {resp}')
            if len(resp) > 1:
                return resp
            return resp[0]
