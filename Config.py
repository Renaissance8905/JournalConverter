import json
from Classes.Buffer import Buffer
from Classes.Dates import Dates


class Config(object):

    @staticmethod
    def load(filename='config.json'):
        with open(filename, 'r') as f:
            configs = list(map(Config, json.load(f)))

        return configs

    def __init__(self, d):
        self.year = d.get('year')
        self.input_filename = d.get('input_filename')
        self.expected_output = d.get('expected_output')
        self.needs_clean = d.get('needs_char_clean') or False
        self.buffer = Buffer(d)
        self.anomalies = Dates(d)


if __name__ == '__main__':
    Config.load()
