# blaze-dem-gpu

A CUDA 12.x port of [Blaze-DEM](https://github.com/ElsevierSoftwareX/SOFTX-D-15-00085), a GPU-accelerated Discrete Element Method (DEM) framework supporting spheres and polyhedra.

The original code targeted CUDA 5.5 / Compute 3.0 (Kepler). This fork brings it up to date for modern NVIDIA hardware and toolchains.

> **Use at your own risk!** It took quite a bit of vibe coding to get this running! :) It kind of works.

## Changes from original

- CUDA 12.x compatibility (sm_50 / sm_70 / sm_80 targets)
- C++17 standard throughout
- CMake build system replacing the Eclipse/make setup
- Per-timestep GPU scratch buffers pre-allocated at startup
- Dead code removed (KHost)
- Modernised device utilities

## Requirements

- NVIDIA GPU, Compute 5.0 or newer (Maxwell / Pascal / Turing / Ampere)
- CUDA Toolkit 12.x
- CMake 3.25+
- OpenGL and GLUT (e.g. `freeglut`)

On Ubuntu/Debian:

```bash
sudo apt install freeglut3-dev libgl1-mesa-dev
```

## Build

```bash
cd SOFTX-D-15-00085
cmake --preset release
cmake --build --preset release
```

The binary is placed at `SOFTX-D-15-00085/build/release/BlazeDEM`.

## Running a simulation

The binary is run from the `SOFTX-D-15-00085/V_02_2015/` directory and reads `../Simulation.KSim` to find the active simulation:

```bash
cd SOFTX-D-15-00085/V_02_2015
../build/release/BlazeDEM
```

Edit `SOFTX-D-15-00085/Simulation.KSim` to select which project and world file to run — only the first line is used:

```
PROJECTFOLDER: 1.Particles_Box    WORLDFILENAME: Poly_128cm     RunMode(0:3D|1:2D)= 0  |GPU_FLAGS| USE_GPU_NUM= 0  USE_MANY_DEVICES= 0
```

Example projects are provided under `SOFTX-D-15-00085/Projects/`.

Results are written to `SOFTX-D-15-00085/Results/<PROJECTFOLDER>/<WORLDFILENAME>/`.

## Original source

The source code under `SOFTX-D-15-00085/` is derived from the upstream Blaze-DEM repository at https://github.com/ElsevierSoftwareX/SOFTX-D-15-00085 and has been modified for CUDA 12 compatibility. The original (unmodified) upstream README is preserved at `SOFTX-D-15-00085/README.md`. If you use this software, please cite the original authors' work as required by the license:

- doi:10.1016/j.cam.2013.12.032
- doi:10.1016/j.amc.2014.10.013
- doi:10.1016/j.mineng.2015.05.010

## License

BSD 3-Clause — see [LICENSE](LICENSE). Original copyright (c) 2015 blazedem.
