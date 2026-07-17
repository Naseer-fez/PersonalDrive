from flask import Blueprint,jsonify
from utils.Storage import get_storage
from utils.acceptjson import getjson
from utils.updatespace import updatespace
from utils.FolderStructure import updatefilestructure
from utils.trashfile import deletefromtrash

trashbp=Blueprint("trash",__name__)
Fileoperation=get_storage()
@trashbp.route("/trash/<int:userid>/",methods=["DELETE"]) #Frontend should send trash /filename
@getjson
def Home(userid,data):
    userid=str(userid)
    filename=str(data.get("filepath"))
    filesize=0
    try:
        filesize=Fileoperation.Filesize(userid,filepath=filename)
    except Exception:
        pass
    obj=deletefromtrash(userid=userid,trashpath=filename)
    if not obj:
        return  jsonify({"return":"Some error removing the trash"}),400
    updatefilestructure(Userid=userid)
    updatespace(userid=userid,operation=-filesize)
    return jsonify({"return":"removed successfully from trash"}),200
