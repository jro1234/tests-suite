#!/usr/bin/env python

from __future__ import print_function

import os

testshome = os.environ.get("TESTS_HOME", None)
dbpath = os.path.join(testshome, "mongo")

if not os.path.exists(testshome):
    raise RuntimeError(
        "tests-rp folder and TESTS_HOME: '{}' must exist".format(testshome))

verbose = os.environ.get('RADICAL_PILOT_VERBOSE', 'DEBUG')
os.environ['RADICAL_PILOT_VERBOSE'] = verbose

import sys
sys.dont_write_bytecode = True
sys.path.append("..")

import time
from pprint import pformat

import radical.pilot as rp
import radical.utils as ru

from ttools import MongoInstance, SessionMover

# this helps us move around and stay organized
session_mover = SessionMover(os.path.abspath(os.path.dirname(__file__)))


configs = {
    "local.localhost" : {
        "project"  : None,
        "queue"    : None,
        "schema"   : "local",
        "cores"    : 2
    },
    "ornl.summit" : {
        "project"  : "BIF112",
        "queue"    : "batch",
        "schema"   : "local",
        "cores"    : 42,
        "gpus"     : 6
    },
}


if __name__ == "__main__":

    if (len(sys.argv) != 2) or (sys.argv[1] not in configs):
        [
         os.remove(f) for f in
         session_mover.capture_fwd_logs()
        ]

        print(
            '\nUsage:\t%s [localhost || summit]\n' % sys.argv[0])

        sys.exit(1)

    else:
        resource = sys.argv[1]
        session_mover.use_current()

        # we use a reporter class for nicer output
        reporter = ru.Reporter(name='radical.pilot', )#, level=verbose)

    # Start mongod on localhost
    mongo = MongoInstance(dbpath)
    mongo.open_mongodb(create_folder=True)
    time.sleep(15)

    reporter.title('Getting Started (RP version %s)' % rp.version)

    session = rp.Session()

    try:
        config = configs[resource]

        reporter.info('reading config\n')
        reporter.info(pformat(config))
        reporter.ok('>>ok\n')
        reporter.header('create and submit pilots')

        # Add a Pilot Manager for one or more ComputePilots.
        pmgr = rp.PilotManager(session=session)

        # Showing dict initialize for pilot
        pd_init = {
            'resource'      : resource,
            'runtime'       : 5,  # pilot runtime (min)
            'exit_on_error' : True,
            'project'       : config['project'],
            'queue'         : config['queue'],
            'access_schema' : config['schema'],
            'cores'          : config['cores'],
        }

        pdesc = rp.ComputePilotDescription(pd_init)

        # Launch the pilot.
        pilot = pmgr.submit_pilots(pdesc)

        reporter.header('create and submit units')

        # Register the ComputePilot in a UnitManager object.
        umgr = rp.UnitManager(session=session)
        umgr.add_pilots(pilot)

        # Create a workload of ComputeUnits. 
        n = 2   # number of units to run
        reporter.info('creating %d unit description(s)\n\t' % n)

        cuds = list()
        for _ in range(n):

            # non-dict initialization style shown here for CUs
            cud = rp.ComputeUnitDescription()
            
            cud.pre_exec    =  []
            cud.pre_exec    += ['source {}'.format(os.path.join(testshome, '.testrc'))]
            cud.pre_exec    += ['source $ENV_ACTIVATE']
            cud.pre_exec    += ['module load cuda/9.2.148']
            cud.pre_exec    += ['module load gcc/8.1.1']
            cud.pre_exec    += ['module load spectrum-mpi/10.2.0.10-20181214']

            cud.executable  = ['cuda_add']

            cuds.append(cud)
            reporter.progress()

        reporter.ok('>>ok\n')

        # Submit the previously created ComputeUnit descriptions to the
        # PilotManager. This will trigger the selected scheduler to start
        # assigning ComputeUnits to the ComputePilots.
        units = umgr.submit_units(cuds)

        # Wait for all compute units to reach a final state (DONE, CANCELED or FAILED).
        reporter.header('gather results')
        umgr.wait_units()
    
        reporter.info('\n')
        for unit in units:
            reporter.plain('  * %s: %s, exit: %3s, out: %s\n' \
                    % (unit.uid, unit.state[:4], 
                        unit.exit_code, unit.stdout.strip()[:35]))

    except Exception as e:
        reporter.error('caught Exception: %s\n' % e)
        raise e

    except (KeyboardInterrupt, SystemExit) as e:
        # the callback called sys.exit(), and we can here catch the
        # corresponding KeyboardInterrupt exception for shutdown.  We also catch
        # SystemExit (which gets raised if the main threads exits for some other
        # reason).
        reporter.warn('exit requested\n')

    finally:
        reporter.header('finalize')
        session.close(download=True)
        mongo.stop_mongodb()
        session_mover.go_back(capture=True)

    reporter.header()

