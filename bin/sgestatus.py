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
    QHOST_COLS=['hostname','arch','ncpu','nsoc','ncor','nthr','nload','memtot','memuse','swapto','swapus']
    cmd = ['qhost']    
    o = subprocess.check_output(cmd, encoding='UTF-8')
    lines = o.splitlines()
    lines = lines[2:]
    lol = []
    for line in lines:
        lol.append(line.split())
    hdf = pd.DataFrame(lol, columns=QHOST_COLS )
    return hdf
    

def get_qstat_all():
    '''
    qstat -u '*'

    job-ID     prior   name       user         state submit/start at     queue                          jclass                         slots ja-task-ID 
    ------------------------------------------------------------------------------------------------------------------------------------------------
   8953586 0.60250 cryosparc_ bauer        r     10/11/2024 15:08:21 gpu_ded.q@bamgpu09                                               24        
   8970983 0.52274 spacexr    nbhandar     r     10/23/2024 10:07:55 gpu.q@bamgpu04                                                   16        
   8924425 0.52155 ana20k-thr benjami      r     09/30/2024 16:08:11 comp.q@bam17                                                     48 3
    
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
        s += str(x)
    print(f'qstat output: \n{s}')
    '''
    QSTAT_A_COLS = ['job_number','prior','name','user','state','ss_date','ss_time','queue','slots','taskid']
    
    cmd = ['qstat', '-u', '*', '-s','r']
    o = subprocess.check_output(cmd, encoding='UTF-8')
    lines = o.splitlines()
    lines = lines[2:]
    lol = []
    for line in lines:
        lol.append(line.split())
    qdf = pd.DataFrame(lol)
    qdf.columns = QSTAT_A_COLS
    return qdf


def get_jstat_all():
    '''
    qstat -j * -s r   (all jobs currently running)

    '==============================================================',    
    'job_number:                 11034153',
    'submission_time:            03/15/2025 21:26:16.516',
    'owner:                      wangm',
    'department:                 cryocourse',
    'hard_resource_list:         gpu=1,m_mem_free=4G']
    'parallel environment:       threads range: 2',
    
    
    '''
    #cmd = ['qstat', '-j', '*', '-s','-r']
    cmd = ['qjstat', '-j', '*', '-s','-r']
    o = subprocess.check_output(cmd, encoding='UTF-8')
    lines = o.splitlines()
    logging.debug(f'got {len(lines)} lines...')
    joblist = []
    jobdict = None
    for line in lines:
        if line == '==============================================================':
            if jobdict is None:
                pass
            else:
                logging.debug(f"adding job {jobdict['job_number']} to joblist len={len(joblist)}")
                joblist.append(jobdict)
            jobdict = {}
        elif line.startswith('job_number:' ):
            flist = line.split()
            jobdict['job_number'] = flist[1]
        elif line.startswith('submission_time:'):
            flist = line.split()
            jobdict['ss_date'] = flist[1]
            jobdict['ss_time'] = flist[2]    
        elif line.startswith('owner'):
            flist = line.split()
            jobdict['owner'] = flist[1]
        elif line.startswith('hard_resource_list:'):
            flist = line.split()
            rlist = flist[1]
            # default no GPU
            jobdict['gpu'] = '0'
            jobdict['m_mem_free'] = 1
            for kv in rlist.split(','):
                (k,v) = kv.split('=')
                if k == 'm_mem_free':
                    if v.endswith('G'):
                        try:
                            v = int( v[:-1] )
                        except ValueError:
                            logging.warning(f'attempting round() on m_mem_free={v}')
                            try:
                                v = round( float( v[:-1] ) )
                            except ValueError:
                                logging.warning(f'serious problem parsing m_mem_free={v}')
                    jobdict['m_mem_free'] = int(v)
                elif kv == 'gpu=1':
                    (k,v) = kv.split('=')
                    jobdict['gpu'] = int( v)
        elif line.startswith('parallel environment:'):
            jobdict['threads'] = 1
            jobdict['mpi'] = 0
            flist = line.split()
            # parallel environment:       threads range: 8
            # parallel environment:       mpi range: 32
            if flist[2] ==  'threads':
                jobdict['threads'] = int( flist[4])
            elif flist[2] == 'mpi':
                jobdict['mpi'] = int( flist[4] )
                
    jdf = pd.DataFrame(joblist)

    # create total_mem column. 
    jdf['total_mem'] = jdf['m_mem_free'] * jdf['threads']
    
    # fix NaNs
    jdf.fillna( {'threads' : 1, 'mpi' : 0 }, inplace=True)
    
    # re-order columns
    jdf = jdf[ ['job_number','owner', 'threads', 'mpi', 'm_mem_free', 'gpu', 'ss_date', 'ss_time', ] ]
    

    return jdf            
    #return joblist


def get_jobtable():
    sdf = get_qstat_all()
    jdf = get_jstat_all()    
    jtdf = jdf.join(sdf.set_index('job_number'), on='job_number', how='left', rsuffix='_r')
    



    


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
    qdf = get_qhost()
    sdf = get_qstat_all()
    jdf = get_jstat_all()

    # Option 2: Using options.display
    pd.options.display.max_rows = None
    pd.options.display.max_columns = None
    pd.options.display.width = 256

    logging.debug( f'\n{qdf}' )
    logging.debug( f'\n{sdf}')
    logging.debug( f'\n{jdf}' )
              