import uuid
import zipfile
import config 
import os
from ruamel.yaml import YAML
import shutil

def generate_GUID():
    GUID = str(uuid.uuid4())

    if GUID not in list_dirs():
        return GUID
    else:
        return generate_GUID()
    
def validate_GUID(guid):
    try:
        uuid_obj = uuid.UUID(guid, version=4)
        return str(uuid_obj) == guid
    except ValueError:
        return False
    
def list_dirs(path = config.INPUTS_DIR):
    return [dir for dir in os.listdir(path) if os.path.isdir(os.path.join(path, dir))]

def get_workflow_dirs(guid):
    inputs_path = os.path.join(config.INPUTS_DIR, guid)
    if not os.path.exists(inputs_path):
        os.makedirs(inputs_path)

    logs_path = os.path.join(config.LOGS_DIR, guid)
    if not os.path.exists(logs_path):
        os.makedirs(logs_path)

    results_dir = os.path.join(config.RESULTS_DIR, guid)
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    jobstore = os.path.join(config.JOBSTORE_DIR, guid)
    return {
        "inputs": inputs_path,
        "logs": logs_path,
        "results": results_dir,
        "jobstore": jobstore
    }

def save_file(file, path):
    with open(path, "wb") as f:
        f.write(file.file.read())
    return path

def validate_inputs(yaml_file, workdir):
    
    cwd = os.getcwd()
    missing = list()
    
    yaml = YAML().load(open(yaml_file))
    for key in yaml:
        if (yaml[key] is not None):
            if isinstance(yaml[key] , list):
                for file in yaml[key]:
                    if (not os.path.isfile(file['path']) and not os.path.isfile(os.path.join(workdir,file['path']))):
                        missing.append(file['path'])
            if isinstance(yaml[key],dict):
                if (not os.path.isfile(yaml[key]['path']) and not os.path.isfile(os.path.join(workdir,yaml[key]['path']))):
                    missing.append(yaml[key]['path'])
    return missing

def delete_workdir(GUID):
    workdir = get_workflow_dirs(GUID)
    for path in workdir.values():
        if os.path.exists(path):
            shutil.rmtree(path)

    workflow_zip_path = os.path.join(config.WORKFLOWS_DIR, f"{GUID}.zip")
    inputs_zip_path = os.path.join(config.INPUTS_DIR, f"{GUID}.zip")
    outputs_zip_path = os.path.join(config.RESULTS_DIR, f"{GUID}.zip")
    if os.path.exists(workflow_zip_path):
        os.remove(workflow_zip_path)
    if os.path.exists(inputs_zip_path):
        os.remove(inputs_zip_path)
    if os.path.exists(outputs_zip_path):
        os.remove(outputs_zip_path)

def zip_folder(folder_path, output_path):
    shutil.make_archive(output_path, 'zip', folder_path)
    return output_path + '.zip'

def get_directory_tree(path):
    file_types = dict()
    for key in config.EXTENSIONS:
        file_types[key] = list()
    file_types['other'] = list()

    for root, dirs, files in os.walk(path):
        files.sort()
        for file in files:
            foundFlag = False
            filename = os.path.relpath(os.path.join(root, file), path)
            for ext in config.EXTENSIONS:
                if file.endswith(tuple(config.EXTENSIONS[ext])):
                    foundFlag = True
                    file_types[ext].append({
                        "filename": filename
                    })
                    continue
            if (not foundFlag):
                file_types['other'].append({
                        "filename": filename
                })
    return file_types

def create_workflow_zip(workflow):
    zip_path = os.path.join(config.WORKFLOWS_DIR,f"{workflow.GUID}.zip")
    if (os.path.exists(zip_path)):
        os.remove(zip_path)
    zip_wf = zipfile.ZipFile(zip_path, 'w')
    zip_wf.write(workflow.template.path, "workflow.cwl")

    for root, directories, files in os.walk(workflow.workdir['inputs']):
            for filename in files:
                filePath = os.path.join(root,filename)
                zip_wf.write(filePath,f"./inputs/{filename}") 

    for root, directories, files in os.walk(workflow.workdir['results']):
            for filename in files:
                filePath = os.path.join(root,filename)
                zip_wf.write(filePath,f"./results/{filename}")

    if os.path.exists(os.path.join(workflow.workdir['logs'], "log.txt")):
        zip_wf.write(os.path.join(workflow.workdir['logs'], "log.txt"), "log.txt")

    zip_wf.close()

    return zip_path


def get_workflow_files_tree(workdir):
    files_tree = {
        "inputs": get_directory_tree(workdir['inputs']),
        "logs": "log.txt",
        "results": get_directory_tree(workdir['results'])
    }
    
    return files_tree

