import os
import sys
import time
import subprocess
import random
import config as cfg

class Plopper:
    def __init__(self):
        # Initilizing global variables
        self.configfile = os.path.dirname(os.path.abspath(__file__))+'/config.txt'
        self.sourcefile = cfg.sourcefile
        self.outputdir = cfg.outputdir+"/tmp_files"
        self.compileoptions = cfg.compileoptions

        if not os.path.exists(self.outputdir):
            os.makedirs(self.outputdir)


    #Creating a dictionary using parameter label and value 
    def createDict(self, x, params):
        dictVal = {}
        for p, v in zip(params, x):
            dictVal[p] = v
        return(dictVal)

    #Replace the Markers in the source file with the corresponding Pragma values
    def plotValues(self, dictVal, inputfile, outputfile):
        with open(inputfile, "r") as f1:
            buf = f1.readlines()
                
        with open(outputfile, "w") as f2:
            for line in buf:
                flag = 0
                for key, value in dictVal.items():
                    if key in line:
                        flag = 1
                        if value != 'None': #For empty string options
                            modified = line.replace('#'+key, str(value))
                            f2.write(modified)
                if flag == 0: #To avoid writing the Marker
                    f2.write(line)

        # second iteration to replace the parameter values mentioned through markers in problem.py
        with open(outputfile, "r") as f1:
            buf = f1.readlines()
                
        with open(outputfile, "w") as f2:
            for line in buf:
                flag = 0
                for key, value in dictVal.items():
                    if key in line:
                        flag = 1
                        if value != 'None': #For empty string options
                            modified = line.replace('#'+key, str(value))
                            f2.write(modified)
                if flag == 0: #To avoid writing the Marker
                    f2.write(line)

    # Function to find the execution time of the interim file, and return the execution time as cost to the search module
    def findRuntime(self, x, params):
        interimfile = ""
        #exetime = float('inf')
        exetime = sys.maxsize
        counter = random.randint(1, 10001) # To reduce collision increasing the sampling intervals

        interimfile = self.outputdir+"/"+str(counter)+".c"

        # Generate intermediate file
        dictVal = self.createDict(x, params)
        self.plotValues(dictVal, self.sourcefile, interimfile)

        #compile and find the execution time
        tmpbinary = interimfile[:-2]

        #cmd1 = "clang -fopenmp -lm "+interimfile+" -o "+tmpbinary

        #cmd1 = "clang -fopenmp -DPOLYBENCH_TIME -O2 -I/home/vinu/workspace/surf/surf-ytopt/OpenMP_benchmark/utilities -I/home/vinu/workspace/surf/surf-ytopt/OpenMP_benchmark/atax "+interimfile+" /home/vinu/workspace/surf/surf-ytopt/OpenMP_benchmark/utilities/polybench.c -o "+tmpbinary

        #cmd1 = "clang -fopenmp -DPOLYBENCH_TIME -O2 -I/home/vinu/workspace/surf/surf-ytopt/OpenMP_benchmark/utilities -I/home/vinu/workspace/surf/surf-ytopt/OpenMP_benchmark/3mm "+interimfile+" /home/vinu/workspace/surf/surf-ytopt/OpenMP_benchmark/utilities/polybench.c -o "+tmpbinary

        #cmd1 = "clang -fopenmp -DPOLYBENCH_TIME -O2 -I/home/vinu/workspace/surf/surf-ytopt/OpenMP_benchmark/utilities -I/home/vinu/workspace/surf/surf-ytopt/OpenMP_benchmark/convolution-2d "+interimfile+" /home/vinu/workspace/surf/surf-ytopt/OpenMP_benchmark/utilities/polybench.c -o "+tmpbinary

        #cmd1 = "clang -fopenmp -lm -DPOLYBENCH_TIME -O2 -I/home/vinu/workspace/surf/surf-ytopt/OpenMP_benchmark/utilities -I/home/vinu/workspace/surf/surf-ytopt/OpenMP_benchmark/datamining/covariance "+interimfile+" /home/vinu/workspace/surf/surf-ytopt/OpenMP_benchmark/utilities/polybench.c -o "+tmpbinary

        cmd1 = "clang -fopenmp -lm -DPOLYBENCH_TIME -O2 -I/home/vinu/workspace/surf/surf-ytopt/OpenMP_benchmark/utilities -I/home/vinu/workspace/surf/surf-ytopt/OpenMP_benchmark/datamining/correlation "+interimfile+" /home/vinu/workspace/surf/surf-ytopt/OpenMP_benchmark/utilities/polybench.c -o "+tmpbinary
        cmd2 = tmpbinary+" "+self.compileoptions

        #Find the compilation status using subprocess
        compilation_status = subprocess.run(cmd1, shell=True, stderr=subprocess.PIPE)
        
        #Find the execution time only when the compilation return code is zero, else return infinity
        if compilation_status.returncode == 0 and len(compilation_status.stderr) == 0: #Second condition is to check for warnings
            execution_status = subprocess.run(cmd2, shell=True, stdout=subprocess.PIPE)
            exetime = float(execution_status.stdout.decode('utf-8'))

        #start = time.time()
        #end = time.time()
        #exetime = end - start

        return exetime #return execution time as cost

if __name__ == '__main__':
    params = ["LOOP1", "LOOP2", "LOOP3", "LOOP4"]
    x = ["#pragma omp for private (i)", "#pragma omp for private (i)", "#pragma omp for private (j)", "#pragma omp for private (j2, i)"]
    obj = Plopper()
    retVal = obj.findRuntime(x, params)
    print(retVal)