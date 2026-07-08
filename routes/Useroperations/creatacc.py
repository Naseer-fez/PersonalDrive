from flask import Blueprint,jsonify
from utils.acceptjson import getjson
from flask_jwt_extended import create_access_token
from utils.Databaseop import writedb
accountcreationbp=Blueprint("createaccount",__name__)

@accountcreationbp.route("/createaccount/",methods=["GET"])
@getjson
def home(data):

    userid=writedb(data)
    if not userid:
        return jsonify({"return":userid}),401
    username=data.get("username")
    tooken=create_access_token(identity=username)
    return jsonify({"return":tooken,"userid":userid}),200
    
