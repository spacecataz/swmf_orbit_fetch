#!/usr/bin/env python3

'''
Fetch orbit data from CDAweb for modern NASA missions and convert into
SWMF input files.
'''

from argparse import ArgumentParser

parser = ArgumentParser(description=__doc__)
# Add arguments:
parser.add_argument('date', help='Start date to begin fetching in YYYYMMDD'+
                    ' format.', type=str)
parser.add_argument('--nday', '-n', help='Set the number of days to fetch.'+
                    '  Default is to obtain 1 day only.')
parser.add_argument('--save', '-s', help='Save intermediary files' +
                    ' Default behavior is to delete downloaded files.',
                    action='store_true')
parser.add_argument('--debug', '-d', help='Turn on debug output.',
                    action='store_true')
parser.add_argument('--verbose', '-v', help='Turn on verbose output',
                    action='store_true')

import urllib

# Get args from caller, collect arguments into a convenient object:
args = parser.parse_args()

# If we are in debug mode, we want lots and lots of output!
# Therefore, we turn on verbose mode and save mode, too:
if args.debug:
    args.verbose=True
    args.save=True

try:
    # Try to parse date into datetime object.
    time = dt.datetime.strptime(args.date, '%Y%m%d')
except ValueError:  # Specify the type of exception to be specific!
    # If we can't, stop the program and print help.
    print('ERROR: Could not parse date!')
    print(__doc__)
    exit()

# Define
sats = {}
