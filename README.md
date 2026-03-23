# blaze-dem-gpu

A CUDA 12.x port of [Blaze-DEM](https://github.com/ElsevierSoftwareX/SOFTX-D-15-00085), a GPU-accelerated Discrete Element Method (DEM) framework supporting spheres and polyhedra.

The original code targeted CUDA 5.5 / Compute 3.0 (Kepler). This fork brings it up to date for modern NVIDIA hardware and CUDA 12.

## Changes from original

- CUDA 12.x compatibility (sm_50 / sm_70 / sm_80 targets)
- C++17 standard throughout
- CMake build system replacing Eclipse/make
- Per-timestep GPU scratch buffers pre-allocated at startup
- Dead code removed (KHost)
- Modernised device utilities

## Build

Requires CUDA 12.x and CMake 3.18+.

```bash
cmake --preset release
cmake --build --preset release
```

The binary is placed in `SOFTX-D-15-00085/build/release/`.

## Original source

The original Blaze-DEM code is preserved under `SOFTX-D-15-00085/` and is unchanged from the upstream baseline. The upstream repository is at https://github.com/ElsevierSoftwareX/SOFTX-D-15-00085.

If you use this software, please cite the original authors' work as required by the license:

- doi:10.1016/j.cam.2013.12.032
- doi:10.1016/j.amc.2014.10.013
- doi:10.1016/j.mineng.2015.05.010

## License

BSD 3-Clause — see [LICENSE](LICENSE). Original copyright (c) 2015 blazedem.
