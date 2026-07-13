import ngrok
from config import config
import requests as req
import os



def getapi():
    API = os.getenv("ngrokauth","3BqIDkoRJ447eifyDYKxMQCD4mW_bGgo32eaypS2zozbsPjb")
    if not API:
        try:
            import winreg
            key_handle = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment", 0, winreg.KEY_READ)
            API, _ = winreg.QueryValueEx(key_handle, "ngrokauth")
            winreg.CloseKey(key_handle)
        except Exception:
            API = None

    if not API:
        API=config.get("ngrokauth")
        
    if not API:
        raise TypeError("Ngrok api key missing")
    ngrok.set_auth_token(API)

def startngrok():
    listener=ngrok.forward(
        config.get("port",5000),)
    return listener.url()




URL=config.get("backend")
# URL= "http://127.0.0.1:5000"
API=getapi()
def resetlink():
    global URL
    if not URL:
        raise TypeError("The backend url is missing")
    LINK=startngrok()
    try: #notify the center server
        URL=f"{URL}/change/{URL}"
        data={
            "LINK":LINK
        }
        response=req.put(url=URL,json=data)
        strc=response.status_code
        if strc==200:
            return LINK
    except Exception as e:
        raise TypeError("No link created")
        return 0













