#!/usr/bin/env python

import argparse
import datetime
import json
import os
import requests
import time
import re

FILES_ENDPOINT = 'https://api.gdc.cancer.gov/files'
DESC = """This program will attempt to use the GDC api to associate a file or set of files with any fields specified
If no fields are specified only the case id will be associated
Either --files or --dir option must be specified"""

def associate(files, fields):
    filters = {
        "op": "in",
        "content": {
            "field": "file_name",
            "value": files
            }
        }
    params = {
        "filters": json.dumps(filters),
        "fields": ",".join(fields),
        "format": "TSV",
        "size": len(files)
    }
    headers = {'content-type': 'application/json'}
    print('Contacting GDC to get requested data')
    response = requests.post(FILES_ENDPOINT, json=params, headers=headers)
    print(response.url)
    now = datetime.datetime.fromtimestamp(time.time()).strftime('%Y%m%d%H%M%S')
    filename = 'files-' + now + '.tsv'
    print('Writing to output file ' + filename)
    file_handle = open(filename, 'w')
    file_handle.write(response.text)


parser = argparse.ArgumentParser(description=DESC)

parser.add_argument('--fields',
                    help='a list of fields to associate with the filename',
                    action='append')
parser.add_argument('--files',
                    help='A list of filenames to get the field data for',
                    action='append')
parser.add_argument('--files-file',
                    help='A file containing a space, comma or newline delimited list of files to get field data for')
parser.add_argument('--dir',
                    help='Instead of a list of files, specify a directory with the files to use, these must have the original filename')

args = parser.parse_args()

if not args.files and not args.dir and not args.files_file:
    parser.print_help()
else:
    fields_arg = args.fields
    if not fields_arg:
        fields_arg = ['cases.case_id', 'file_name']
    else:
        fields_arg.extend(['cases.case_id', 'file_name'])
    # Actually do something
    # prefer files over dir
    files_list = []
    if args.files:
        files_list = args.files
    elif args.dir:
        for dirpath, dirnames, filenames in os.walk(args.dir):
            for filename in filenames:
                files_list.append(filename)
    elif args.files_file:
        with open(args.files_file) as input_file:
            files_list = re.compile("[,\s\n]").split(input_file.read())
    associate(files_list, fields_arg)
