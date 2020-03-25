from flask import Flask, request, send_file
from markupsafe import escape
import os, sys, time, subprocess, glob, uuid, config, zipfile, sqlite3, shutil, signal, threading, multiprocessing, psutil
import util
from xml.etree.ElementTree import XML, fromstring

app = Flask(__name__)

@app.route('/echo', methods=['POST'])
def index():
    req_data = request.get_json()
    return {'status': 'OK',
            'your_request':req_data}

    
@app.route('/get-workflow-templates', methods=['POST'])
def get_workflow_templates():

    query = 'SELECT t.name, t.description, type.Type_Name FROM templates t JOIN Types type ON t.TypeID=type.ID'
    conn = sqlite3.connect(config.DATABASE)
    c = conn.cursor()
    c.execute(query)
    rows = c.fetchall()
    conn.close()
    
    cwl = []
    toil = []

    for row in rows:
        if (row[2] == 'cwl'):
            cwl.append({
                "workflow-template": row[0],
                "description": row[1]
            })
        if (row[2] == 'toil'):
            toil.append({
                "workflow-template": row[0],
                "description": row[1]
            })
    


    return {
        "status": 'OK',
        "templates": {
            "cwl": cwl,
            "toil": toil
        }
    }

@app.route('/template-description', methods=["GET", "POST", "PUT"])
def template_descriptions():
    if request.method == 'GET':
        template = request.args.get("workflow-template")
        if (template is None):
            return {
                "success": False,
                "message": "No workflow template specified."
            }
        
        query = 'SELECT description FROM templates WHERE name="'+template+'"'
        conn = sqlite3.connect(config.DATABASE)
        c = conn.cursor()
        c.execute(query)
        row = c.fetchone()
        description = row[0]
        conn.close()

        return {
            "success": True,
            "description": description
        }
    elif (request.method == "POST"):
        data = dict(request.form)
        template = data.get("workflow-template")
        description = data.get("description")
        type = data.get("type")

        if (template is None):
            return {
                "success": False,
                "message": "No workflow template specified."
            }

        if (description is None):
            return {
                "success": False,
                "message": "No description."
            }
        
        if (type is None):
            return {
                "success": False,
                "message": "No type specified."
            }
        TypeID = 0
        if (type == "cwl"):
            TypeID = 1
        elif (type == "toil"):
            TypeID = 2
        else:
            return{
                "succes": False,
                "message": "Uknown type"
            }

        query = 'SELECT description FROM templates WHERE name="'+template+'"'
        conn = sqlite3.connect(config.DATABASE)
        c = conn.cursor()
        c.execute(query)
        row = c.fetchone()

        if (row is None):
            query = 'INSERT INTO templates (name, description, TypeID) VALUES("'+template+'","'+description+'",'+str(TypeID)+')'
            try:
                c.execute(query)
                conn.commit()
                conn.close()
            except :
                return {
                    "success": False,
                    "message": "Server error."
                }

            return {
                "success": True
            }
            
        else:
            return {
                "success": False,
                "message": "Workflow template already exists."
            }
    else: 
        data = dict(request.form)
        template = data.get("workflow-template")
        description = data.get("description")

        if (template is None):
            return {
                "success": False,
                "message": "No workflow template specified."
            }

        if (description is None):
            return {
                "success": False,
                "message": "No description."
            }
        

        query = 'SELECT description FROM templates WHERE name="'+template+'"'
        conn = sqlite3.connect(config.DATABASE)
        c = conn.cursor()
        c.execute(query)
        row = c.fetchone()

        if (row is not None):
            query = 'UPDATE templates SET description = "'+description+'" WHERE name="'+template+'"'
            try:
                c.execute(query)
                conn.commit()
                conn.close()
            except :
                return {
                    "success": False,
                    "message": "Server error."
                }

            return {
                "success": True
            }
            
        else:
            return {
                "success": False,
                "message": "Workflow template doesn't exists."
            }



