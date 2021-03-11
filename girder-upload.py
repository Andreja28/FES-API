import girder_client
import config
import sys,os
import util

guid = sys.argv[1]
girder_api_key = sys.argv[2]
outputs = sys.argv[3]
if (not os.listdir(os.getcwd())):
    sys.exit()

gc = girder_client.GirderClient(apiUrl=config.GIRDER_API)
userId = gc.authenticate(apiKey=girder_api_key)['_id']

privateFolder = gc.loadOrCreateFolder('Private', userId, parentType="user")

outFolder = gc.loadOrCreateFolder('workflow-outputs', privateFolder['_id'], parentType="folder")
wf = util.get_wf(guid)
wfFolder = gc.loadOrCreateFolder(wf, outFolder['_id'], parentType="folder")

gc.upload(outputs, wfFolder['_id'])