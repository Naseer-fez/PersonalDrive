from flask import Blueprint,jsonify
from utils.acceptjson import getjson
from flask_jwt_extended import create_access_token
from utils.Databaseop import readdb
loginbp=Blueprint("login",__name__)

@loginbp.route("/login/",methods=["GET"])
@getjson
def home(data):
    userid=readdb(data)
    if not userid:
        return jsonify({"return":userid}),401
    username=data.get("username")
    tooken=create_access_token(identity=username)
    return jsonify({"return":tooken,"userid":userid}),200
    
