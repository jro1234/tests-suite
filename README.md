## tests-suite
HPC Tests for Radical Pilot, OpenMM, and AdaptiveMD

Tests for gpu usage, openmm functionality, and workflow functionality via RP and AdaptiveMD.
To deploy this test suite on your system, you will likely need to make a number of changes to
these files and/or configure RP for your resource, which cannot be automated. 

The software components and tests are used as building blocks to evaluate the multiple
layers involved in running HPC workflows. Tests are organized in hierarchies that build up
to full end-to-end workflow tests.

AdaptiveMD - Workflow Generator
 - with RP:
 - bare metal:

Radical Pilot - Rsc/Exec Manager
 - OpenMM MD:
 - OpenMM Benchmark:
 - cuda_add:
 - helloworld:

OpenMM - MD Task Kernel
 - benchmark: find & use `/openmm/examples/benchmark.py`
 - test: execute `python -m simtk.testInstallation`
   - without submission:
   - with submission:
 - MD: villin system `TODO simple call`
 
Cuda_add - hello gpu
 - without submission:
 - with submission:

Experiments: Weak Scaling with Villin MD System
 - AdaptiveMD bare metal:
   - watch: DB Host, workflow execution profiling
 - AdaptiveMD with RP:
   - watch: workflow execution profiling
