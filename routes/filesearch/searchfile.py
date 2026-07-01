from flask import Blueprint,jsonify

from .searchhelp import searchfile
filesearch=Blueprint("search",__name__)


@filesearch.route("/searchfile/<int:userid>/<string:filename>/",methods=["GET"])
def Home(userid,filename):
    result=searchfile(userid=str(userid),tofind=filename)
    if result[0]==-1:
        return jsonify({"return":result[1]}),400
    else:
        return jsonify({"return":"File Found","path":result[1]}),200
    

    
    
    