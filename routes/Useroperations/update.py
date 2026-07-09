from flask import Blueprint,jsonify
from utils.acceptjson import getjson
from utils.Databaseop import updatedb
updatebp=Blueprint("updateacc",__name__)

@updatebp.route("/updateacc/",methods=["POST"])
@getjson
def home(data):
    message=updatedb(data)
    if not message[0]:
        return jsonify({"return":message[1]}),401
    return jsonify({"return":message[1]}),200
    
