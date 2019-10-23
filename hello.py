
from flask import Flask
from markupsafe import escape
from flask import request
import os
import time
import glob


app = Flask(__name__)

@app.route('/echo', methods=['POST'])
def index():
    req_data = request.get_json()
    return {'status': 'OK',
            'your_request':req_data}

@app.route('/get_all_workflows', methods=['POST'])
def get_all_workflows():
    print(request)
    path_cwl = './workflows/cwl/'
    folders_cwl = [f.split('/')[-2] for f in glob.glob(path_cwl + "**/")]

    path_toil = './workflows/toil/'
    folders_toil = [f.split('/')[-2] for f in glob.glob(path_toil + "**/")]
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

    tstamp = time.time()
    
    #Run workflow script
    os.system('bash '+"./run_"+req_data["cwl_toil"]+".sh "+req_data["workflow"]+" "+str(tstamp))
    
    #Add Error Handling
    return {'status':'OK',
             'workflow_id': str(tstamp) }

