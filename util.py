import os, psutil, time, signal, sqlite3, config

def check_pid(pid):
    try:
        os.kill(pid, 0)
        
        if (psutil.Process(pid).status() == psutil.STATUS_ZOMBIE):
            return False

        return True
    except OSError:
        return False

def get_wf_status(pid, guid):
    if (pid == None):
        return "NOT_YET_EXECUTED"
    if (pid<0):
        return "TERMINATED"
    
    if (check_pid(pid)):
        return "RUNNING"
    
    input_path = os.path.join(config.INPUTS,guid)

    return "FINISHED"


def terminate(GUID, pid, flag, timeout = 0):
    time.sleep(timeout)
    os.kill(pid, signal.SIGINT)
    conn = sqlite3.connect(config.DATABASE)
    c = conn.cursor()

    c.execute('UPDATE workflows SET PID='+str(flag)+' WHERE GUID="'+GUID+'"')

    conn.commit()
    conn.close()

def get_wf_pid(GUID):
    conn = sqlite3.connect(config.DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM workflows WHERE GUID="'+GUID+'"')
    row = c.fetchone()

    conn.close()
    if (row is None):
        return None

    return row[3]

def get_wf(GUID):
    conn = sqlite3.connect(config.DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM workflows WHERE GUID="'+GUID+'"')
    row = c.fetchone()

    conn.close()
    return row
