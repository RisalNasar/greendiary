
import subprocess
import logging
import sys



class TimeoutExpired(Exception):
    pass



def runProcess(commandList, cwd=None, waitTimeout=None, callingFunctionLogger=None):
    if callingFunctionLogger != None:
        locallogger = logging.getLogger(f"{callingFunctionLogger}.{__name__}.runProcess")
    else:
        locallogger = logging.getLogger(f"{__name__}.runProcess")
    
    try:
        p = subprocess.Popen(commandList, shell=False, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
        out, err = p.communicate()
        
        if waitTimeout != None:
            p.wait(waitTimeout)
    except TimeoutExpired as e:
        p.kill()
        out, err = p.communicate()
        locallogger.exception(e)
        sys.exit(1)
    
    
    # Convert out, err to strings
    out = out.decode('utf-8')
    err = err.decode('utf-8')
    
    return out, err

