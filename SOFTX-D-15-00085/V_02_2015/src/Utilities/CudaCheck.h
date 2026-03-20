/*
 * CudaCheck.h
 *
 * CUDA error checking macro. Replaces the manual
 * cudaGetLastError() + if(errormsg>0) + exit(1) pattern.
 */

#ifndef CUDACHECK_H_
#define CUDACHECK_H_

#include <cstdio>
#include <cstdlib>
#include <cuda_runtime.h>

#define CUDA_CHECK(msg)                                                  \
    do {                                                                 \
        cudaError_t err = cudaGetLastError();                            \
        if (err != cudaSuccess) {                                        \
            fprintf(stderr, "CUDA error at %s:%d [%s]: %s\n",           \
                    __FILE__, __LINE__, (msg), cudaGetErrorString(err)); \
            exit(1);                                                     \
        }                                                                \
    } while (0)

#endif /* CUDACHECK_H_ */
