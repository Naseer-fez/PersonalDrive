from flask import Blueprint,jsonify
from utils.acceptjson import getjson
from utils.Databaseop import deletedb
deleteacc=Blueprint("deleteaccount",__name__)

@deleteacc.route("/deleteuser/",methods=["GET"])
@getjson
def home(data):
    message=deletedb(data)
    if not message:
        return jsonify({"return":message}),401
    return jsonify({"return":message}),200
    
