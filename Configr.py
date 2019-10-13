import json


class Buffer(object):

    def __init__(self, d):
        
        self.size = d['buffer_size']
        self.title = d['buffer_title_index']
        self.date = d['buffer_date_index']
        self.ambiguous = d.get('ambiguous_title_date_order') or False


class Dates(object):

    def __init__(self, d):

        self.whitelist = d.get('whitelist_dates') or {}
        self.blacklist = d.get('blacklist_dates') or []
        self.dateless = d.get('known_dateless_entries') or []


class Config(object):

    def __init__(self, d):
        
        self.year = d.get('year')
        self.input_filename = d.get('input_filename')
        self.expected_output = d.get('expected_output')
        self.needs_clean = d.get('needs_char_clean') or False
        self.buffer = Buffer(d)
        self.anomalies = Dates(d)


def load(filename='config.json'):
    with open(filename, 'r') as f:
        configs = list(map(Config, json.load(f)))

    return configs


if __name__ == '__main__':
    load()
