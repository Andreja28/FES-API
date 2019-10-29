from flask import Flask, request
from markupsafe import escape
import os, time, subprocess, glob, uuid, config

app = Flask(__name__)

@app.route('/echo', methods=['POST'])
def index():
    req_data = request.get_json()
    return {'status': 'OK',
            'your_request':req_data}

@app.route('/get_all_workflows', methods=['POST'])
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

@app.route('/run_workflow', methods=['POST'])
def run_workflow():
    req_data = request.get_json()

    GUID = uuid.uuid4()
    job_store_path = os.path.join(config.RUNNING_WORKFLOWS,str(GUID))

    if (req_data['cwl_toil'] == 'cwl'):
        cwl_path = os.path.join(config.CWL,req_data['workflow'], 'workflow.cwl')
        yaml_path = os.path.join(config.CWL,req_data['workflow'], 'inputs.yaml')
        subprocess.Popen(['cwltoil','--jobStore',job_store_path, cwl_path, yaml_path])
    elif (req_data['cwl_toil'] == 'toil'):
        out_dir = os.path.join(os.path.abspath(config.RESULTS), str(GUID))
        toil_path = os.path.join(config.TOIL, 'main.py')

        os.mkdir(out_dir)
        subprocess.Popen(['python', config.TOIL +req_data["workflow"]+"/main.py", job_store_path,out_dir])
    else:
        return {'status':'FAILED' }

    
    #Add Error Handling
    return {'status':'OK',
             'workflow_id': str(GUID) }

