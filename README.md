# Diffusion Limited Aggregation

Program for observing fractal dimensions of structures created using process called 
Diffusion Limited Aggregation (DLA), depending on memory parameter used in autoregressive process.
## Requirements

- Python >=3.8
- `gcc` for Linux, `XCode` for MacOS, `Visual Studio` for Windows
- [optional] `pygame` for visualization


## How to run

1. Install using pip: `pip install git+https://github.com/Vlaska/diffusion-limited-aggregation` 
or 
`pip install git+https://github.com/Vlaska/diffusion-limited-aggregation[display]` when you want to visualize simualtions.
2. Get configuration files: `python -m DLA configs`
3. Modify configuration files
4. Start simulation
    1. To start one simulation, use `python -m DLA simulate [config-file]`
    2. To start server, use `python -m DLA server -o [output-folder] [config-file]`
    3. To start client, use `python -m DLA client -c [num-of-simultaneous-connections]`

For full list of parameters use `python -m DLA --help`.
