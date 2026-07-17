from pathlib import Path
from flask import Blueprint,jsonify,request
from utils.Storage import get_storage
from utils.acceptjson import getjson
from utils.FolderStructure import updatefilestructure
postionbp=Blueprint("postion",__name__)

Fileoperation=get_storage()
@postionbp.route("/changefilelocation/<int:userid>/",methods=["PUT"])
@getjson
def Home(userid,data):
    oldpath=data.get("oldpath")
    newloaction=data.get("newlocation")
    resolved_destination = Fileoperation.getfilepath(userid=str(userid), filename=newloaction)
    if Fileoperation.isdirectory(resolved_destination):
        newloaction = str(Path(newloaction) / Path(oldpath).name)
    tosend=updatelocation(userid=str(userid),filepath=oldpath,newpath=newloaction)
    statuscode=200
    if tosend[0] ==0:
        statuscode=400
    updatefilestructure(Userid=userid,Updates=[oldpath,newloaction],operation="update")
    return jsonify({"return":tosend[1]}),statuscode


def updatelocation(userid,filepath,newpath):
    try:
        Fileoperation.locationchnage(userid=userid,oldpath=filepath,tochange=newpath)
        return [1,"file postion changed"]
    except FileNotFoundError as e:
        return [0,"Filenotfound"]
    except FileExistsError as e:
        return [0,"filedonotexist"]
    except PermissionError as e:
        return [0,"permissiondenied"]
    except Exception as e:
        return [0,str(e)]
    
    
