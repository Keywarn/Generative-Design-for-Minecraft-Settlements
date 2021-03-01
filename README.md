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

## Useful Links:

[GDMC Competition](http://gendesignmc.engineering.nyu.edu)

[Generative Deisgn in Minecraft Paper](https://www.researchgate.net/publication/327638962_Generative_design_in_minecraft_GDMC_settlement_generation_competition)

## Early Findings and Notes

Just the results of some early testing so I can keep track

#### Changing Aproach to selecting agents to travel to frontier cell (500 iters of simulation, 4 agents)

| Method                                     | Time  | Number of cells explored | Cells per second |
| ------------------------------------------ | ----- | ------------------------ | ---------------- |
| Find closest agent to the frontier cell    | 34.09 | 323                      | 9.47             |
| Just send the first free agent in the list | 28.13 | 300                      | 10.66            |
|                                            |       |                          |                  |

