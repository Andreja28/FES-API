from flask import Flask, request, send_file
from markupsafe import escape
import os, time, subprocess, glob, uuid, config, zipfile, sqlite3


app = Flask(__name__)

@app.route('/echo', methods=['POST'])
def index():
    req_data = request.get_json()
    return {'status': 'OK',
            'your_request':req_data}

@app.route('/get-workflows', methods=['POST'])
def get_all_workflows():
    folders_cwl = [f.split('/')[-2] for f in glob.glob(config.CWL  + "**/")]

    folders_toil = [f.split('/')[-2] for f in glob.glob(config.TOIL  + "**/")]
    return {
        "status": 'OK',
        "workflows": {
            "cwl": folders_cwl,
            "toil": folders_toil
        }
    }

@app.route('/create-workflow', methods=['POST'])
def create_wf():
    req_data = request.get_json()
    yaml_field = 'yaml'
    zip_field = 'input_zip'
    conn = sqlite3.connect('workflows')
    print(request.files[yaml_field])
    if yaml_field not in request.files or request.files[yaml_field].filename=='':
        return{
            'success': False,
            'message': 'Yaml file not selected.'
        }
    
    if zip_field not in request.files or request.files[zip_field].filename=='':
        return{
            'success': False,
            'message': 'Zip with input files not selected.'
        }

    yaml = request.files[yaml_field]
    inputs = request.files[zip_field]

    GUID = uuid.uuid4()

    in_dir = os.path.join(os.path.abspath(config.INPUTS), str(GUID))
    os.mkdir(in_dir)


    yaml.save(os.path.join(in_dir, 'inputs.yaml'))
    inputs.save(os.path.join(in_dir, 'inputs.zip'))

    with zipfile.ZipFile(os.path.join(in_dir, 'inputs.zip'), 'r') as zip_ref:
        zip_ref.extractall(in_dir)

    if (req_data['type'] == 'cwl'):
        typeId = 1
    else:
        typeId = 0
    c = conn.cursor()
    c.execute("INSERT INTO stocks VALUES ('"+GUID+"',"+typeId+","+req_data['workflow']+")")
    conn.commit()
    return {
        'success': True,
        'workflow_id':GUID
    }

@app.route('/run-workflow', methods=['POST'])
def run_workflow():
    req_data = request.get_json()

    GUID = req_data['GUID']
    conn = sqlite3.connect('workflows')
    c = conn.cursor()
    c.execute('SELECT * FROM workflows WHERE GUID="'+GUID+'"')
    row = c.fetchone()
    req_data['workflow'] = row[2]
    if (row == None):
        return {
            'success':False,
            "message": "Workflow doesn't exist."
        }
    c.execute('SELECT Type_Name FROM Types where ID='+str(row[1]))
    row = c.fetchone()
    req_data['type'] = row[0]
    
    
    input_path = os.path.join(config.INPUTS,GUID)
    job_store_path = os.path.join(config.RUNNING_WORKFLOWS,str(GUID))

    out_dir = os.path.join(os.path.abspath(config.RESULTS), str(GUID))
    os.mkdir(out_dir)

    if (req_data['type'] == 'cwl'):
        cwl_path = os.path.abspath(os.path.join(config.CWL,req_data['workflow'], 'workflow.cwl'))
        yaml_path = os.path.abspath(os.path.join(input_path, 'inputs.yaml'))
        
        subprocess.Popen(['timeout',str(req_data['timelimit']),'cwltoil','--jobStore',os.path.abspath(job_store_path), cwl_path, yaml_path], cwd=os.path.abspath(out_dir))
    elif (req_data['type'] == 'toil'):
        toil_path = os.path.join(config.TOIL, 'main.py')
        
        subprocess.Popen(['timeout',str(req_data['timelimit']),'python', config.TOIL +req_data["workflow"]+"/main.py", job_store_path,input_path,out_dir])
    else:
        return {'status':'FAILED' }

    
    #Add Error Handling
    return {'status':'OK',
             'workflow_id': str(GUID) }


@app.route('/get-status', methods=['GET'])
def get_status():
    GUID = request.args['workflow_id']
    job_store = os.path.abspath(os.path.join(config.RUNNING_WORKFLOWS, GUID))

    message = subprocess.check_output(['toil', 'status', job_store])

    return{
        "success": True,
        "message": message
    }


@app.route('/get-results', methods=['GET'])
def get_results():
    GUID = request.args['workflow_id']
    out_dir = os.path.join(config.RESULTS, GUID)
    job_store = os.path.join(config.RUNNING_WORKFLOWS, GUID)
    print('pozvao')
    if (os.path.isdir(out_dir)):
        print("out")
        if (not os.path.isdir(job_store)):
            print("job store")
            dir_name = os.path.join(config.RESULTS, GUID)
            zip_file = zipfile.ZipFile(dir_name+".zip", 'w')

            for root, directories, files in os.walk(dir_name):
                for filename in files:
                    filePath = os.path.join(root, filename)
                    zip_file.write(filePath)

            zip_file.close()
            print(dir_name)
            return send_file(dir_name+".zip")
            
            
        else:
            return {
                "success": False,
                "message": "Job not finished"
            }
    else:
        return{
            "success": False,
            "message": "Job doesn't exist."
        }

    return {}
