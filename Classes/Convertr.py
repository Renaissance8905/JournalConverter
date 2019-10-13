import dateparser
from datetime import datetime
import Config
import os
from typing import *


def is_date(config: Config.Config, d: str) -> bool:
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
            return not d.strip() in config.anomalies.blacklist

    # if date didn't work, check if it's a known edge case
    return config.anomalies.whitelist.get(d.strip()) is not None


def write_header(f: IO[AnyStr], t: str, d: str):
    header = 'Title: {}\nDate: {}\n++++++++++++++++++++++++++++++++++++\n\n'
    f.write(header.format(t.strip(), d.strip()))


def get_file_name(config: Config.Config, raw_title: str, raw_date: str) -> (str, str, str):
    try:
        date = dateparser.parse(raw_date, languages=['en', 'de', 'ru'])

        # if the date's year is this year, and we're not in this year's journal,
        # then assume the date string had no year component and it defaulted
        if date.year == datetime.now().year and not config.year == date.year:
            d = date.strftime('{}-%m-%d'.format(config.year))
        else:
            d = date.strftime('%Y-%m-%d')

    # threw NoneType because (hopefully) we're on a whitelist date
    except AttributeError:
        d = config.anomalies.whitelist[raw_date.strip()]

    t = clean_file_name(raw_title)
    f = '({0}) {1}.txt'.format(d, t)
    print(f)
    return f, t, d


def clean_file_name(f: str) -> str:
    f = f.strip()
    for c in [',', '.', '\'', '’', '…', '?', '!', ':']:
        f = f.replace(c, '')
    return f


# returns Boolean Tuple (is_date, date_and_title_are_reversed)
def is_at_new_entry(config: Config.Config, b: List[str]) -> (bool, bool):
    # We expect, if we're in the inter-entry position, to see:
    # a non-empty string at title index
    # a valid date at date index
    # only newlines at all other indices
    for i in range(0, config.buffer.size):
        if i == config.buffer.title or i == config.buffer.date:
            # just checking for existence for now
            if len(b[i].strip()) < 1:
                return False, False
        elif not b[i].strip().strip('-') == '':
            return False, False

    # only checking this once all other checks have passed,
    # in case this is_date implementation is expensive
    if is_date(config, b[config.buffer.date]):
        return True, False

    if config.buffer.ambiguous and is_date(config, b[config.buffer.title]):
        return True, True

    return False, False


def check_count(config: Config.Config, count: int):
    expected = config.expected_output
    file = config.input_filename
    if expected == count:
        success = '\nSuccess! {} entries written from {}.txt\n'
        print(success.format(count, file))
    else:
        warning = '\nWARNING: expected {} entries, found {} in {}.txt\n'
        print(warning.format(expected, count, file))


def process_input_file(config: Config.Config, test: bool) -> str:
    input_filename = config.input_filename

    if test or not config.needs_clean:
        return input_filename

    with open('./plaintexts/' + input_filename + '.txt', 'rt') as file:
        with open('./plaintexts/' + input_filename + '-charcleaned.txt', 'w') as out:
            for line in file.readlines():
                out.write(line.replace('\u2028', '\n'))

    return input_filename + '-charcleaned'


def output_directory(config: Config.Config) -> str:
    return 'entries-new/{}/'.format(config.year)


def known_dateless(config: Config.Config, b: List[str]) -> Optional[str]:
    lines = list(filter(lambda x: len(x.strip()) > 1, b))
    if not len(lines) == 1 or not b[-1] == '\n':
        return None

    line = lines[0].strip()

    for known in config.anomalies.dateless:
        if line == known:
            return line

    return None


def translate(config: Config.Config, test: bool) -> int:
    buffer_size = config.buffer.size
    buffer_title_index = config.buffer.title
    buffer_date_index = config.buffer.date

    input_filename = process_input_file(config, test)

    line_buffer = []

    entry_count = 0
    current_date = None
    save_dir = output_directory(config)

    if not test:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        outfile = open(save_dir + 'header.txt', 'w')

    with open('./plaintexts/' + input_filename + '.txt', 'rt') as file:
        for line in file.readlines():
            if len(line_buffer) < buffer_size:
                # still filling the buffer
                line_buffer.append(line)
                continue

            else:
                # cycle a full buffer
                if not test:
                    outfile.write(line_buffer.pop(0))
                else:
                    line_buffer.pop(0)

                line_buffer.append(line)

                # check if we're crossing entries
                (new_entry, swap_d_t) = is_at_new_entry(config, line_buffer)
                if new_entry:

                    # figure out the new filename data
                    raw_title = line_buffer[buffer_title_index]
                    raw_date = line_buffer[buffer_date_index]

                    if swap_d_t:
                        raw_date, raw_title = raw_title, raw_date

                elif known_dateless(config, line_buffer):

                    raw_title = known_dateless(config, line_buffer)
                    raw_date = current_date

                else:
                    continue

                (filename, title, date) = get_file_name(config, raw_title, raw_date)

                current_date = date

                if not test:
                    # cycle to the next file
                    outfile.close()
                    outfile = open(save_dir + filename, 'w')
                    write_header(outfile, raw_title, raw_date)

                # reset the buffer
                line_buffer = []

                # tally the closed entry
                entry_count += 1

    if not test:
        for buff in line_buffer:
            outfile.write(buff)

        outfile.close()

    check_count(config, entry_count)
    return entry_count


def main():
    print_only = True
    count = 0
    configs = Config.load()
    for config in configs:
        count += translate(config, print_only)

    print('\nTOTAL ENTRY COUNT: {}\n'.format(count))


if __name__ == '__main__':
    main()
