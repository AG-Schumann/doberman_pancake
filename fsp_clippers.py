from Doberman import Device, utils
import requests
import re

class fsp_clippers(Device):

    def set_parameters(self):
        self.keys = ['batteryCapacity',
                     'batteryRemainTime',
                     'batteryVoltage',
                     'inputVoltage',
                     'outputCurrent',
                     'outputVoltage',
                     'outputLoadPercent',
                     'temperature'
                     ]

    def send_recv(self, message):
        ret = {'retcode': 0, 'data': []}
        data = requests.get(url=self.url).json()['workInfo']
        for key in self.keys:
            ret['data'].append(float(data[key]))
        return ret

    def process_one_value(self, name, data):
        return data
