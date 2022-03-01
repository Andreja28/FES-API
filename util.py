import os, psutil, time, signal, sqlite3, config, subprocess, json
from ruamel.yaml import YAML
import girder_client
import xml.etree.ElementTree as ET
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
    parent = psutil.Process(pid)
    for child in parent.children(recursive=True):  # or parent.children() for recursive=False
        print(child)
        os.kill(child.pid, signal.SIGINT)
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
    girderFile = gc.getFile(girderId)
    gc.downloadItem(girderFile['itemId'], pathToInputs)

def uploadToGirder(folderPath, girder_api_key, girder_parent_id):
    gc = girder_client.GirderClient(apiUrl=config.GIRDER_API)
    gc.authenticate(apiKey=girder_api_key)
    

    gc.upload(folderPath, girder_parent_id)

    ls = gc.listFolder(girder_parent_id, name=folderPath.split("/")[-1])
    return list(ls)[0]

def ifReadOnlyWf(workflow):
    jsonFile = json.load(open("read-only-wfs.json",'r'))
    wfs = jsonFile['wfs']

    if (workflow in wfs):
        return True
    return False

def getWfOutputDir(GUID):
    return os.path.join(config.RESULTS,GUID)

def getDownloadLink(GUID,path):
    link = "get-output-file?GUID="+GUID+"&filepath="+path
    return link

def getZipLink(GUID):
    link = "get-results?GUID="+GUID
    return link

def getGirderOutputDir(wf):
    #print(wf)
    if (wf[4] is None):
        return wf[0]
    try:
        tree = ET.fromstring(wf[4])
        return tree.find('output').text
    except:
        return wf[0]

def deleteFolderFromGirder(wf, girder_api_key):
    
    try:
        gc = girder_client.GirderClient(apiUrl=config.GIRDER_API)
        userId = gc.authenticate(apiKey=girder_api_key)['_id']
        privateFolder = gc.loadOrCreateFolder('Private', userId, parentType="user")

        outFolder = gc.loadOrCreateFolder('workflow-outputs', privateFolder['_id'], parentType="folder")
        #wf = util.get_wf(guid)
        wfFolder = gc.loadOrCreateFolder(wf[2], outFolder['_id'], parentType="folder")

        outputFolder = gc.loadOrCreateFolder(util.getGirderOutputDir(wf), wfFolder['_id'], parentType="folder")
        gc.delete(outputFolder)
        for item in os.listdir(outputs):
            gc.upload(os.path.join(outputs,item), outputFolder['_id'])
    except:
        return