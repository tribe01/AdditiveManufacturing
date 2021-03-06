#!/usr/bin/env python
import os, sys
import optparse
from puqutil import dump_hdf5
from subprocess import call

usage = "usage: %prog --np cpus --on_time x --power y --wait_time z" 
parser = optparse.OptionParser(usage)
parser.add_option("--np", type=int)
parser.add_option("--on_time", type=float)
parser.add_option("--power", type=float)
parser.add_option("--wait_time", type=float)
(options, args) = parser.parse_args()

# get the parameters from PUQ
cpus = options.np
x = options.on_time
y = 200 #options.power
z = 10 #options.wait_time

# generate input path file
PUQ_dir = '/home/n22/IN718/PUQ_test/'
case_folder = '5_spot'
scripts_dir = PUQ_dir + 'scripts'
launch_dir = PUQ_dir + case_folder
result_dir = PUQ_dir + case_folder +'/test_output' 
cmd = ['./xyzdtp_gen.out', str(x), str(y), str(z)]
call(cmd, cwd=os.getcwd())

# copy the input path file
#cmd =['cp', 'xyzdtp.dat', '../'+ case_folder +'/']
#call(cmd, cwd=scripts_dir)

# launch the simulation
truchas_binary = '/home/srdjans/projects/truchas-2.8.0-RC/install/linux.x86_64.intel.parallel.opt/bin/t-linux.x86_64.intel.parallel.opt-2.8.0'
cmd = ['mpirun', '-np', str(cpus), truchas_binary, 'test.inp']
call(cmd, cwd=launch_dir)

# postprocess the results
cmd = ['bash', scripts_dir+'/postprocessor.sh']
call(cmd, cwd=result_dir)

# extract quantity of interest
with open(result_dir+'/PHI.txt', 'r') as fin:
    lines = fin.readlines()
    qoi = float(lines[0].split(':')[1].lstrip(' ').strip('\n'))

# report the quantities of interest to PUQ
if qoi > 1:
    print 'Case failed due to one or more errors'
    sys.exit()
dump_hdf5('volume_fraction_of_equiaxed_grains', qoi)
