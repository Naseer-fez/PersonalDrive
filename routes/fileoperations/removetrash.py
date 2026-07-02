from flask import Blueprint,jsonify
from utils.Storage import get_storage
from utils.acceptjson import getjson
from utils.updatespace import updatespace
from utils.FolderStructure import updatefilestructure
from utils.updatespace import updatespace
trashbp=Blueprint("trash",__name__)

Fileoperation=get_storage()
@trashbp.route("/trash/<int:userid>/",methods=["DELETE"]) #Frontend shoudl send trash /filename
@getjson
def Home(userid,data):
    userid=str(userid)
    filename=str(data.get("filepath"))
    filesize=Fileoperation.Filesize(filepath=filename)
    obj=Fileoperation.deletefile(userid=userid,filepath=filename)
    if not obj:
        return  jsonify({"return":"Some error is removing the trash"})
    updatefilestructure(userid=userid,Updates=filename,operation="delete")
    updatespace(userid=userid,operation=filesize)
    return jsonify({"return":"removedsuccesully from trash"})
