import os, psutil, time, signal, sqlite3, config, subprocess
from ruamel.yaml import YAML

import girder_client
def check_pid(pid):
    try:
        os.kill(pid, 0)
        
        if (psutil.Process(pid).status() == psutil.STATUS_ZOMBIE):
            return False

        return True
    except OSError:
        return False

def get_wf_status(pid, guid):
    if (pid == None):
        return "NOT_YET_EXECUTED"
    if (pid<0):
        return "TERMINATED"
    
    if (check_pid(pid)):
        return "RUNNING"
    
    input_path = os.path.join(config.INPUTS,guid)

    dir_name = os.path.join(config.RESULTS, guid)

    for root, directories, files in os.walk(dir_name):
        directories[:] = [d for d in directories if d not in ['tmp']]
        for filename in files:
            print(filename)
            return "FINISHED_OK"

    return "FINISHED_ERROR"


def terminate(GUID, pid, flag, timeout = 0):
    time.sleep(timeout)
    os.kill(pid, signal.SIGINT)
    conn = sqlite3.connect(config.DATABASE)
    c = conn.cursor()

    c.execute('UPDATE workflows SET PID='+str(flag)+' WHERE GUID="'+GUID+'"')

    conn.commit()
    conn.close()

def get_wf_pid(GUID):
    conn = sqlite3.connect(config.DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM workflows WHERE GUID="'+GUID+'"')
    row = c.fetchone()

    conn.close()
    if (row is None):
        return None

    return row[3]

def get_wf(GUID):
    conn = sqlite3.connect(config.DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM workflows WHERE GUID="'+GUID+'"')
    row = c.fetchone()

    conn.close()
    return row


def validate_yaml(input_dir):
    yaml = YAML()
    cwd = os.getcwd()
    os.chdir(input_dir)
    missing = list()
    with open('inputs.yaml') as file:
        
        yaml_in = yaml.load(file)
        for key in yaml_in:
            if (yaml_in[key] is not None and key!="girderIds"):
                if isinstance(yaml_in[key] , list):
                    for d in yaml_in[key]:
                        if (not os.path.isfile(d['path'])):
                            missing.append(d['path'])
                if isinstance(yaml_in[key],dict):
                    if (not os.path.isfile(yaml_in[key]['path'])):
                        missing.append(yaml_in[key]['path'])
    
    os.chdir(cwd)
    return missing

def getGirderIds(input_dir):
    yaml = YAML()
    cwd = os.getcwd()
    os.chdir(input_dir)
    with open('inputs.yaml') as file:
        os.chdir(cwd)
        yaml_in = yaml.load(file)
        if yaml_in.get('girderIds') is not None:
            return yaml_in['girderIds']
        else:
            return []

def downloadGirderFile(girderId, pathToInputs, girder_api_key):
    gc = girder_client.GirderClient(apiUrl=config.GIRDER_API)
    gc.authenticate(apiKey=girder_api_key)
    gc.downloadFile(girderId, pathToInputs)


def uploadToGirder(folderPath, girder_api_key, girder_parent_id):
    gc = girder_client.GirderClient(apiUrl=config.GIRDER_API)
    gc.authenticate(apiKey=girder_api_key)
    

    gc.upload(folderPath, girder_parent_id)

    ls = gc.listFolder(girder_parent_id, name=folderPath.split("/")[-1])
    return list(ls)[0]
