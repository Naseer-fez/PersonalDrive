from flask import Blueprint,jsonify
from utils.Storage import get_storage
from utils.acceptjson import getjson
from .tookengeneration  import generatelink,maplink 
from dotenv import load_dotenv
import os
setpublicbp=Blueprint("setpublic",__name__)

Fileoperation=get_storage()
@setpublicbp.route("/access/<int:userid>/",methods=["POST"])
@getjson
def Home(userid,data):
    userid=str(userid)
    filepath=data.get("filepath")
    expiredata=604800 if data.get("time") is None else data.get("time") #week of default
    if filepath is None:
        return jsonify({"return":"no filepath sent"}),400
    tooken=maplink(userid=userid,filepath=filepath,exptime=expiredata)
    link=generatelink(data=tooken)
    base=os.getenv("URL")
    link=f"{base}/{link}"
    return jsonify({"return":str(link)}),200
    




    