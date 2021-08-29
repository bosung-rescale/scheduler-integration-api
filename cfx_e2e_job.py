#!/usr/bin/env python

import requests
import json
import sys
import time
import os
import datetime
import getpass
import argparse
import signal
import platform
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

def download_files() :
    global rescale_platform
    global job_id
    global my_token
    global job_name

    list_output_files_url = rescale_platform + '/api/v2/jobs/' + job_id + '/files/'

    current_page = 1
    file_count = 0
    last_page = False
    current_dir = os.getcwd()

    list_output_files = requests.get(
        list_output_files_url,
        headers={'Authorization': my_token}
    )
    list_output_files_dict = json.loads(list_output_files.text)

    total_file_size = 0
    files_count = list_output_files_dict['count']

    if files_count != 0 :

        top_dir = job_name + '/'

        if not(os.path.exists(top_dir)) :
            os.makedirs(top_dir)

        while (not(last_page)):

            list_output_files = requests.get(
                list_output_files_url,
                params = {'page' : current_page},
                headers={'Authorization': my_token}
            )
            list_output_files_dict = json.loads(list_output_files.text)

            for label in list_output_files_dict['results'] :
                path = ''

                os.chdir(current_dir)
                file_count += 1
                total_file_size += label['decryptedSize']
                relative_path = label['relativePath'].rsplit('/',1)[0]

                if relative_path != label['relativePath'] :
                    path = relative_path

                if not os.path.exists(top_dir + path) :
                    os.makedirs(top_dir + path)

                os.chdir(top_dir + path)

                downloadUrl = label['downloadUrl']
                filename = os.path.basename(label['relativePath'])

                response = requests.get(
                    downloadUrl,
                    headers={'Authorization': my_token}
                )

                with open(filename, 'wb') as fd:
                    for chunk in response.iter_content(chunk_size=100):
                        fd.write(chunk)
                print (file_count, label['path']+' downloaded')

            #print(json.dumps(list_output_files_dict, indent=2, separators=(',',': ')))

            current_page += 1
            if (list_output_files_dict['next'] == None):
                last_page = True

    print ('Total ' + str(file_count) + ' files, %.3f MB downloaded'%(total_file_size/1024/1024))

    return

def kill_job() :
    global rescale_platform
    global job_id
    global my_token

    job_stop_url = rescale_platform + '/api/v2/jobs/' + job_id + '/stop/'
    job_status = requests.post(
        job_stop_url,
            headers={'Authorization': my_token} 
    )  

    job_status_url = rescale_platform + '/api/v2/jobs/' + job_id + '/statuses/'

    prev_status = None
    current_status = None
    job_completed = False

    while job_completed == False :
        prev_status = current_status
        job_status = requests.get(
            job_status_url,
            headers={'Authorization': my_token} 
        )
        job_status_dict = json.loads(job_status.text)
        current_status = job_status_dict['results'][0]['status']

        if current_status == 'Completed' : 
            print ('Job ' + job_id + ' : ' + current_status)
            job_completed = True

        time.sleep(5)   

    download_files()

    return

def getTERM(sigNum, stackFrame):
    global job_id
    #print('signal catch', sigNum)

    if (job_id != None) :
         kill_job()

    print('killed by the user ', sigNum)
    exit(0)

def dcv_info(job_name) :
    global rescale_platform
    global job_id
    global my_token

    instance_info_url = rescale_platform + '/api/v2/jobs/'+job_id+'/instances/' 

    instance_info = requests.get(
        instance_info_url,
        headers = {'Authorization': my_token}
    )   

    if (instance_info.text != None) :
        instance_info_dict = json.loads(instance_info.text)

    rescale_platform_addr = rescale_platform.split('/')[-1]
    cluster_id = instance_info_dict['results'][0]['clusterId']
    pub_hostname = instance_info_dict['results'][0]['publicHostname']
    pub_ipaddr = instance_info_dict['results'][0]['publicIp']
    instance_username = instance_info_dict['results'][0]['username']

    dcv_pass_url = rescale_platform + '/api/v2/clusters/'+cluster_id+'/remote_viz_hardware_settings/password/'
    dcv_pass_info = requests.post(
        dcv_pass_url,
        headers = {'Authorization': my_token}
    )   

    dcv_pass_dict = json.loads(dcv_pass_info.text)
    instance_password = dcv_pass_dict['data']

    #print(instance_info_dict)
    #print(dcv_pass_dict)

    time.sleep(120)
    dcv_connection_filename = job_name+".dcv"
    dcv_connection_file = open(dcv_connection_filename, 'w')

    dcv_connection_file.write('[version]\n')
    dcv_connection_file.write('format=1.0\n')
    dcv_connection_file.write('[connect]\n')
    dcv_connection_file.write('host='+rescale_platform_addr+'\n')
    dcv_connection_file.write('port=443\n')
    dcv_connection_file.write('weburlpath=/in-browser-desktops/'+cluster_id+'/\n')
    dcv_connection_file.write('user='+instance_username+'\n')
    dcv_connection_file.write('password='+instance_password+'\n')

    dcv_connection_file.close()
   
    return pub_hostname

