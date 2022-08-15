#!/usr/bin/env python
import subprocess
import sys


def run_command_shell(cmd):
    """
    maybe subprocess.run(" ".join(cmd), shell=True)
    cmd should be standard list of tokens...  ['cmd','arg1','arg2'] with cmd on shell PATH.
    
    """
    cmdstr = " ".join(cmd)
    #logging.info(f"running command: {cmdstr} ")
    start = dt.datetime.now()
    cp = subprocess.run(" ".join(cmd), 
                    shell=True, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT)
    #cp = subprocess.run(cmd, 
    #                shell=True, 
    #                stdout=subprocess.PIPE, 
    #                stderr=subprocess.STDOUT)
    end = dt.datetime.now()
    elapsed =  end - start
    #logging.debug(f"ran cmd='{cmdstr}' return={cp.returncode} {elapsed.seconds} seconds.")
    return cp

jobid = sys.argv[1]

#output = str(subprocess.check_output("sacct -j %s --format State --noheader | head -1 | awk '{print $1}'" % jobid, shell=True).strip())

status = "unknown"

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
  
