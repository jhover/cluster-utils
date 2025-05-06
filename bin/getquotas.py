#!/usr/bin/env python
#
#  /usr/lpp/mmfs/bin/mmlsquota -j gillis_hpc_data grid   
#  
# zador_hpc                Linked  /mnt/grid/zador/hpc
# zador_hpc_norepl         Linked  /mnt/grid/zador/hpc_norepl
# zador_hpc_home           Linked  /mnt/grid/zador/hpc/home
# zador_hpc_norepl_data    Linked  /mnt/grid/zador/hpc_norepl/data
# zador_nlsas              Linked  /mnt/grid/zador/nlsas
# zador_nlsas_norepl       Linked  /mnt/grid/zador/nlsas_norepl
# zador_nlsas_norepl_data  Linked  /mnt/grid/zador/nlsas_norepl/data
# zador_nlsas_data         Linked  /mnt/grid/zador/nlsas/data
#
#   



import argparse
import datetime as dt
import logging
import subprocess


FSLIST = [  'mbseq_data_norepl',
            'mbseq_data',
            'mbseq_data_norepl',
            'zador_data_norepl',
            'zador_hpc_home'
          ]
QUOTACMD = '/usr/lpp/mmfs/bin/mmlsquota'


def run_command_shell(cmd):
    """
    maybe subprocess.run(" ".join(cmd), shell=True)
    cmd is list of tokens...  ['cmd','arg1','arg2'] with cmd on shell PATH.
    """
    cmdstr = " ".join(cmd)
    logging.info(f"running command: {cmdstr} ")
    start = dt.datetime.now()
    cp = subprocess.run(" ".join(cmd),
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT)
    end = dt.datetime.now()
    elapsed =  end - start

    if cp.stderr is not None:
        #logging.debug(f"got stderr: {cp.stderr}")
        pass
    if cp.stdout is not None:
        #logging.debug(f"got stdout: {cp.stdout}")
        pass
    if str(cp.returncode) == '0':
        #logging.info(f'successfully ran {cmdstr}')
        return(cp.stderr, cp.stdout, cp.returncode)
    else:
        logging.error(f'non-zero return code for cmd {cmdstr}')

def parse_mmls_output(out):
    out = str(out)
    lines = out.split('\\n')
    for line in lines:
        fields = line.split()
        if fields[0] == 'grid':
            kb = int(fields[2])
            quota = int(fields[3])
            limit = int(fields[4])
            logging.debug(f"kb={kb} quota={quota} limit={limit}")
    return (kb, quota, limit)


if __name__ == "__main__":
    FORMAT = '%(asctime)s (UTC) [ %(levelname)s ] %(filename)s:%(lineno)d %(name)s.%(funcName)s(): %(message)s'
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

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    if args.verbose:
        logging.getLogger().setLevel(logging.INFO)

    for fs in FSLIST:
        cmd = [QUOTACMD, '-j', f'{fs}', 'grid']
        (err, out, rc) = run_command_shell(cmd)
        (kb, quota, limit) = parse_mmls_output(out) 
        mb = kb / 1024
        gb =int( mb / 1024)
        qmb = quota / 1024
        qgb = int(qmb / 1024)
        free = qgb - gb
        print(f'{fs}\tused={gb} GB\tquota={qgb} GB\tfree={free} GB') 

