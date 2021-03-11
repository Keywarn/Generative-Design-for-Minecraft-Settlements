import argparse

"""
Parsing of command line arguments.

No other functionality should be added to this module.
The typically usage is:

>>> from utils.console_args import CONSOLE_ARGS 
"""

def _parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--agentVis', dest='agentVis', action='store_true',help='Enable to see agents moving around in the world')
    parser.add_argument('--timing', dest='timing', action='store_true',help='Enable to get timing outputs')

    parser.add_argument('--output', dest='output', action='store_true',help='Enable to store the output of various operations such as heightmaps to files')
    parser.add_argument('-worldFile', dest='worldFile', help='Name of the file to get world data from')
    return parser.parse_args()

CONSOLE_ARGS =  _parse_arguments()

# optional: delete function after use to prevent calling from other place
del _parse_arguments