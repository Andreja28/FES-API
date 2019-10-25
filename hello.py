
from flask import Flask
from markupsafe import escape
from flask import request
import os
import time, subprocess
import glob
import config


app = Flask(__name__)

@app.route('/echo', methods=['POST'])
def index():
    req_data = request.get_json()
    return {'status': 'OK',
            'your_request':req_data}

@app.route('/get_all_workflows', methods=['POST'])
def get_all_workflows():
    print(request)
    folders_cwl = [f.split('/')[-2] for f in glob.glob(config.CWL_PATH + "**/")]

    folders_toil = [f.split('/')[-2] for f in glob.glob(config.TOIL_PATH + "**/")]
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

    path_to_wf = ""
    tstamp = time.time()
    if (req_data['cwl_toil'] == 'cwl'):
        subprocess.Popen(['cwltoil','--jobStore','running/'+str(tstamp), config.CWL_PATH+req_data["workflow"]+"/workflow.cwl", config.CWL_PATH+req_data['workflow']+"/inputs.yaml"])
    elif (req_data['cwl_toil'] == 'toil'):
        subprocess.Popen(['python', config.TOIL_PATH+req_data["workflow"]+"/main.py", "running/"+str(tstamp)])
    else:
        return {'status':'FAILED' }

    
    #Add Error Handling
    return {'status':'OK',
             'workflow_id': str(tstamp) }

