> **Note:** This folder contains code derived from the original [Blaze-DEM](https://github.com/ElsevierSoftwareX/SOFTX-D-15-00085) repository, modified for CUDA 12.x compatibility. The build instructions below are from the original and are outdated — see the [root README](../README.md) for current build and usage instructions.

---

# blazedemGPU
GPU based discrete element framework (spheres and polyhedra (experimential))
============================================================================

Graphics card (NVIDIA only): Atleast CUDA Compute 3.0 (Kepler only) 
Software requirements: CUDA 5.5 and above
                       C++ compiler

Compile on machine: 
-------------------

1. Launch nsight
2. File -> Import -> General -> Existing Projects into Workspace -> Select root directory -> Finish
3. Project -> Build Configurations -> Set Active -> Release
4. Project -> Clean
5. Project -> Build All

Run Executable: 
---------------

cd blazedemGPU/V_02_2015/

ln -s Release/V_02_2015 Blaze-DEM

chmod +x Blaze-DEM (Linux / OSX)  

./Blaze-DEM

