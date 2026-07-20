
import hmac
import hashlib
from flask import current_app
import time
import base64
from config import config
# secret=b"hello"


def get_secret():
    secret = (
        current_app.config.get("SECRET_KEY")
        or current_app.config.get("secret")
        or config.get("SECRET_KEY")
        or config.get("secret")
        or "default_secret_key"
    )
    if isinstance(secret, str):
        return secret.encode("utf-8")
    return secret
def generatelink(data):  
    tooken= hmac.new(get_secret(), data.encode(), hashlib.sha256).hexdigest()
    return f"{data}/{tooken}"
    

def verify_token(data, token):
    expected = hmac.new(get_secret(), data.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, token)


def maplink(userid,filepath,exptime,change=1,encode=1):
    if  change:
        currenttime=time.time()
        exptime=int(currenttime+exptime)
        exptime=str(exptime)
    if encode is not None:
        filepath=path64(filepath,encode=encode)
    completedata=f"{userid}/{filepath}/{exptime}"
    return completedata



def path64(path, encode=1) -> str:
    if encode:
        return base64.urlsafe_b64encode(path.encode("utf-8")).decode("ascii").rstrip("=")
    padding = "=" * (-len(path) % 4)
    return base64.urlsafe_b64decode(path + padding).decode("utf-8")

def verification(expiretime):
    currenttime=time.time()
    if expiretime<currenttime: #it is valid or not
        return 0
    return 1

if __name__=="__main__":
    # data="hehehh"
    # tooken=(create_token(data=data))
    # print(tooken)
    # result=verify_token(token=tooken,data="tooken")
    # print(extractdata(userid="1",filesharing=f"ha{pattern}hello/99999999999999999999/112"))
    pass