#!/usr/bin/env python
#
# qhist 
# jobid     jobname                 ?       submit      time    start                dur        cpus   mem    exit
# 4220821   af2.single               NONE  04/23/2022 19:08:43   04/23/2022 19:30:33    0:21:49  8      1.848T    0     
# 4220108   af2.single               NONE  04/23/2022 19:03:44   04/23/2022 19:25:39    0:21:54  8      1.848T    0    
#

import argparse
import logging
import os
import pwd
import subprocess
import sys

   
    
def qhist(jobname=None, ):
    cmd = f"qhist "
    result = subprocess.check_output( cmd, shell=True, text=True )
    lines = result.split('\n')
    jobid, jobname, 
    

if __name__ == '__main__':
    FORMAT='%(asctime)s (UTC) [ %(levelname)s ] %(filename)s:%(lineno)d %(name)s.%(funcName)s(): %(message)s'
    logging.basicConfig(format=FORMAT)
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--debug',
                         action="store_true",
                         dest='debug',
                         help='debug logging')

    parser.add_argument('-v', '--verbose',
                         action="store_true",
                         dest='verbose',
                         help='verbose logging')


    args= parser.parse_args()
