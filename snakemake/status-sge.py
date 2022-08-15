#!/usr/bin/env python
#
# status script for SGE/UGE
# takes jobid, returns success, failed, running. 
#



import subprocess
import sys

def run_command_shell(cmd):
    """
    
    """
    cmdstr = " ".join(cmd)
    cp = subprocess.run(" ".join(cmd), 
                    shell=True, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT)
    return cp

jobid = sys.argv[1]
status = "unknown"
exit_status = "unknown"

statcmd = ['qstat', '-j', f'{jobid}'  ]
acctcmd = ['qacct', '-j', f'{jobid}'  ]

cp = run_command_shell( statcmd )
if str(cp.returncode) == '0':
    # successful return with given jobid, job is running.     
    status = "running"
else:
    # job not running, check job history...
    cp = run_command_shell( acctcmd )
    lines = cp.stdout.decode().split('\n')
    for line in lines:
        key = line[0:13].strip()
        value = line[13:].strip()
        #print(f"{key} = {value}")
        if key == "exit_status":
            exit_status = value
    
    if str(exit_status) == '0':
        status = 'success'
    else:
        status = 'failed'

print(status)
  
