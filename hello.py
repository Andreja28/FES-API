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
    if (req_data['cwl_toil'] == 'cwl'):
        subprocess.Popen(['cwltoil','--jobStore','running/'+str(GUID), config.CWL +req_data["workflow"]+"/workflow.cwl", config.CWL +req_data['workflow']+"/inputs.yaml"])
    elif (req_data['cwl_toil'] == 'toil'):
        out_dir = os.path.join(os.path.abspath('results'), str(GUID))
        os.mkdir(out_dir)
        subprocess.Popen(['python', config.TOIL +req_data["workflow"]+"/main.py", "running/"+str(GUID),out_dir])
    else:
        return {'status':'FAILED' }

    
    #Add Error Handling
    return {'status':'OK',
             'workflow_id': str(GUID) }

