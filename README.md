# Diffusion Limited Aggregation

Program for observing fractal dimensions of structures created using process called
Diffusion Limited Aggregation (DLA), depending on memory parameter used in autoregressive process.

## Requirements

- Python >=3.8
- `gcc` for Linux, `XCode` for MacOS, `Visual Studio` for Windows
- [optional] `pygame` for visualization

## How to run

1. Install using one of listed below methods:
   1. `pip install git+https://github.com/Vlaska/diffusion-limited-aggregation`
   2. `pip install git+https://github.com/Vlaska/diffusion-limited-aggregation[display]` when you want to visualize simulations.
   3. Download the repository and use `pip install .` or `python setup.py install`
   4. For development option: install `pip install poetry`, download repository and unpack it, `poetry install --dev`, `python setup.py develop`
2. Get configuration files: `python -m DLA configs`
3. Modify configuration files
4. Start simulation
   1. To start one simulation, use `python -m DLA simulate [config-file]`
   2. To start server, use `python -m DLA server -o [output-folder] [config-file]`
   3. To start client, use `python -m DLA client -c [num-of-simultaneous-connections]`

Get more information by using `python -m DLA --help` or `python -m [simulate|server|client|render|configs]`.

## Server/client connection

Server by default runs at port `1025`. It's broadcasted on the network.

Port of the server/client can be changed by settings environmental variable `DLA_PORT`.

To set ip address of the server for clients, set environmental variable `DLA_SERVER`.

## `.pickle` files

In these files stored are results of simulations.

To open `.pickle` file, you need to use `pickle` library available in `python` and installed library `numpy`.

You can also use `python -m DLA render <file>.pickle`, to render end result of simulation.

### Data in `.pickle` file

`.pickle` file stores dictionary with these keys:

'box_size', 'num_of_boxes'

- `radius` - radius of particles used in simulation
- `window_size` - [see window_size](#window-size)
- `memory` - [see memory](#memory)
- `step_strength` - determines strength of the step, calculated using autoregressive process
- `num_of_iterations` - number of iterations after which simulation ended
- `num_of_particles` - number of particles used in simulation
- `stuck_particles` - positions of all stuck particles at the end of simulation
- `walking_particles` - positions of all walking particles at the end of simulation
- `box_size`
  - sizes of boxes used for calculating fractal dimension
  - every power of 2 in range \[[min_box_size](#min_box_size), [window_size](#window-size) // 2]
- `num_of_boxes`
  - number of boxes of a given size
  - stored in the same order as values of `box_size`

## Configuration file structure

### `config.yml`<span id="config.yml"></span>

- `display`
  - `fps` - frames per second in visualization mode
  - `window_size`<span id="window-size"></span>
    - size of the window and **main plain**
    - must be a power of 2
  - `use_pygame`
    - turn on/off visualization mode
    - turned off, when `pygame` isn't available
  - `print_results`
    - print table with box sizes and their count at the end of simulation
    - turned off when run on server
- `particles`
  - `radius` - radius of the particles
  - `num`
    - number of particles used in simulation
    - real number is `num + 1` (+1 for first static particle)
  - `start_pos` - `list` or `tuple` of two values used for placing first static particle
- `system`
  - `push_out_tries`- how many times to try push out walking particle from inside of static particles, before making it static
  - `max_steps`
    - number of updates of simulations, before it's stopped
    - number of taken steps can be lower, as simulation ends, when there are no walking particles
  - `regen_after_updates`
    - number of updates, after which stuck particles are removed from walking particles
    - used for optimization
- `planes`
  - `min_box_size`<span id="min_box_size"></span>
    - size of the smallest box
    - must be a power of 2
  - `particle_collision_plane_size`
    - size of `Plane` on which stored are, which particles are inside it
    - should not be smaller than 4
    - used for optimized collision detection
    - must be a power of 2
- `simulation`
  - `step_strength` - determines strength of the step, calculated using autoregressive process
  - `memory`<span id="memory"></span>
    - value used in autoregressive process to determined, how much previous value influences new one
    - must be in range (-1, 1)
    - when run on server, this value is not required (it's overwritten)

### `server_config.yml`

- `simulation`
  - for description of contained parameters in this section look into [`config.yml`](#config.yml)
  - `display.print_results` is always `False`
  - `simulation.memory` isn't necessary
- `server`
  - `start`
    - lower value for memory values distributed between clients
    - inclusive value
    - [more info](#memory)
  - `end`
    - upper value for memory values distributed between clients
    - exclusive value
    - [more info](#memory)
  - `step` - step, at which new memory values are generated
  - `num_of_samples` - number of times each memory value is run in simulation
  - `wait_for`
    - time in which server is waiting for simulation end on client side
    - in seconds \[s]
