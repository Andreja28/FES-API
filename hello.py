from flask import Flask, request, send_file
from markupsafe import escape
import os, time, subprocess, glob, uuid, config, zipfile

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

    out_dir = os.path.join(os.path.abspath(config.RESULTS), str(GUID))
    os.mkdir(out_dir)

    if (req_data['type'] == 'cwl'):
        cwl_path = os.path.abspath(os.path.join(config.CWL,req_data['workflow'], 'workflow.cwl'))
        yaml_path = os.path.abspath(os.path.join(config.CWL,req_data['workflow'], 'inputs.yaml'))
        print(cwl_path)
        print(yaml_path)
        print(os.path.abspath(job_store_path))
        print(os.path.abspath(out_dir))
        subprocess.Popen(['bash cwl_run.sh', cwl_path, yaml_path, os.path.abspath(job_store_path), os.path.abspath(out_dir)])
    elif (req_data['type'] == 'toil'):
        toil_path = os.path.join(config.TOIL, 'main.py')

        subprocess.Popen(['python', config.TOIL +req_data["workflow"]+"/main.py", job_store_path,out_dir])
    else:
        return {'status':'FAILED' }

    
    #Add Error Handling
    return {'status':'OK',
             'workflow_id': str(GUID) }




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
