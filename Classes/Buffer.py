from typing import List, Optional
from Classes.Dates import Dates

Line = str
LineBuffer = List[Line]


class Buffer(object):

    _buffer: LineBuffer = []

    def __init__(self, d):
        self.size = d['buffer_size']
        self.title = d['buffer_title_index']
        self.date = d['buffer_date_index']
        self.ambiguous = d.get('ambiguous_title_date_order') or False

    def push(self, line: Line) -> Optional[Line]:
        """ Add an incoming line to the buffer and, if full, return the outgoing line

        :param line: the line to be added
        :return: the first line in the current buffer, or None if the buffer is not full
        """

        self._buffer.append(line)
        if len(self._buffer) > self.size:
            return self._buffer.pop(0)

    def clear(self):
        """ Remove all elements from the current buffer """

        self._buffer = []

    @property
    def item_at_date(self) -> Line:
        """ Return the item that is currently at the specified date index

        :return: The line at the date index
        """

        return self._buffer[self.date]

    @property
    def item_at_title(self) -> Line:
        """ Return the item that is currently at the specified title index

        :return: The line at the title index
        """

        return self._buffer[self.title]

    @property
    def is_aligned(self) -> bool:
        """ Checks whether empty/non-empty lines match target indices

            Also will return false while the buffer is still filling

        :return: True if date and title indices are the ONLY lines with content
        """

        if len(self._buffer) < self.size:
            return False

        for idx, item in enumerate(self._buffer):
            d_t = idx in [self.date, self.title]
            has_len = len(item.strip().strip()) > 0
            if not d_t == has_len:
                return False

        return True

    def is_at_new_entry(self, date_config: Dates) -> bool:
        """ Checks whether the current line buffer is at the start of a new entry

        We expect, if we're in the inter-entry position, to see:
        - a non-empty string at title index
        - a valid date at date index
        - only newlines at all other indices
        - OR, if `ambiguous` = true, the above with reversed title and date


        :return: true if the current buffer fits the title/date/emptiness requirements
        """

        # check alignment before doing any actual in-line parsing
        # in case the implementation of is_date is expensive
        if not self.is_aligned:
            return False

        if date_config.is_date(self.item_at_date):
            return True

        if self.ambiguous and date_config.is_date(self.item_at_title):
            self.reverse_title_and_date()
            return True

        return False

    def reverse_title_and_date(self):
        """ Swaps the current title index and date index

            DO NOT CALL
            this should only be invoked internally when the
            proper conditions are discovered during other checks
        """
        if self.ambiguous:
            self.title, self.date = self.date, self.title
