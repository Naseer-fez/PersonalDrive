from apirlpy import ratelimiter as RL
from flask import request,jsonify
from dotenv import load_dotenv
import os
load_dotenv()
path=os.getenv("ratelimiter")

ALLOW={
    "FileUpload.home",
    "Downloadbp.home",
    "folderupload.home"
    
    }
def enableratelimiter(app):
    
    @app.before_request
    def enforcing():
        if request.method == "OPTIONS":
            return
        ip = request.remote_addr
        endpoint = request.endpoint or request.path
        if endpoint in ALLOW:
            return
        endpoint=endpoint.replace("/", "")
        key=f"{ip}:{endpoint}"
        waittime=RL(IP_Adrs=key,FolderPath=path,Filename=endpoint.strip("/"),Format=None,
                    CooldownTime=20,ResetTime=10,AllowedFreq=50)
        if waittime!=1:
            return jsonify({"return":f"too many requests!!, wait for {waittime}sec","waittime":int(waittime)}),429
        return
    return
        