from Doberman import LANSensor, utils
import re  # EVERYBODY STAND BACK xkcd.com/208

class alicat_mcv(LANSensor):

    """
    Flow controller
    """

    def SetParameters(self):
        self._msg_end = '\r'


    def ProcessOneReading(self, name, data):
        ret = []
        pattern = re.compile((f'{utils.number_regex}').encode())
        matches = re.findall(pattern, data)
        ret = [float(match) for match in matches][:5]
        if len(ret) == 5:
            return ret

