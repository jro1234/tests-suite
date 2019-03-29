#!/usr/bin/env python

import os
import sys

from ttools import small_proc_watch_block

def match_line(line, keys):
    return all([0 <= line.find(k) for k in keys])

resultfile = "md.log"
parsfile = "jobscript.bash"
reading_key = {"ns/day", "hour/ns"}
verify_key = {"Performance"}
pars_key = {"jsrun"}

# Must be ordered!
pars_test = ["--cpu_per_rs", "--gpu_per_rs", "--tasks_per_rs"]

all_sessions = os.listdir("sessions")

data = list()

for session in all_sessions:
    session_results = os.path.realpath(os.path.join("sessions", session, resultfile))
    session_pars = os.path.realpath(os.path.join("sessions", session, parsfile))

    if os.path.exists(session_results):

        lines, retval = small_proc_watch_block("cat " + session_pars)
        for line in lines.decode(encoding='UTF-8').splitlines():
            if match_line(line, pars_key):
                ll = iter(line.split())
                pars = dict()
                for l in ll:
                    if l in pars_test:
                        pars[l] = next(ll)

                data.append(pars)

        lines, retval = small_proc_watch_block("tail " + session_results)
        for line in lines.decode(encoding='UTF-8').splitlines():
            if match_line(line, verify_key):
                data[-1]["speed"] = float(line.split()[1])

print(data)

with open("mdspeeds.data", "w") as f:
    lines = list()
    for d in data:
        line = ' '.join(['- '.join([k, str(d[k])]) for k in pars_test])
        line += ' ' + "speed- " + str(d["speed"])
        lines.append(line)

    f.write('\n'.join(lines))
