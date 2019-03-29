#!/usr/bin/env python

import sys
import os
import shutil
import itertools

from ttools import JobBuilder, SessionMover

# First working directory
if "__file__" in globals():
    fwd = os.path.abspath(os.path.dirname(__file__))
else:
    fwd = os.getcwd()

session_mover = SessionMover(fwd)
config_file = "gmxsimple.yml"
input_file  = os.path.realpath("../small.tpr")

jobconfig_matrix = dict(
  threads_per_task = [7, 14, 21],
  gpu_per_task = [1, 2, 3],
)

test_keys, test_matrix = list(zip(*jobconfig_matrix.items()))

# Task here is like "MD task" of whatever
# is assigned to a single MD instance.
# On Summit, this maps to "resource set"
jobconfig_base = dict(
  allocation = 'bif112',
  minutes = 5,
  mpi_per_task = 1,
  n_nodes = 1,
  n_tasks = 1,
)


if __name__ == "__main__":
  #  # Moves us to a new, unique subdirectory
  # TODO needs to capture env and do file linking
  #  session_mover.use_current()

    jb = JobBuilder()
    jb.load(config_file)
    next_session_directory = session_mover.current

    # Loop through parameter combinations
    # 1. this config 2. move dir 3. launch 4. move back
    for test_pars in itertools.product(*test_matrix):
        jobconfig = {k:v for k,v in zip(test_keys, test_pars)}
        jobconfig.update(jobconfig_base)
        jb.configure_workload(jobconfig)

        os.mkdir(next_session_directory)
        shutil.copy(input_file, next_session_directory)
        os.chdir(next_session_directory)

        jb.launch_job()
        os.chdir(fwd)
        next_session_directory = next(session_mover)
  #  # Move logs that were left in first working
  #  # directory to the session's subdirectory
  #  session_mover.go_back(capture=True)
