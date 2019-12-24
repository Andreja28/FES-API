from flask import Flask, request, send_file
from markupsafe import escape
import os, time, subprocess, glob, uuid, config, zipfile, sqlite3, shutil, signal, threading, multiprocessing, psutil
import util


app = Flask(__name__)

@app.route('/echo', methods=['POST'])
def index():
    req_data = request.get_json()
    return {'status': 'OK',
            'your_request':req_data}

    
@app.route('/get-workflow-templates', methods=['POST'])
def get_workflow_templates():
    folders_cwl = [f.split('/')[-2] for f in glob.glob(config.CWL  + "**/")]

    folders_toil = [f.split('/')[-2] for f in glob.glob(config.TOIL  + "**/")]
    return {
        "status": 'OK',
        "templates": {
            "cwl": folders_cwl,
            "toil": folders_toil
        }
    }

@app.route('/get-workflows', methods=["GET"])
def get_workflows():
    try:
        conn = sqlite3.connect(config.DATABASE)
        c = conn.cursor()
        c.execute('SELECT * FROM workflows')
        rows = c.fetchall()
        wfs = list()
        for row in rows:
            wf = dict()
            wf['workflow-template'] = row[2]
            wf['GUID'] = row[0]
            wf['status'] = util.get_wf_status(row[3])
            wf['metadata'] = row[4]
            wfs.append(wf)
        return {
            "success":True,
            "workflows":wfs
        }
    except:
        return {
            "success":False,
            "message":"Server error."
        }

@app.route('/get-workflow-info', methods=["GET"])
def get_workflow_info():

    GUID = request.args['GUID']

    if GUID is None:
        return{
            "success": False,
            "message": "GUID field not set."
        }

    try:
        conn = sqlite3.connect(config.DATABASE)
        c = conn.cursor()
        c.execute("SELECT * FROM workflows where GUID='"+GUID+"'")
        row = c.fetchone()

        if (row == None):
            return{
                "success": False,
                "message": "Error"
            }
                
        wf = dict()
        wf['workflow-template'] = row[2]
        wf['GUID'] = row[0]
        wf['status'] = util.get_wf_status(row[3])
        wf['metadata'] = row[4]
        return {
            "success":True,
            "workflow":wf
        }
    except:
        return {
            "success":False,
            "message":"Server error."
        }

@app.route('/create-workflow', methods=['POST'])
def create_wf():
    
    try:
        req_data = dict(request.form)
    except:
        return{
            "success": False,
            "message": "Bad request."
        }

    yaml_field = 'yaml'
    zip_field = 'input_zip'
    try:
        conn = sqlite3.connect(config.DATABASE)
        if yaml_field not in request.files or request.files[yaml_field].filename=='':
            return{
                'success': False,
                'message': 'Yaml file not selected.'
            }
        '''
        if zip_field not in request.files or request.files[zip_field].filename=='':
            return{
                'success': False,
                'message': 'Zip with input files not selected.'
            }
        '''
        

        if ('workflow-template' not in req_data.keys()):
            return{
                "success":False,
                "message": "Workflow template not selected."
            }
        
        if ('type' not in req_data.keys()):
            return{
                "success":False,
                "message": "type field not set"
            }
            
        if not (req_data['type'][0] == 'toil' or req_data['type'][0] == 'cwl'):
            return{
                "success": False,
                "message": "type field is not 'toil' or 'cwl'"
            }

        cwl_templates = [f.split('/')[-2] for f in glob.glob(config.CWL  + "**/")]

        toil_templates = [f.split('/')[-2] for f in glob.glob(config.TOIL  + "**/")]

        if (req_data['type'][0] == 'toil'):
            templates = [f.split('/')[-2] for f in glob.glob(config.TOIL  + "**/")]
        else:
            templates = [f.split('/')[-2] for f in glob.glob(config.CWL  + "**/")]
        
        if not (req_data['workflow-template'][0] in templates):
            return {
                "success": False,
                "message": "Workflow template doesn't exist."
            }

        yaml = request.files[yaml_field]
        if zip_field in request.files:
            inputs = request.files[zip_field]

        GUID = uuid.uuid4()
        in_dir = os.path.join(os.path.abspath(config.INPUTS), str(GUID))
        if (os.path.isdir(in_dir) == True):
            return{
                "success": False,
                "message": "GUID already exists. Try sending the same request again."
            }
        os.mkdir(in_dir)


        yaml.save(os.path.join(in_dir, 'inputs.yaml'))
        if zip_field in request.files:
            inputs.save(os.path.join(in_dir, 'inputs.zip'))

        try:
            if zip_field in request.files:
                with zipfile.ZipFile(os.path.join(in_dir, 'inputs.zip'), 'r') as zip_ref:
                    zip_ref.extractall(in_dir)
        except:
            shutil.rmtree(in_dir)
            return{
                "success": False,
                "message": "Bad .zip file."
            }

        if (req_data['type'][0] == 'cwl'):
            typeId = 1
        else:
            typeId = 2
        if ('metadata' in req_data.keys() and req_data['metadata'] is not None):
            metadata = req_data['metadata'][0]
        else:
            metadata = None
        
        c = conn.cursor()
        
        if (metadata is not None):
            c.execute("INSERT INTO workflows VALUES ('"+str(GUID)+"',"+str(typeId)+",'"+req_data['workflow-template'][0]+"',NULL, '"+metadata+"')")
        else:
            c.execute("INSERT INTO workflows VALUES ('"+str(GUID)+"',"+str(typeId)+",'"+req_data['workflow-template'][0]+"',NULL, NULL)")
        conn.commit()
        return {
            'success': True,
            'GUID':GUID
        }
    except:
        shutil.rmtree(in_dir)
        return{
            "success": False,
            "message": "Server error."
        }


