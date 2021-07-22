2021/07/22
- Add the Result file path
- Remove license_info

2021/06/17
- License info is modified for considering Ansys <= 19.2

2021/06/09
- Add license infomation variable
- inputfile full path handling using os.path.basename(inputfiles)
        - users can upload files with full path name, in Rescale, only file name is required
        - modify rm_command using uploaded_files variable
        
2021/05/25
- Job information file creation is added - will be used for job sharing
        job_info_filename = job_name+".job"
        job_info_file = open(job_info_filename, 'w')
        job_info_file.write(job_id)
        job_info_file.close()

- File download is added when the api script is killed by the user. In the LSF scheduler 'bkill -s 2 <jobID>' is required for downloading the intermediate files

- Job sharing api script is added

2021/05/24
- waiveSLA needs to be included

                    'hardware' : { 
                        'coresPerSlot' : core_per_slot,
                        'slots' : slot,
                        'walltime' : wtime,
                        'coreType' : coretype_code,
                        'type' : 'interactive',
                        },
                        'data' : { 
                            'waiveSla' : True
                        },
                    'inputFiles' : inputfiles_list



2021/05/23
- Ansys E2E : handling of spot-kill, need to be modified not to download when skot kill occurs
- waiveSLA needs to be included


CFX batch with E2E command :
python cfx_e2e_job.py --name=CFX-restart-test --nprocs=2 --inputs='2019R1_4cores.def 2019R1_4cores_001.res' --wtime=1
usage: cfx_e2e_job.py [-h] [--key KEY] [--platform PLATFORM] --name NAME [--coretype CORETYPE] --nprocs NPROCS [--ver VER] [--option OPTION] --inputs INPUTS --wtime WTIME
 
help

optional arguments:
  -h, --help            show this help message and exit
  --key KEY, -k KEY     API key
  --platform PLATFORM, -p PLATFORM
                        Platform address
  --name NAME, -n NAME  Job Name
  --coretype CORETYPE, -c CORETYPE
                        Coretype Name
  --nprocs NPROCS, -np NPROCS
                        Number of Cores
  --ver VER, -v VER     Ansys Version, 16.2.1 / 16.2 / 18.2 / 19.0 / 19.1 / 19.2 / 2019r1 / 2019r2 / 2019r3 / 2020r1 / 2020r2 / 2021r1
  --option OPTION, -o OPTION
                        CFX Option
  --inputs INPUTS, -i INPUTS
                        Input File Name
  --wtime WTIME, -w WTIME
                        Max. Wall Time
                        
                        
Fluent batch command :
python fluent_batch_job.py --name Fluent_Batch --nprocs 2 --inputs "run_plot.jou simple_aero_car.cas.gz" --journal run_plot.jou --wtime 1

usage: fluent_batch_job.py [-h] [--key KEY] [--platform PLATFORM] --name NAME [--coretype CORETYPE] --nprocs NPROCS [--ver VER] [--option OPTION]
                           --inputs INPUTS --journal JOURNAL --wtime WTIME
help

optional arguments:
  -h, --help            show this help message and exit
  --key KEY, -k KEY     API key
  --platform PLATFORM, -p PLATFORM
                        Platform address
  --name NAME, -n NAME  Job Name
  --coretype CORETYPE, -c CORETYPE
                        Coretype Name
  --nprocs NPROCS, -np NPROCS
                        Number of Cores
  --ver VER, -v VER     Ansys Version, 16.0 / 16.2 / 16.2.1 / 17.1.0-pcmpi / 17.2-pcmpi / 18.0 / 18.1 / 18.2 / 19.0 / 19.1 / 19.2 / 2019r1 / 2019r2 /
                        2019r3 / 2020r1 / 2020r2 / 2021r1
  --option OPTION, -o OPTION
                        Fluent Option
  --inputs INPUTS, -i INPUTS
                        Input File Name
  --journal JOURNAL, -j JOURNAL
                        Journal File
  --wtime WTIME, -w WTIME
                        Max. Wall Time

Ansys E2E command : python ansys_e2e_job.py --name Fluent_E2E --nprocs=4 --inputs="run_plot.jou simple_aero_car.cas.gz" --wtime 2
usage: ansys_e2e_job.py [-h] [--key KEY] [--platform PLATFORM] --name NAME [--coretype CORETYPE] --nprocs NPROCS [--ver VER] --inputs INPUTS --wtime WTIME

help

optional arguments:
  -h, --help            show this help message and exit
  --key KEY, -k KEY     API key
  --platform PLATFORM, -p PLATFORM
                        Platform address
  --name NAME, -n NAME  Job Name
  --coretype CORETYPE, -c CORETYPE
                        Coretype Name
  --nprocs NPROCS, -np NPROCS
                        Number of Cores
  --ver VER, -v VER     Ansys Version, 16.2.1 / 16.2 / 18.2 / 19.0 / 19.1 / 19.2 / 2019r1 / 2019r2 / 2019r3 / 2020r1 / 2020r2 / 2021r1
  --inputs INPUTS, -i INPUTS
                        Input File Name
  --wtime WTIME, -w WTIME
                        Max. Wall Time


Mechanical command : mechanical_batch_job.py --name Mechanical_Batch --nprocs 4 --inputs input_crankshaft.dat --wtime 1
usage: mechanical_batch_job.py [-h] [--key KEY] [--platform PLATFORM] --name NAME [--coretype CORETYPE] --nprocs NPROCS [--ver VER] [--option OPTION] --inputs INPUTS --wtime WTIME

help

optional arguments:
  -h, --help            show this help message and exit
  --key KEY, -k KEY     API key
  --platform PLATFORM, -p PLATFORM
                        Platform address
  --name NAME, -n NAME  Job Name
  --coretype CORETYPE, -c CORETYPE
                        Coretype Name
  --nprocs NPROCS, -np NPROCS
                        Number of Cores
  --ver VER, -v VER     Mechanical Version, 16.2 / 17.0 / 17.1 / 17.2 / 18.0 / 18.1 / 18.2 / 19.0 / 19.1 / 19.2 / 2019r1 / 2019r2 / 2019r3 / 2020r1 / 2020r2 / 2021r1
  --option OPTION, -o OPTION
                        Mechanical Option
  --inputs INPUTS, -i INPUTS
                        Input File Name
  --wtime WTIME, -w WTIME
                        Max. Wall Time

