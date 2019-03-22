#!/bin/bash

# TODO a makefile of this
module  load cuda/9.2.148
nvcc -o cuda_add cuda_add.cu
