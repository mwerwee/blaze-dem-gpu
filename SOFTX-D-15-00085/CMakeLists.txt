cmake_minimum_required(VERSION 3.25)
project(BlazeDEM LANGUAGES CXX CUDA)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CUDA_STANDARD 17)
set(CMAKE_CUDA_ARCHITECTURES "50;70;80")

find_package(OpenGL REQUIRED)
find_package(GLUT REQUIRED)

add_executable(BlazeDEM
    V_02_2015/src/main.cpp
    V_02_2015/src/Interface/KDevice.cpp
    V_02_2015/src/Input/KSimulationData.cpp
    V_02_2015/src/Device/DeviceInterface.cu
)

target_include_directories(BlazeDEM PRIVATE V_02_2015/src/)
target_link_libraries(BlazeDEM PRIVATE OpenGL::GL OpenGL::GLU GLUT::GLUT)
target_compile_options(BlazeDEM PRIVATE $<$<COMPILE_LANGUAGE:CUDA>:-O3>)
