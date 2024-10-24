#!/usr/bin/env python
#
# Make human-interpretable table of node resources/occupancy. 
#
import argparse
import logging
import os
import pprint
import subprocess
import sys
import traceback

from configparser import ConfigParser

import datetime as dt
import pandas as pd


def format_config(cp):
    cdict = {section: dict(cp[section]) for section in cp.sections()}
    s = pprint.pformat(cdict, indent=4)
    return s

class NonZeroReturnException(Exception):
    """
    Thrown when a command has non-zero return code. 
    """
    

def run_command_shell(cmd):
    """
    maybe subprocess.run(" ".join(cmd), shell=True)
    cmd should be standard list of tokens...  ['cmd','arg1','arg2'] with cmd on shell PATH.
    
    """
    cmdstr = " ".join(cmd)
    logging.debug(f"running command: {cmdstr} ")
    start = dt.datetime.now()
    cp = subprocess.run(" ".join(cmd), 
                    shell=True, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT)

    end = dt.datetime.now()
    elapsed =  end - start
    logging.debug(f"ran cmd='{cmdstr}' return={cp.returncode} {elapsed.seconds} seconds.")
    
    if cp.stderr is not None:
        logging.warn(f"got stderr: {cp.stderr}")
        pass
    if cp.stdout is not None:
        #logging.debug(f"got stdout: {cp.stdout}")
        pass
    if str(cp.returncode) == '0':
        #logging.debug(f'successfully ran {cmdstr}')
        logging.debug(f'got rc={cp.returncode} command= {cmdstr}')
    else:
        logging.warn(f'got rc={cp.returncode} command= {cmdstr}')
        raise NonZeroReturnException(f'For cmd {cmdstr}')
    return cp



def get_qhost():
    '''
    
    qhost
    
    HOSTNAME                ARCH         NCPU NSOC NCOR NTHR NLOAD  MEMTOT  MEMUSE  SWAPTO  SWAPUS
    ----------------------------------------------------------------------------------------------
    global                  -               -    -    -    -     -       -       -       -       -
    bam01                   lx-amd64       96    2   48   96  0.20  754.4G  286.7G   12.0G  174.5M
    bam02                   lx-amd64       96    2   48   96  0.01  754.4G   23.1G   12.0G     0.0
    bam03                   lx-amd64       96    2   48   96  0.19  754.4G  144.1G   12.0G  789.4M


    '''

    cmd = ['qhost']

    try:
        cp = run_command_shell(cmd)
        
    except NonZeroReturnException as nzre:
        logging.error(f'problem with command {cmd}')
        logging.error(traceback.format_exc(None))
        raise    

    output = [line for line in cp.stdout.splitlines() if line != '']
    s = ''
    for x in output:
        s += x
    print(f'qhost output: \n{s}')


def get_qstat_all():
    '''
    qstat -u '*'

    job-ID     prior   name       user         state submit/start at     queue                          jclass                         slots ja-task-ID 
    ------------------------------------------------------------------------------------------------------------------------------------------------
   8953586 0.60250 cryosparc_ bauer        r     10/11/2024 15:08:21 gpu_ded.q@bamgpu09                                               24        
   8970983 0.52274 spacexr    nbhandar     r     10/23/2024 10:07:55 gpu.q@bamgpu04                                                   16        
   8924425 0.52155 ana20k-thr benjami      r     09/30/2024 16:08:11 comp.q@bam17                                                     48 3
    
    '''

    cmd = ['qstat', '-u', "'*'"]

    try:
        cp = run_command_shell(cmd)
        
    except NonZeroReturnException as nzre:
        logging.error(f'problem with command {cmd}')
        logging.error(traceback.format_exc(None))
        raise    

    output = [line for line in cp.stdout.splitlines() if line != '']
    s = ''
    for x in output:
        s += x
    print(f'qstat output: \n{s}')


if __name__ == '__main__':
    FORMAT='%(asctime)s (UTC) [ %(levelname)s ] %(filename)s:%(lineno)d %(name)s.%(funcName)s(): %(message)s'
    logging.basicConfig(format=FORMAT)
    logging.getLogger().setLevel(logging.WARN)
    
    parser = argparse.ArgumentParser()
      
    parser.add_argument('-d', '--debug', 
                        action="store_true", 
                        dest='debug', 
                        help='debug logging')

    parser.add_argument('-v', '--verbose', 
                        action="store_true", 
                        dest='verbose', 
                        help='verbose logging')
    
    parser.add_argument('-c','--config', 
                        metavar='config',
                        required=False,
                        default=os.path.expanduser('~/git/elzar-example/etc/sgestatus.conf'),
                        type=str, 
                        help='config file.')    
        
    args= parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)   

    cp = ConfigParser()
    cp.read(args.config)
       
    cdict = format_config(cp)
    logging.debug(f'Running with config. {args.config}: {cdict}')

    get_qstat_all()
    get_qhost()
          