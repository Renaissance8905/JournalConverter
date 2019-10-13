from Config import Config
import os
from typing import *


def write_header(f: IO[AnyStr], t: str, d: str):
    header = 'Title: {}\nDate: {}\n++++++++++++++++++++++++++++++++++++\n\n'
    f.write(header.format(t.strip(), d.strip()))


def check_count(file: str, expected: int, count: int):
    if expected == count:
        success = '\nSuccess! {} entries written from {}.txt\n'
        print(success.format(count, file))
    else:
        warning = '\nWARNING: expected {} entries, found {} in {}.txt\n'
        print(warning.format(expected, count, file))


def process_input_file(config: Config, test: bool) -> str:
    input_filename = config.input_filename

    if test or not config.needs_clean:
        return input_filename

    with open('./plaintexts/' + input_filename + '.txt', 'rt') as file:
        with open('./plaintexts/' + input_filename + '-charcleaned.txt', 'w') as out:
            for line in file.readlines():
                out.write(line.replace('\u2028', '\n'))

    return input_filename + '-charcleaned'


def translate(config: Config, test: bool) -> int:
    # TODO: let's make the Buffer object actually hold the line buffer
    buffer_size = config.buffer.size
    buffer_title_index = config.buffer.title
    buffer_date_index = config.buffer.date

    input_filename = process_input_file(config, test)

    line_buffer = []

    entry_count = 0
    current_date = None
    save_dir = config.output_directory

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
                (new_entry, swap_d_t) = config.is_at_new_entry(line_buffer)
                if new_entry:

                    # figure out the new filename data
                    raw_title = line_buffer[buffer_title_index]
                    raw_date = line_buffer[buffer_date_index]

                    if swap_d_t:
                        raw_date, raw_title = raw_title, raw_date

                elif config.anomalies.known_dateless(line_buffer):

                    raw_title = config.anomalies.known_dateless(line_buffer)
                    raw_date = current_date

                else:
                    continue

                (filename, title, date) = config.get_file_name(raw_title, raw_date)

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

    check_count(config.input_filename, config.expected_output, entry_count)
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
