import json
import dateparser
from datetime import datetime
from typing import List
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

    def is_at_new_entry(self, b: List[str]) -> (bool, bool):
        """ Checks whether the current line buffer is at the start of a new entry

        We expect, if we're in the inter-entry position, to see:
        - a non-empty string at title index
        - a valid date at date index
        - only newlines at all other indices

        :param b: the current line buffer to check
        :return: boolean pair representing (is_new_entry, date_and_title_are_reversed)
        """

        for i in range(0, self.buffer.size):
            if i == self.buffer.title or i == self.buffer.date:
                # just checking for existence for now
                if len(b[i].strip()) < 1:
                    return False, False
            elif not b[i].strip().strip('-') == '':
                return False, False

        # only checking this once all other checks have passed,
        # in case this is_date implementation is expensive
        if self.anomalies.is_date(b[self.buffer.date]):
            return True, False

        if self.buffer.ambiguous and self.anomalies.is_date(b[self.buffer.title]):
            return True, True

        return False, False

    def get_file_name(self, raw_title: str, raw_date: str) -> (str, str, str):
        try:
            date = dateparser.parse(raw_date, languages=['en', 'de', 'ru'])
            d = date.strftime(self.date_format(date.year))

        # threw NoneType because (hopefully) we're on a whitelist date
        except AttributeError:
            d = self.anomalies.whitelist[raw_date.strip()]

        t = self.clean_file_name(raw_title)
        f = '({0}) {1}.txt'.format(d, t)
        print(f)
        return f, t, d

    def date_format(self, year: int) -> str:
        """ Format string for date -> str conversions

        If the date's year is this year, and we're not in this year's journal,
        then assume the date string had no year component and it defaulted.
        In that case we will hardcode the config's date into the format string.

        :param year: the (supposed) year of the date to be stringified
        :return: a `%Y-%m-%d`-style format string for dateparser
        """

        if year == datetime.now().year and not self.year == year:
            return '{}-%m-%d'.format(self.year)
        else:
            return '%Y-%m-%d'

    @classmethod
    def clean_file_name(cls, f: str) -> str:
        f = f.strip()
        for c in [',', '.', '\'', '’', '…', '?', '!', ':']:
            f = f.replace(c, '')
        return f

    @property
    def output_directory(self) -> str:
        """ The directory in which to write output from this config

        NOTE:   this string is only hardcoded for consistency during
                processing. Feel free to edit it however you want;
                e.g. remove the reference to `self.year` to have all
                entries from several groups to write to the same place
        :return: the relative filepath of the destination directory
        """

        return 'entries-new/{}/'.format(self.year)


if __name__ == '__main__':
    Config.load()
