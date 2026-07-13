from apirlpy import ratelimiter as RL
from flask import request,jsonify
from config import config


path=config.get("ratelimiter",None)
Allowreq=config.get("Allowfreq",50)
Resettime=config.get("resettime",10)
cooldowntime=config.get("cooldowntime",20)
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
                    CooldownTime=cooldowntime,ResetTime=Resettime,AllowedFreq=Allowreq)
        if waittime!=1:
            return jsonify({"return":f"too many requests!!, wait for {waittime}sec","waittime":int(waittime)}),429
        return
    return
        