@app.route('/get-workflows', methods=["GET"])
def get_workflows():
    try:
        userID = request.args.get("userID")
        wf_type = request.args.get("type")
        template = request.args.get("workflow-template")
        status = request.args.get("status")
        
        
        query = 'SELECT w.*, t.Type_Name FROM workflows w join Types t on w.TypeId=t.ID'
        if (wf_type is not None and template is not None):
            query += ' WHERE Name="'+template+'" and Type_Name="'+wf_type+'"'
        elif (wf_type is not None):
            query += ' WHERE t.Type_Name="'+wf_type+'"'
        elif (template is not None):
            query += ' WHERE w.Name="'+template+'"'

        print(query)

        conn = sqlite3.connect(config.DATABASE)
        c = conn.cursor()
        c.execute(query)
        rows = c.fetchall()
        wfs = list()
        for row in rows:
            wf = dict()
            wf['workflow-template'] = row[2]
            wf['type']= row[5]
            wf['GUID'] = row[0]
            wf['status'] = util.get_wf_status(row[3], row[0])
            wf['metadata'] = row[4]

                       
            if (status is None and userID is None):
                wfs.append(wf)
            elif (status is None and userID is not None):
                if(wf['metadata'] is not None):
                    try:
                        tree = fromstring(wf['metadata'])
                    except:
                        continue
                    if tree.find('userID').text == userID:
                        wfs.append(wf)
            elif (status is not None and userID is None):
                if (wf['status']==status):
                    wfs.append(wf)
            else:
                if (wf['status']==status and wf['metadata'] is not None):
                    try:
                        tree = fromstring(wf['metadata'])
                    except:
                        continue
                    if tree.find('userID').text == userID:
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
            conn.close()
            return{
                "success": False,
                "message": "Workflow does't exist"
            }
        
        typeID = row[1]
        wf = dict()
        wf['workflow-template'] = row[2]
        wf['GUID'] = row[0]
        wf['status'] = util.get_wf_status(row[3], GUID)
        wf['metadata'] = row[4]

        
        c.execute('SELECT * FROM Types WHERE ID='+str(typeID))
        row = c.fetchone()
        if (row is not None):
            wf['type']=row[1]
        conn.close()
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

        if zip_field in request.files:
            if (not zipfile.is_zipfile(inputs)):
                return {
                    "success":False,
                    "message":"input_zip is not a .zip"
                }

        yaml.save(os.path.join(in_dir, 'inputs.yaml'))

        try:
            if zip_field in request.files:
                with zipfile.ZipFile(inputs, 'r') as zip_ref:
                    zip_ref.extractall(in_dir)
        except:
            shutil.rmtree(in_dir)
            return{
                "success": False,
                "message": "Bad .zip file."
            }

        
        missing = util.validate_yaml(in_dir)
        if len(missing) > 0:
            shutil.rmtree(in_dir)
            return {
                "success": False,
                "message": "Input files are missing",
                "missing": missing
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
        log_file_path = os.path.join(config.LOGS, str(GUID))

        out_dir = os.path.join(config.RESULTS, str(GUID))
        if (os.path.isdir(out_dir)):
            return{
                "success": False,
                "message": "Workflow has already been run."
            }

        if (req_data['type'] == 'cwl'):

            os.mkdir(out_dir)
            os.mkdir(log_file_path)
            log_file_path = os.path.join(log_file_path,"log.txt")
            cwl_path = os.path.abspath(os.path.join(config.CWL,req_data['workflow'], 'workflow.cwl'))
            yaml_path = os.path.abspath(os.path.join(input_path, 'inputs.yaml'))
            
            if (req_data['workflow'] == 'annotation'):
                process = subprocess.Popen(['cwltoil','--no-match-user','--no-read-only','--jobStore',os.path.abspath(job_store_path),'--logFile',os.path.abspath(log_file_path), cwl_path, yaml_path], cwd=os.path.abspath(out_dir))
            
            else:
                process = subprocess.Popen(['cwltoil','--jobStore',os.path.abspath(job_store_path),'--logFile',os.path.abspath(log_file_path), cwl_path, yaml_path], cwd=os.path.abspath(out_dir))
            pid = process.pid
            
            #th = threading.Thread(target=terminate(GUID,pid, -2, req_data['timelimit']))
            #th.start()
            c.execute('UPDATE workflows SET PID='+str(pid)+' WHERE GUID="'+GUID+'"')

            conn.commit()
        elif (req_data['type'] == 'toil'):

            os.mkdir(out_dir)
            os.mkdir(log_file_path)
            log_file_path = os.path.join(log_file_path,"log.txt")
            toil_path = os.path.join(config.TOIL, req_data["workflow"] , 'main.py')
            #print('timeout '+str(req_data['timelimit'])+' python '+ toil_path+" " +job_store_path+" "+input_path+" "+out_dir)
            #subprocess.Popen(['timeout',str(req_data['timelimit']),'python', config.TOIL +"/"+req_data["workflow"]+"/main.py", job_store_path,input_path,out_dir])

            process = subprocess.Popen(['python', toil_path, job_store_path,input_path,out_dir,'--logFile',os.path.abspath(log_file_path)])
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

@app.route('/get-log', methods=['GET'])
def get_log():
    GUID = request.args['GUID']
    if (GUID is None):
        return {
            "success":False,
            "message": "GUID field not set."
        }
    try:
        log_file_path = os.path.join(config.LOGS, str(GUID))
        log_file_path = os.path.join(log_file_path,"log.txt")
        if (os.path.isfile(log_file_path)):
            return send_file(log_file_path)
        else:
            return {
                "success": False,
                "message": "Log does not exist."
            }
    except:
        return {
            "success":False,
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
    
    status = util.get_wf_status(row[3], GUID)

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
        if (util.get_wf_status(util.get_wf_pid(GUID), GUID) == 'FINISHED_OK'):
            try:
                dir_name = os.path.join(config.RESULTS, GUID)
                zip_file = zipfile.ZipFile(dir_name+".zip", 'w')

                for root, directories, files in os.walk(dir_name):
                    directories[:] = [d for d in directories if d not in ['tmp']]
                    for filename in files:
                        filePath = os.path.join(root, filename)
                        zip_file.write(filePath, filename)

                zip_file.close()
                return send_file(dir_name+".zip")
            except:
                return {
                    "success": False,
                    "message": "Server error."
                }

        elif (util.get_wf_status(util.get_wf_pid(GUID), GUID) == 'FINISHED_ERROR'):
            return {
                "success": False,
                "message": "Job finished with error"
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
        log_dir = os.path.abspath(os.path.join(config.LOGS,GUID))

        if (os.path.isdir(jobStore)):
            shutil.rmtree(jobStore)
        if (os.path.isdir(input_dir)):
            shutil.rmtree(input_dir)
        if (os.path.isdir(output_dir)):
            shutil.rmtree(output_dir)
        if (os.path.isdir(log_dir)):
            shutil.rmtree(log_dir)
    
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
            if (util.get_wf_status(util.get_wf_pid(GUID), GUID) == 'FINISHED_OK'):
                
                zip_file = zipfile.ZipFile(wf[2]+"-out.zip", 'w')
                for root, directories, files in os.walk(out_dir):
                    directories[:] = [d for d in directories if d not in ['tmp']]
                    for filename in files:
                        filePath = os.path.join(root, filename)
                        zip_file.write(filePath, filename)

                zip_file.close()
                zip_wf.write(zip_file.filename)
                os.remove(zip_file.filename)
        
        log_dir = os.path.join(config.LOGS,GUID)

        if (os.path.isdir(log_dir)):
            if (os.path.isfile(os.path.join(log_dir,'log.txt'))):
                zip_wf.write(os.path.join(log_dir,'log.txt'), 'log.txt')

        zip_wf.close()
        
        return send_file(zip_wf.filename)
    except:
        return {
            "success": False,
            "message": "Server error."
        }
    

            
