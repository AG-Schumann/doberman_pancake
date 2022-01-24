from Doberman import Device
import re

class storm_pancake(Device):

    def send_recv(self, message):
        ret = {'retcode': 0, 'data': message}
        return ret

    def process_one_reading(self, name, data):
        return data
