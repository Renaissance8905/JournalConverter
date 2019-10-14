import dateparser
from typing import Optional, List


class Dates(object):

    def __init__(self, d):

        self.whitelist = d.get('whitelist_dates') or {}
        self.blacklist = d.get('blacklist_dates') or []
        self.dateless = d.get('known_dateless_entries') or []

    def is_date(self, d: str) -> bool:
        """ Check if a line in a file is a date

        Also checks the date whitelist to see if this is
        an unparseable date that we already know about

        :param d: the string to be checked for date-ness
        :return: true if input looks like a date
        """

        if d is None:
            return False

        try:
            test_date = dateparser.parse(d, languages=['en', 'de', 'ru'])

        # from date.parse(), should not happen with dateparser
        except ValueError:
            pass

        else:
            # sometimes NoneType is returned without raising an error
            if test_date is not None:
                # ensure this is not a known false-positive before returning True
                return not d.strip() in self.blacklist

        # if date didn't work, check if it's a known edge case
        return self.whitelist.get(d.strip()) is not None

    def known_dateless(self, b: List[str]) -> Optional[str]:
        """ Check if a line buffer is at a dateless entry

        Note that this depends on a hardcoded list of known dateless
        entries to compare against lines in the buffer. In addition
        to looking for matches from that list, this also requires
        that all other lines in the buffer are blank

        :param b: the current line buffer to check
        :return: the matched entry title, if any
        """

        lines = list(filter(lambda x: len(x.strip()) > 1, b))
        if not len(lines) == 1 or not b[-1] == '\n':
            return None

        line = lines[0].strip()

        for known in self.dateless:
            if line == known:
                return line

        return None
