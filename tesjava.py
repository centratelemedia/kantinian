import os.path, subprocess
from subprocess import STDOUT, PIPE

def compile_java():
    subprocess.check_call(['javac','-cp','.:./libjava/*', 'com/company/Main.java'])

def execute_java(args):
    cmd = ['java','-cp','.:./libjava/*','com.company.Main', args[0], args[1]]
    proc = subprocess.Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    stdout, stderr = proc.communicate()
    print(str(stdout))

# compile_java()
execute_java(['img2json','fingerprint.bmp'])
# execute_java(['findMatch','fingerprint.bmp'])