@app.route('/run-workflow', methods=['POST'])
def run_workflow():
    req_data = request.get_json()

    if ('GUID' not in req_data.keys()):
        return{
            "success": False,
            "message": "GUID field not set."
        }

    GUID = req_data['GUID']
    try:
        conn = sqlite3.connect(config.DATABASE)
        c = conn.cursor()
        c.execute('SELECT * FROM workflows WHERE GUID="'+GUID+'"')
        row = c.fetchone()
        req_data['workflow'] = row[2]
        if (row == None):
            conn.close()
            return {
                'success':False,
                "message": "Workflow doesn't exist."
            }
    
        if (not row[3] == None):
            conn.close()
            return {
                "success": False,
                "message": "Workflow already run."
            }

        c.execute('SELECT Type_Name FROM Types where ID='+str(row[1]))
        row = c.fetchone()
        req_data['type'] = row[0]
    
    
        input_path = os.path.join(config.INPUTS,GUID)
        job_store_path = os.path.join(config.RUNNING_WORKFLOWS,str(GUID))

        out_dir = os.path.join(config.RESULTS, str(GUID))
        if (os.path.isdir(out_dir)):
            return{
                "success": False,
                "message": "Workflow has already been run."
            }
        os.mkdir(out_dir)

        if (req_data['type'] == 'cwl'):
            cwl_path = os.path.abspath(os.path.join(config.CWL,req_data['workflow'], 'workflow.cwl'))
            yaml_path = os.path.abspath(os.path.join(input_path, 'inputs.yaml'))
            
            process = subprocess.Popen(['cwltoil','--jobStore',os.path.abspath(job_store_path), cwl_path, yaml_path], cwd=os.path.abspath(out_dir))
            pid = process.pid
            
            #th = threading.Thread(target=terminate(GUID,pid, -2, req_data['timelimit']))
            #th.start()
            c.execute('UPDATE workflows SET PID='+str(pid)+' WHERE GUID="'+GUID+'"')

            conn.commit()
        elif (req_data['type'] == 'toil'):
            toil_path = os.path.join(config.TOIL, req_data["workflow"] , 'main.py')
            #print('timeout '+str(req_data['timelimit'])+' python '+ toil_path+" " +job_store_path+" "+input_path+" "+out_dir)
            #subprocess.Popen(['timeout',str(req_data['timelimit']),'python', config.TOIL +"/"+req_data["workflow"]+"/main.py", job_store_path,input_path,out_dir])

            process = subprocess.Popen(['python', toil_path, job_store_path,input_path,out_dir])
            pid = process.pid
            #th = threading.Thread(target=terminate(GUID,pid, -2, req_data['timelimit']))
            #th.start()
            c.execute('UPDATE workflows SET PID='+str(pid)+' WHERE GUID="'+GUID+'"')
            conn.commit()

        conn.close()
        return {
            "success": True
        }
    except:
        return{
            "success":True,
            "message": "Server error."
        }