# Coretype check
def coretype_check(coretype_name) :
    global rescale_platform
    global my_token

    coretypes_url = rescale_platform + '/api/v2/coretypes/'
    current_page = 1
    coretype_check = False
    last_page = False

    while (not(last_page)):
        core_info = requests.get(
            coretypes_url,
            params = {'page' : current_page},
            headers = {'Authorization': my_token}
        )
        core_info_dict = json.loads(core_info.text)

        for label in core_info_dict['results'] :
            if label['name'].strip().lower().replace(" ","") == coretype_name.lower().replace(" ","") :
                coretype_code = label['code'].strip()
                cores = label['cores']
                coretype_check = True
                
        current_page += 1

        if (coretype_check == True) :
            #print (coretype_name + ' is used for analysis')
            break

        if (core_info_dict['next'] == None):
            last_page = True

    if (coretype_check == False) :
        print (coretype_name + ' is not supported. check the core type name')
        exit(1)

    return coretype_code, cores

# Analysis software check 
def analysis_check(code_name, version_code) :
    global rescale_platform
    global my_token

    analyses_url = rescale_platform + '/api/v2/analyses/'

    current_page = 1
    last_page = False
    code_name_check = False
    version_code_check = False

    #json = json.dumps(software_info_dict, indent=2, separators=(',',': '))
    #print(json)

    while (not(last_page)):
        software_info = requests.get(
            analyses_url,
            params = {'page' : current_page},
            headers = {'Authorization': my_token}
        )
        software_info_dict = json.loads(software_info.text)

        for label in software_info_dict['results'] :
            if label['code'].strip() == code_name:
               code_name_check = True
            for label_version in label['versions'] :
               if label_version['versionCode'].strip() == version_code:
                   version_code_check = True

        current_page += 1

        if (code_name_check and version_code_check) :
            #print (code_name + ' ' + version_code + ' is used for analysis')
            break

        if (software_info_dict['next'] == None):
            last_page = True

    if code_name_check  == False :
        print (code_name + ' is not supported. check the analysis software')
        exit(1)

    if version_code_check == False :
        print (version_code + ' is not supported. check the analysis software version')
        exit(1)

    return

if __name__ == '__main__':
    global rescale_platform 
    global job_id 
    global my_token 
    global job_name

    signal.signal(signal.SIGINT, getTERM)
    signal.signal(signal.SIGTERM, getTERM)

    rescale_platform = None
    job_id = None
    my_token = None

    parser = argparse.ArgumentParser(description='help')

    parser.add_argument('--key', '-k', required=False, help='API key')
    parser.add_argument('--platform', '-p', required=False, help='Platform address')
    parser.add_argument('--name', '-n', required=True, help='Job Name')
    parser.add_argument('--coretype', '-c', required=False, default='Emerald', help='Coretype Name')
    parser.add_argument('--nprocs', '-np', required=True, help='Number of Cores')
    parser.add_argument('--ver', '-v', required=False, default='2020r1', help='Ansys Version, \
                         16.2.1 / 16.2 / 18.2 / 19.0 / 19.1 / 19.2 / 2019r1 / 2019r2 / 2019r3 / 2020r1 / 2020r2 / 2021r1')
    parser.add_argument('--option', '-o', required=False, default='', help='CFX Option')
    parser.add_argument('--inputs', '-i', required=True, help='Input File Name')
    parser.add_argument('--otherfiles', '-of', required=False, help='Other File Names')
    parser.add_argument('--wtime', '-w', required=True, help='Max. Wall Time')

    args = parser.parse_args()

    api_key = None
    rescale_platform = None

    if (platform.system() == 'Windows' ):
        apiconfig_file = os.environ['USERPROFILE']+"\\.config\\rescale\\apiconfig"
    else:
        apiconfig_file = os.environ['HOME']+"/.config/rescale/apiconfig"

    if (os.path.isfile(apiconfig_file)):
        f = open(apiconfig_file, 'r')
        lines = f.readlines()
        f.close()

        rescale_platform =lines[1].split('=')[1].rstrip('\n').lstrip().replace("'","")
        api_key =lines[2].split('=')[1].rstrip('\n').lstrip().replace("'","")

    if (args.key != None):
        api_key = args.key
    if (args.platform != None):
        rescale_platform = args.platform

    if (api_key == None) :
        print("API key should be defined in the $HOME/.config/rescale/apiconfig or --key option")
    if (rescale_platform == None) :
        print("Platform address should be defined in the $HOME/.config/rescale/apiconfig or --rescale_platform option")
        exit(1)

    my_token = 'Token ' + api_key

    batch_name = args.name
    num_of_cores = int(args.nprocs)
    cfx_option = args.option
    input_file = args.inputs
    other_file = args.otherfiles
    wtime = int(args.wtime)
    coretype_name = args.coretype

