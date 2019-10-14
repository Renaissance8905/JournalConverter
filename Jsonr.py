import datetime
import json
import os
import glob

journal_entries = []
my_path = './entries-new/'

for filename in glob.iglob(my_path + '**/*.txt', recursive=True):
    f = filename.split('/')[-1]
    print(f)
    if f == 'header.txt':
        continue

    entry = {}
    (d, t) = f.replace('.txt', '', 1).strip('(').split(') ')
    (yr, mon, day) = list(map(lambda x: int(x), d.split('-')))
    date = datetime.datetime(yr, mon, day)

    entry['title'] = t
    entry['date'] = date.timestamp()
    if os.path.isfile(filename):
        with open(filename, 'rt') as file:
            lines = file.readlines()
            if lines[2] == '++++++++++++++++++++++++++++++++++++\n':
                entry['title'] = lines[0].strip().replace('Title: ', '')
                entry['date_fmt'] = lines[1].strip().replace('Date: ', '')

            entry['body'] = '\n'.join(lines[4:])

    journal_entries.append(entry)
    print(len(journal_entries))

with open('jsons_TEST.json', 'w') as out:
    json.dump(journal_entries, out)


# print_result(journal_entries)

