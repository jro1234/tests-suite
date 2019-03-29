#!/usr/bin/env python

import sys
import os
from ttools import JobBuilder, SessionMover
session_mover = SessionMover(os.path.abspath(os.path.dirname(__file__)))

# First working directory
fwd = os.getcwd()
config_file = "gmxsimple.yml"
input_file  = os.path.realpath("../small.tpr")
session_counter = 0

test_config_matrix = dict(
  allocation = 'bif112',
  minutes = 5,
  n_mpi_tasks = 1,
  n_nodes = 1,
  threads_per_task = [7, 14, 21],
  mpi_per_task = [1, 2, 3],
  gpu_per_task = [1, 2, 3],
)

node_layout = dict(
  cores = 42,
  gpus = 6,
)
# TODO use node_layout to help calculate
#      allowed configs (they just fail now)
#      --> use it to set some pars
def generate_jobconfigs(config_matrix):
    fixed = dict()
    matrix = list()
    midx = list()

    for k,v in config_matrix.keys():

        if isinstance(v, list):
            matrix.append(v)
            midx.append(k)

        else:
            fixed[k] = v

    for parameterset in itertools.product(*matrix):
        thisset = {k:v for k,v in zip(midx, parameterset)}
        yield thisset.update(fixed)


if __name__ == "__main__":
  #  # Moves us to a new, unique subdirectory
  # TODO needs to capture env and do file linking
  #  session_mover.use_current()  

    jb = JobBuilder()
    jb.load(config_file)

    if not os.path.exists('sessions'):
        os.mkdir('sessions')

    for jobcfg in generate_jobconfigs(test_config_matrix):
        jb.configure_workload(jobcfg)

        next_session_directory = os.path.realpath('sessions/{:04}'.format(session_counter))
        shutil.copy(input_file, next_session_directory)
        os.mkdir(next_session_directory)
        session_counter += 1
        os.chdir(next_session_directory)

        jb.launch_job()

        os.chdir(fwd)
  #  # Move logs that were left in first working
  #  # directory to the session's subdirectory
  #  session_mover.go_back(capture=True)
