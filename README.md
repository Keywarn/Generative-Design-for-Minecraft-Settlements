# Project
Repo for my final year MEng project. Using generative design in Minecraft to create settlements

## Environments

I am using [pyenv](https://github.com/pyenv/pyenv) to manage different python installs and project dependencies. This project has its own enivronemnt running Python 3. To create a new environment:

`pyenv virtualenv <env_name>`

To enter the environemnt:

`pyenv activate <env_name>`

Install required python packages:

`pip install -r requirements.txt`

Leave the environmnet:

`pyenv deactivate`

# Running Code

For running the generator in the competition, simply do:

`python Generator.py`

This command automatically makes use of the `/setbuildarea` command.

Otherwise, in order to run the generator with more options, simply use the following command:

`python Generator.py -ax <CORNER_X> -az <CORNER_Z> -dx <DIM_X> -dz <DIM_Z>`

This will run the program on an area starting at the corner `[<CORNER_X>,<CORNER_Z>]` with a width of `<DIM_X>` and `<DIM_Z>`

There are also other various options which can be changed:



| Option          | Arguments      | Default       | Description                                                  | Required |
| --------------- | -------------- | ------------- | ------------------------------------------------------------ | -------- |
| -h, --help      |                |               |                                                              |          |
| -ax             | AX             |               | X co-ordinate of settlement corner                           | Yes      |
| -az             | AZ             |               | Z co-ordinate of settlement corner                           | Yes      |
| -dx             | DX             | 100           | Size of settlement in x direction                            |          |
| -dz             | DZ             | 100           | Size of settlement in z direction                            |          |
| -steps          | STEPS          | -1 (infinite) | Set how many iterations should be used during exploration stage |          |
| -maxPlotSize    | MAXPLOTSIZE    | 999999        | Set the maximum plot size for merging, smaller numbers esults in denser populations but smaller buildings |          |
| -maxFloors      | MAXFLOORS      | 2             | Maximum number of floors in a building                       |          |
| -maxFloorHeight | MAXFLOORHEIGHT | 4             | Maximum height of each floor                                 |          |
| -minBuildSize   | MINBUILDSIZE   | 4             | Minimum dimensions of a building                             |          |
| -heightDiff     | HEIGHTDIFF     | 1             | Difference in height acceptable for a plot                   |          |
| -paveFreq       | PAVEFREQ       | 3             | How frequently a path should be upgraded uses randint(0,n) so 1/(paveFreq) is upgraded |          |
| --agentVis      |                | Off           | Enable to see agents moving around in the world              |          |
| --noGraph       |                | Off           | Flag to disable graph visualisations                         |          |
| --timing        |                | Off           | Enable to get timing outputs                                 |          |
| --output        |                | Off           | Enable to store world data in binary file                    |          |
| -worldFile      | WORLDFILE      |               | Name of the file to get world data from (skips data gathering) |          |
| --paint         |                | Off           | Paint the plotmaps onto minecraft world                      |          |

