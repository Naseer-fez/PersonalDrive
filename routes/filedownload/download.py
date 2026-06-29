from flask  import Blueprint,jsonify,Response
# from flask import Flask,jsonify,Response
# # from .sendfile import Filedownload
# from sendfile import Filedowload
import os 
from dotenv import load_dotenv
from pathlib import Path
from utils.Storage import get_storage
from utils.acceptjson import getjson

downloadbp=Blueprint('Downloadbp',__name__)
# downloadbp=Flask(__name__)
Fileoperation=get_storage()

# @downloadbp.route("/downloadfile/<int:userid>/",defaults={"folderpath":None,"filepath":None,},methods=["GET"])
@downloadbp.route("/downloadfile/<int:userid>/",methods=["GET"]) 
@getjson
def Home(userid,data):
    filepath=data.get("filepath")
    filepath,filesize,filetype=filedetails(str(userid),filepath)
    if filepath is None:
        return jsonify({"retutn":"WrongFile Inputed Tryahain"}),429
    headerdata={"filesize":filesize,"filetype":filetype}
    SIZE=os.getenv("size") or 5
    value=Fileoperation.readdata(filename=filepath,Sizeofdata=SIZE)
    return Response(value,mimetype=filetype,headers=headerdata)
    
    
    

def filedetails(userid,filepath):
    Source=Fileoperation.source 
    filepath=Fileoperation.joinpath(Source,[str(userid),filepath])  
    if Fileoperation.isdirectory(filepath):
        return [None]
    Filesize=Fileoperation.Filesize(filepath)
    Fileextenstion=Fileoperation.getextenstion()
    return [filepath,Filesize,Fileextenstion]




    
    

if __name__=="__main__":
    downloadbp.run(debug=True)