@app.route('/get-status', methods=['GET'])
def get_status():
    GUID = request.args['GUID']
    if GUID is None:
        return{
            "success": False,
            "message": "GUID field not set."
        }
    try:
        conn = sqlite3.connect(config.DATABASE)
        c = conn.cursor()
        c.execute('SELECT * FROM workflows WHERE GUID="'+GUID+'"')
        row = c.fetchone()
            
        conn.close()
    except:
        return{
            "success": False,
            "message": "Server error.",
            "status": "Error"

        }
    if (row == None):
        return{
                "success": False,
                "message": "Workflow doesn't exist",
                "status": "Error"
            }
    
    status = util.get_wf_status(row[3])

    if (row[3] == None):
        return {
            'success':True,
            "message": "Workflow has not been started yet.",
            "status": status
        }
    if (row[3] == -1):
        return {
            'success': True,
            "message": "Workflow has been terminated by user.",
            "status": status
        }
    if (row[3] == -2):
        return{
            'success': True,
            "message": "Workflow has been terminated due to timeout.",
            "status": status
        }

    job_store = os.path.abspath(os.path.join(config.RUNNING_WORKFLOWS, GUID))
    

    message = subprocess.check_output(['toil', 'status', job_store])

    return{
        "success": True,
        "message": message,
        "status": status
    }


@app.route('/get-results', methods=['GET'])
def get_results():
    
    GUID = request.args['GUID']
    if request.args['GUID'] == None:
        return{
            "success": False,
            "message": "GUID field not set."
        }
    out_dir = os.path.join(config.RESULTS, GUID)
    if (os.path.isdir(out_dir)):
        if (util.get_wf_status(util.get_wf_pid(GUID)) == 'Finished'):
            try:
                dir_name = os.path.join(config.RESULTS, GUID)
                zip_file = zipfile.ZipFile(dir_name+".zip", 'w')

                for root, directories, files in os.walk(dir_name):
                    directories[:] = [d for d in directories if d not in ['tmp']]
                    for filename in files:
                        print(filename)
                        filePath = os.path.join(root, filename)
                        zip_file.write(filePath, filename)

                zip_file.close()
                return send_file(dir_name+".zip")
            except:
                return {
                    "success": False,
                    "message": "Server error."
                }
            
            
        else:
            return {
                "success": False,
                "message": "Job not finished"
            }
    else:
        return{
            "success": False,
            "message": "Workflow either doesn't exist or it hasn't been run."
        }



@app.route('/stop-workflow', methods=['POST'])
def stop_workflow():
    
    req_data = request.get_json()
    if 'GUID' not in req_data.keys():
        return{
            "success": False,
            "message": "GUID field not set."
        }
    GUID = req_data['GUID']
    try:
        
        conn = sqlite3.connect(config.DATABASE)
        c = conn.cursor()
        c.execute('SELECT * FROM workflows WHERE GUID="'+GUID+'"')
        row = c.fetchone()

        conn.close()
    except:
        return{
            "success": False,
            "message": "Server error."
        }

    if (row == None):
        return {
            "success": False,
            "message": "Workflow doesn't exist."
        }
    if (row[3] == None):
        return {
            "success": False,
            "message": "Workflow is not running"
        }
    
    if (row[3] == -1):
        return {
            'success': False,
            "message": "Workflow has been terminated by user."
        }
    if (row[3] == -2):
        return{
            'success': False,
            "message": "Workflow has been terminated due to timeout."
        }

    if (not util.check_pid(row[3])):
        return {
            "success": False,
            "message": "Workflow is finished."
        }
    else:
        util.terminate(GUID, row[3], -1)
        return {
            "success":True,
            "message": "Workflow terminated."
        }


