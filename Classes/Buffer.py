
class Buffer(object):

    def __init__(self, d):
        self.size = d['buffer_size']
        self.title = d['buffer_title_index']
        self.date = d['buffer_date_index']
        self.ambiguous = d.get('ambiguous_title_date_order') or False
