from flask import Blueprint,jsonify
from utils.acceptjson import getjson
from flask_jwt_extended import create_access_token
from utils.Databaseop import writedb
from utils.Storage import get_storage
Fileoperation=get_storage()
accountcreationbp=Blueprint("createaccount",__name__)
@accountcreationbp.route("/createaccount/",methods=["POST"])
@getjson
def home(data):

    userid=writedb(data)
    if not userid[0]:
        return jsonify({"return":userid[1]}),401
    username=data.get("username")
    tooken=create_access_token(identity=username)
    Fileoperation.createnewuser(userid=userid[1])
    return jsonify({"return":tooken,"userid":userid[1]}),200
    
