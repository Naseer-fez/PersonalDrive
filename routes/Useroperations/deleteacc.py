from flask import Blueprint,jsonify
from utils.acceptjson import getjson
from utils.Databaseop import deletedb
deleteacc=Blueprint("deleteaccount",__name__)

@deleteacc.route("/deleteacc/",methods=["DELETE"])
@getjson
def home(data):
    message=deletedb(data)
    if not message[0]:
        return jsonify({"return":message[1]}),401
    return jsonify({"return":message[1]}),200
    
