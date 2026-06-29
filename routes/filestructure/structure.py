from flask import Blueprint,jsonify
from utils.FolderStructure import Createfilestructure
from dotenv import load_dotenv
from utils.Storage import get_storage
structurebp=Blueprint("structure",__name__)

File=get_storage()

@structurebp.route("/structure/<int:userid>",methods=["GET"])
def Home(userid):
    structure=Createfilestructure(userid=userid)
    if structure==0:
        return jsonify({"return":"UserHasnofile","instruction":"createfile"}),500
    filepath=File.getfilepath(userid=str(userid))
    filedata=File.jsonread(userid=str(userid))
    if  filedata==0:
        return jsonify({"return":"fileopeningerror","instruction":"tryagain"}),500
    return jsonify(filedata),200
    
