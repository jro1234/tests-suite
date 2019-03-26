#!/usr/bin/env python

import sys
import os
from ttools import JobBuilder, SessionMover
session_mover = SessionMover(os.path.abspath(os.path.dirname(__file__)))

config_file = "gmxsimple.yml"

jobconfig = dict(
  allocation = 'bif112',
  minutes = 5,
  n_tasks = 1,
  n_nodes = 1,
  threads_per_task = 7,
  mpi_per_task = 1,
  gpu_per_task = 1,
)


if __name__ == "__main__":
  #  # Moves us to a new, unique subdirectory
  # TODO needs to capture env and do file linking
  #  session_mover.use_current()  

    jb = JobBuilder()
    jb.load(config_file)
    jb.configure_workload(jobconfig)

    jb.launch_job()

  #  # Move logs that were left in first working
  #  # directory to the session's subdirectory
  #  session_mover.go_back(capture=True)
