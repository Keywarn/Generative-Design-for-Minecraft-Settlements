import argparse

"""
Parsing of command line arguments.

No other functionality should be added to this module.
The typically usage is:

>>> from utils.console_args import CONSOLE_ARGS 
"""

def _parse_arguments():
    parser = argparse.ArgumentParser()

    parser.add_argument('-ax', dest='ax',help='The x coordinate of the settlement corner', type=int)
    parser.add_argument('-az', dest='az',help='The z coordinate of the settlement corner', type=int)

    parser.add_argument('-dx', dest='dx',help='Size of settlement in x direction, default is 100', default = 100, type=int)
    parser.add_argument('-dz', dest='dz',help='Size of settlement in z direction, default is 100', default = 100, type=int) 

    parser.add_argument('--agentVis', dest='agentVis', action='store_true',help='Enable to see agents moving around in the world')
    parser.add_argument('--noGraph', dest='noGraph', action='store_true',help='Flag to disable graph visualisations')
    parser.add_argument('--timing', dest='timing', action='store_true',help='Enable to get timing outputs')

    parser.add_argument('--output', dest='output', action='store_true',help='Enable to store the output of various operations such as heightmaps to files')
    parser.add_argument('-worldFile', dest='worldFile', help='Name of the file to get world data from')
    parser.add_argument('--paint', dest='paint', action='store_true', help='Paint the plotmaps onto minecraft world')
    
    #Tuning Params
    parser.add_argument('-steps', dest='steps',help='Set how many iterations should be used during exploration stage (default is -1, explore whole area)', default = -1, type=int)
    
    parser.add_argument('-maxPlotSize', dest='maxPlotSize',help='Set the maximum plot size for merging, smaller numbers results in denser populations but smaller buildings, default 999999', default = 99999, type=int)
    parser.add_argument('-maxFloors', dest='maxFloors',help='Set the maximum number of floors of a building, default 2', default = 2, type=int)
    parser.add_argument('-maxFloorHeight', dest='moxFloorHeight',help='Set the maximum height of each floor, default 4', default = 4, type=int)
    parser.add_argument('-minBuildSize', dest='minBuildSize',help='Set the minimum size of a building, default 4', default = 4, type=int)
    parser.add_argument('-heightDiff', dest='heightDiff',help='Difference in height acceptable for a plot, default 1', default = 1, type=int)
    parser.add_argument('-paveFreq', dest='paveFreq',help='How frequently a path should be upgraded uses randint(0,n) so 1/(paveFreq) is upgraded, default 3', default = 3, type=int)
    return parser.parse_args()

CONSOLE_ARGS =  _parse_arguments()

# optional: delete function after use to prevent calling from other place
del _parse_arguments