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

#### Number of cells observed by 4 agents in 500 iters

| Method                        | Time  | Cells | Cells per Second |
| ----------------------------- | ----- | ----- | ---------------- |
| Just taking the closest agent | 30.85 | 101   | 3.27             |
|                               |       |       |                  |
|                               |       |       |                  |