# Coretype & the numbers of cores will be setup according to the core type
    coretype_code, cores = coretype_check(coretype_name)
    if num_of_cores in cores :
        core_per_slot = num_of_cores
    else :
        for core in cores:
            if (num_of_cores < core) :
                core_per_slot = core
                break
            else:
                core_per_slot = ((num_of_cores-1) // cores[-1] + 1) * cores[-1]
    slot = '1'

# Analysis version check
    code_name = 'ansys_e2e_desktop'  # Ansys Interactive Workflow 
    version_code = args.ver         
    analysis_check(code_name, version_code)

# job_name is set as the job_submisstion time 
    now = datetime.datetime.now()
    current_user = getpass.getuser()
    job_name = current_user+'@'+batch_name+'@'+now.strftime('%Y%m%d-%H%M%S') # Rescale job name setup

# Input File upload
    upload_url = rescale_platform + '/api/v2/files/contents/'

    input_files = input_file.split()
    inputfile_id = {}
    inputfiles_list = []
    def_file = ''
    res_file = ''
    uploaded_files = ''

    if (other_file != None):
        other_files = other_file.split()
        for i in range(len(other_files)):
            input_files.append(other_files[i])
    else:
        other_file = ''

    for i in range(len(input_files)) :
        try:
            if os.path.splitext(input_files[i])[-1] == '.def' :
                def_file = os.path.basename(input_files[i])
            if os.path.splitext(input_files[i])[-1] == '.res' :
                res_file = os.path.basename(input_files[i])

            with open(input_files[i], 'rb') as ifile:
#                def cb_print_status(monitor):
#                    sys.stdout.write('\r'+input_files[i]+' {:.2f}% uploaded ({} of {} bytes)'.format(
#                        100.0 * monitor.bytes_read / monitor.len, monitor.bytes_read, monitor.len))
#                    sys.stdout.flush()

                encoder = MultipartEncoder(fields={'file': (ifile.name, ifile)})
#                monitor = MultipartEncoderMonitor(encoder, cb_print_status)
                monitor = MultipartEncoderMonitor(encoder)

                upload_file = requests.post(
                    upload_url,
                    data=monitor,
                    headers={'Authorization' : my_token,'Content-Type': encoder.content_type})

                if (upload_file.status_code == 201) :
                    print('- ' + input_files[i] + ' uploaded')
                    uploaded_files = uploaded_files + ' ' + os.path.basename(input_files[i])
                    upload_file_dict = json.loads(upload_file.text)
                    inputfile_id[i] = upload_file_dict['id']
                    inputfiles_list.append({'id':inputfile_id[i]})
                else:
                    print('-  ' + input_files[i] + ' upload failed')
                    exit(1)

        except FileNotFoundError as e:
            print (e) 
            exit(1)

    #json = json.dumps(upload_file_dict, indent=2, separators=(',',': '))
    #print(json)

# job_command set
    if (res_file == '') :
#        command = 'cfx5solve -def ' + def_file + ' -part ' + str(core_per_slot) + ' '+ cfx_option + ' \n'
        command = 'cfx5solve -def '+def_file+' -part '+str(num_of_cores)+' '+cfx_option+' \n'
        rm_command = 'rm -f '+ uploaded_files + '\n'
    else :
        sed_command = 'cfx5cmds -read -def ' + def_file + ' -text ' + def_file + '.ccl\n' \
                    + 'sed -i "s/=.*.' + res_file + '/= ' + res_file + '/" ' + def_file + '.ccl\n' \
                    + 'cfx5cmds -write -def '+ def_file + ' -text ' + def_file + '.ccl\n'

        command = sed_command \
                + 'cfx5solve -def '+ def_file +' -part ' + str(core_per_slot) + ' -initial-file ' + res_file + ' ' + cfx_option + ' \n'
        rm_command = 'rm -f '+ uploaded_files + ' ' + def_file+'.ccl\n'

#    zip_command = 'zip -r -q ' + job_name + '_out.zip * -x process_output.log -x tmp/* \n' 
#    zip_command = zip_command + 'find . -name "*.zip" -prune -o -name "*.log" -prune -o -exec rm -rf {} \;'
    zip_command = ''
    job_command = command + rm_command + zip_command

    print('\nJob Information')
    print('- input_file : ' + input_file)
    print('- other_file : ' + other_file)
    print('- code_name : ' + code_name)
    print('- version_code : ' + version_code)
    print('- coretype_name : ' + coretype_name)
    print('- num_of_cores / core_per_slot : ' + str(num_of_cores) + ' / ' + str(core_per_slot))
    print('- slot : ' + slot)
    print('- wall time : ' + str(wtime))
    print('- job_name : ' + job_name)
    print('- job_command : ')
    print(job_command)

    sys.stdout.flush()
    sys.stderr.flush()
    
# Job setup

    if version_code in ['16.0', '16.2', '16.2.1','17.1.0-pcmpi','17.2-pcmpi','18.0','18.1','18.2','19.0','19.1','19.2'] :
        license_info = { 
                        'ANSYSLMD_LICENSE_FILE': '1055@test',
                        'ANSYSLI_SERVERS': '1055@test',
                        'LM_PROJECT': 'ANSYSLI_LCP',
                        'ANSYSLI_LCP': '0',
                        'ANSYS_ELASTIC_CLS': ''
                    }
    else:
        license_info = { 
                        'ANSYSLMD_LICENSE_FILE': '1055@test',
                        'ANSYSLI_SERVERS': '1055@test',
                        'LM_PROJECT': 'ANSYSLI_LCP',
                        'ANSYSLI_LCP': '1',
                        'ANSYS_ELASTIC_CLS': 'xxxxxx:yyyyyy',
                    }

    projectid = ""  # Input the project ID

    job_url = rescale_platform + '/api/v2/jobs/'
    job_setup = requests.post(
        job_url,
        json = {
            'name' : job_name,
            'isLowPriority' : True,
            'projectId' : projectid,
            'jobanalyses' : [
                {
#                    'envVars' : license_info,
                    'useRescaleLicense' : False,
                    'onDemandLicenseSeller' : { 
                        'code' : 'rescale-trial',
                        'name' : 'Rescale Trial'
                    },
                    'useMPI' : False,
                    'command' : job_command,
                    'analysis' : {
                        'code' : code_name,
                        'version' : version_code
                    },
                    'hardware' : {
                        'coresPerSlot' : core_per_slot,
                        'slots' : slot,
                        'walltime' : wtime,
                        'coreType' : coretype_code,
                        'type' : 'interactive',
                        },
#                        'data' : { 
#                            'waiveSla' : True
#                        },
                    'inputFiles' : inputfiles_list
                },
                {
                    'useRescaleLicense' : False,
                    'useMPI' : False,
                    'command' : '', 
                    'flags' : { 
                        'igCv' : True,
                        'runForever' : True
                    },
                    'analysis' : { 
                        'code' : "rescale-ckpt-e2e",
                        'version' : "rescale_ckpt_e2e_4H"
                    },
                    'hardware' : { 
                        'coresPerSlot' : core_per_slot,
                        'slots' : slot,
                        'walltime' : wtime,
                        'coreType' : coretype_code,
                        'type' : 'interactive',
                        },
                    'inputFiles' : []
                },
            ]
        },
        headers={'Content-Type' : 'application/json',
                 'Authorization' : my_token}
    )

    if (job_setup.status_code != 201) :
        print (job_setup.text)
        print ('Job creation failed')
        exit(1)

    job_setup_dict = json.loads(job_setup.text)
    job_id = job_setup_dict['id'].strip()

    #print(json.dumps(job_setup_dict, indent=2, separators=(',',': ')))

# Submit Job
    job_submit_url = rescale_platform + '/api/v2/jobs/' + job_id + '/submit/'
    submit_job = requests.post(
        job_submit_url,
        json={'waiveSla' : True},
        headers={'Authorization': my_token},
    )
    if (submit_job.status_code == 200) :
        print ('Job ' + job_id + ' : submitted')
        job_info_filename = job_name+".job"
        job_info_file = open(job_info_filename, 'w')
        job_info_file.write(job_id)
        job_info_file.close()

        if (platform.system() == 'Windows' ):
            job_url_filename = job_name+".url"
            job_url_file = open(job_url_filename, 'w')
            url = 'URL='+rescale_platform+'/jobs/'+job_id+'/runs/1/results/'
            url = '[InternetShortcut]\n'+url
        else:
            job_url_filename = job_name+".desktop"
            job_url_file = open(job_url_filename, 'w')
            url = 'URL='+rescale_platform+'/jobs/'+job_id+'/runs/1/results/'
            url = '[Desktop Entry]\nType=Link\n'+url

        job_url_file.write(url)
        job_url_file.close()

    else:
        print ('Job submission Failed')
        exit(1)

    sys.stdout.flush()
    sys.stderr.flush()

# Monitoring Job
    job_status_url = rescale_platform + '/api/v2/jobs/' + job_id + '/statuses/'
    instance_info_url = rescale_platform + '/api/v2/jobs/' + job_id + '/instances/'

    prev_status = None
    current_status = None
    job_completed = False
    dcv_file_created = False

    # CFX out file name
    if (os.path.splitext(def_file)[0] == res_file.rsplit('_',1)[0]) :
        out_num = str(int(res_file.split('_')[-1].split('.')[0])+1).zfill(3)
        cfx_tail_out = res_file.rsplit('_',1)[0]+'_'+out_num+'.out'
    else :
        cfx_tail_out = os.path.splitext(def_file)[0]+'_001.out'

    while job_completed == False :
        prev_status = current_status
        job_status = requests.get(
            job_status_url,
            headers={'Authorization': my_token} 
        )
        job_status_dict = json.loads(job_status.text)
        current_status = job_status_dict['results'][0]['status']

        if (current_status != prev_status) :
            print ('Job ' + job_id + ' : ' + current_status)

            while current_status == 'Executing' :
                if dcv_file_created == False :
                    pub_hostname = dcv_info(job_name)
                    dcv_file_created = True
                    print('\nDCV connection file is created.')

                # Live tail of CFX out
                tail_file_url = rescale_platform + '/api/v2/jobs/' + job_id + '/runs/1/tail/shared/' + cfx_tail_out
                tail_file = requests.get(
                    tail_file_url,
                    headers={'Authorization': my_token},
                    params={'lines':20}
                )

                try : 
                    tail_file_dict = json.loads(tail_file.text)
                    print(json.dumps(tail_file_dict['lines'],indent=2))
                except:
                    print('Waiting.....')

                sys.stdout.flush()
                sys.stderr.flush()

                time.sleep(5)

                prev_status = current_status
                job_status = requests.get(
                    job_status_url,
                    headers={'Authorization': my_token} 
                )
                job_status_dict = json.loads(job_status.text)
                current_status = job_status_dict['results'][0]['status']

                # Spot-kill handling
                instance_info = requests.get(
                    instance_info_url,
                    headers = {'Authorization': my_token}
                )   
                if (instance_info.text != None) :
                    instance_info_dict = json.loads(instance_info.text)
                    current_pub_hostname = instance_info_dict['results'][0]['publicHostname']

#                if (current_pub_hostname != pub_hostname) :
#                    print('Cluster is restarted')
#                    time.sleep(90)
#                    dcv_file_created = False

                if (current_pub_hostname != pub_hostname) :
                    print('E2E cluster is restarted and shutdown')
                    kill_job()
                    exit (0) 

                # Spot-kill handling : DCV session password is not changed after restart
        
            # End of Live tail 

        if current_status == 'Completed':
           job_completed = True

        sys.stdout.flush()
        sys.stderr.flush()

        time.sleep(5)   
    
    if job_completed != True :
        print('Job execution Failed')
        exit(1)

    download_files()
