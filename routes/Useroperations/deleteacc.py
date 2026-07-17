from flask import Blueprint,jsonify,g
from utils.acceptjson import getjson
from utils.Databaseop import deletedb
deleteacc=Blueprint("deleteaccount",__name__)

@deleteacc.route("/deleteacc/",methods=["DELETE"])
@getjson
def home(data):
    logged_in_username = getattr(g, "username", None)
    if logged_in_username:
        data["logged_in_username"] = logged_in_username
    message=deletedb(data)
    if not message[0]:
        return jsonify({"return":message[1]}),401
    return jsonify({"return":message[1]}),200
    