@app.route('/delete-workflow', methods=['POST'])
def delete_wf():
    req_data = request.get_json()
    if 'GUID' not in req_data.keys():
        return{
            "success": False,
            "message": "GUID field not set."
        }
    try:
        GUID = req_data['GUID']
        conn = sqlite3.connect(config.DATABASE)
        c = conn.cursor()
        c.execute('SELECT * FROM workflows WHERE GUID="'+GUID+'"')
        row = c.fetchone()

        if (row == None):
            conn.close()
            return {
                "success": False,
                "message": "Workflow doesn't exist."
            }
        
        if (row[3] > 0 and util.check_pid(row[3])):
            conn.close()
            return {
                "success":False,
                "message": "Workflow is running"
            }

        jobStore = os.path.abspath(os.path.join(config.RUNNING_WORKFLOWS,GUID))
        input_dir = os.path.abspath(os.path.join(config.INPUTS, GUID))
        output_dir = os.path.abspath(os.path.join(config.RESULTS, GUID))

        if (os.path.isdir(jobStore)):
            shutil.rmtree(jobStore)
        if (os.path.isdir(input_dir)):
            shutil.rmtree(input_dir)
        if (os.path.isdir(output_dir)):
            shutil.rmtree(output_dir)
    
        c.execute('DELETE FROM workflows WHERE GUID="'+GUID+'"')
        conn.commit()
        conn.close()

        return {
            "success":True
        }
    except:
        return{
            "success": False,
            "message": "Server error."
        }

@app.route('/download-workflow', methods=['GET'])
def download_wf():
    try:
        GUID = request.args['GUID']
        if request.args['GUID'] == None:
            return{
                "success": False,
                "message": "GUID field not set."
            }
        
        wf = util.get_wf(GUID)
        if (wf is None):
            return{
                "success":False,
                "message": "Workflow doesn't exist."
            }
        
        out_dir = os.path.join(config.RESULTS, GUID)

        wf_dir = ""
        if (wf[1] == 1):
            wf_dir = os.path.join(config.CWL,wf[2])
        elif (wf[1] == 2):
            wf_dir = os.path.join(config.TOIL,wf[2])
        else:
            return{
                "success":False,
                "message": "Server error."
            }
        
        in_dir = os.path.join(config.INPUTS, GUID)
        zip_wf = zipfile.ZipFile(wf[2]+".zip", 'w')

        execute_path = ""
        for root, directories, files in os.walk(wf_dir):
            execute_path = root
            for filename in files:
                filePath = os.path.join(root,filename)

                zipFilePath = "./wf/"+filePath.split(root)[1]
                zip_wf.write(filePath, zipFilePath)
        
        input_path = ""
        for root,directories,files in os.walk(in_dir):
            input_path = root
            for filename in files:
                filePath = os.path.join(root, filename)
                zipFilePath = "./inputs/"+filePath.split(root)[1]
                zip_wf.write(filePath, zipFilePath)
        
        f = open('start.sh','w')
        f.write("mkdir outputs\n")
        f.write("cd outputs\n")
        command = ""
        if (wf[1] == 1):
            execute_file = os.path.join('..','wf', 'workflow.cwl')
            input_file = os.path.join('..','inputs', 'inputs.yaml')
            command = command+"cwltoil "
            command = command+execute_file+" "+input_file
        elif (wf[1] == 2):
            execute_file = os.path.join('wf', 'main.py')
            input_file = os.path.join('inputs', 'inputs.yaml')
            command = command+"python "
            command = command+execute_file+" . "+input_file+ " ."

        f.write(command)
        f.close()

        zip_wf.write('start.sh')

        
        if (os.path.isdir(out_dir)):
            if (util.get_wf_status(util.get_wf_pid(GUID)) == 'Finished'):
                
                zip_file = zipfile.ZipFile(wf[2]+"-out.zip", 'w')
                for root, directories, files in os.walk(out_dir):
                    directories[:] = [d for d in directories if d not in ['tmp']]
                    for filename in files:
                        filePath = os.path.join(root, filename)
                        zip_file.write(filePath, filename)

                zip_file.close()
                zip_wf.write(zip_file.filename)
                os.remove(zip_file.filename)
                    
        zip_wf.close()
        return send_file(zip_wf.filename)
    except:
        return {
            "success": False,
            "message": "Server error."
        }
    

            
