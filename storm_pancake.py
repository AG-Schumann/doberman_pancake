from Doberman import Sensor
import re

class storm_pancake(Sensor):

    def send_recv(self, message):
        ret = {'retcode': 0, 'data': message}
        return ret

    def process_one_reading(self, name, data):
        return data
