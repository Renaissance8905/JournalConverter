
class Dates(object):

    def __init__(self, d):

        self.whitelist = d.get('whitelist_dates') or {}
        self.blacklist = d.get('blacklist_dates') or []
        self.dateless = d.get('known_dateless_entries') or []

