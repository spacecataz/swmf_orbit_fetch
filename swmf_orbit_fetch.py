#!/usr/bin/env python3

'''
Fetch orbit data from CDAweb for modern NASA missions and convert into
SWMF input files.
'''

from argparse import ArgumentParser

parser = ArgumentParser(description=__doc__)
# Add arguments:
parser.add_argument('start', help='Start date to begin fetching in YYYYMMDD'+
                    ' format.', type=str)
parser.add_argument('stop', help='Stop date of fetching in YYYYMMDD'+
                    ' format.', type=str)
parser.add_argument('--save', '-s', help='Save intermediary files' +
                    ' Default behavior is to delete downloaded files.',
                    action='store_true')
parser.add_argument('--debug', '-d', help='Turn on debug output.',
                    action='store_true')
parser.add_argument('--verbose', '-v', help='Turn on verbose output',
                    action='store_true')

# Get args from caller, collect arguments into a convenient object:
args = parser.parse_args()

### MAIN IMPORTS HERE.
# Some take a while to load, we want no delay on printing help statements.
import urllib
import datetime as dt
import xml.etree.ElementTree as ET

from spacepy.pycdf import CDF
from spacepy.pybats import SatOrbit

#### Function definitions:
def fetch_cdf(sat, tstart, tstop, verbose=False):
    '''
    Create URL and fetch CDF file from CDAWeb's RESTful service.
    
    Returns the saved file name on disk on success, False on failure.
    '''

    # Constants:
    base = 'https://cdaweb.gsfc.nasa.gov/WS/cdasr/1/dataviews/sp_phys/datasets/'
    ns   = r'{http://cdaweb.gsfc.nasa.gov/schema}'
    
    url =  \
        f"{base}{sat['set']}/data/{tstart:%Y%m%dT%H%M%S}Z,"+\
        f"{tstop:%Y%m%dT%H%M%S}Z/{sat['var']}?format=cdf"

    if verbose:
        print(f'URL = {url}')

    # Request CDF and fetch XML response.
    with urllib.request.urlopen(url) as response:
        xml = ET.parse(response).getroot()

    # Search XML response for errors.
    if xml.findall(ns+'Error'):
        print('\tNo data for this satellite (error returned)')
        if verbose:
            for x in xml.findall(ns+'Error'):
                print(f'\t{x.text}')
        return False

    # Get URL of CDF file, download, save to disk.
    cdfurl = xml.find(ns+'FileDescription').find(ns+'Name').text
    filename = cdfurl.split('/')[-1]
    if verbose: print(f'\tCDF URL = {cdfurl}')
    urllib.request.urlretrieve(cdfurl, filename)

    # Return name of file to caller:
    return filename
            
#### MAIN SCRIPT FUNCTIONALITY:
    
# If we are in debug mode, we want lots and lots of output!
# Therefore, we turn on verbose mode and save mode, too:
if args.debug:
    args.verbose=True
    args.save=True

try:
    # Try to parse date into datetime object.
    tstart = dt.datetime.strptime(args.start, '%Y%m%d')
    tstop  = dt.datetime.strptime(args.stop,  '%Y%m%d')
except ValueError:  # Specify the type of exception to be specific!
    # If we can't, stop the program and print help.
    print('ERROR: Could not parse date!')
    print(__doc__)
    exit()

# Start by creating a dictionary of known sats and all information required
# to fetch and parse their orbit data from CDAWeb.
sats = {
    'cluster1':{'set':'C1_CP_FGM_SPIN', 'var':'sc_pos_xyz_gse__C1_CP_FGM_SPIN',
                'time':'time_tags__C1_CP_FGM_SPIN', 'coord':'GSE'},
    'cluster2':{'set':'C2_CP_FGM_SPIN', 'var':'sc_pos_xyz_gse__C2_CP_FGM_SPIN', 'coord':'GSE'},
    'cluster3':{'set':'C3_CP_FGM_SPIN', 'var':'sc_pos_xyz_gse__C3_CP_FGM_SPIN', 'coord':'GSE'},
    'cluster4':{'set':'C4_CP_FGM_SPIN', 'var':'sc_pos_xyz_gse__C4_CP_FGM_SPIN', 'coord':'GSE'},
}

# Ask user what satellite to fetch.

# Build orbits for all satellites:
for s in sats:
    # Check for data, fetch CDFs:
    filename = fetch_cdf(sats[s], tstart, tstop, verbose=args.verbose)

    # Open CDF file:
    cdf = CDF(filename)
    
    # Convert to satellite orbit object:
    out = SatOrbit()
    out['time'] = cdf[sats[s]['time']][...]
    out['xyz']  = cdf[sats[s]['var']][...].transpose()

    # Add attributes to file:
    out.attrs['file'] = f'{s}.sat'
    out.attrs['coor'] = sats[s]['coord']
    tnow=dt.datetime.now()
    out.attrs['head'] =  [f'Created with swmf_orbit_fetch.py on '+
                          f'{tnow:%Y-%m-%d %H:%M%S}']
    out.write()

    # TO DO:
    # --units.
    # --remove CDF files.
    # --Plot orbits.
    
    break
