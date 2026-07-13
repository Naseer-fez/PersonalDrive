from flask  import Blueprint,jsonify,Response
# from flask import Flask,jsonify,Response
# # from .sendfile import Filedownload
# from sendfile import Filedowload
from config import config
from utils.Storage import get_storage
from utils.acceptjson import getjson
from utils.FileHelpers import filedetails
downloadbp=Blueprint('Downloadbp',__name__)
# downloadbp=Flask(__name__)
Fileoperation=get_storage()
# @downloadbp.route("/downloadfile/<int:userid>/",defaults={"folderpath":None,"filepath":None,},methods=["GET"])
@downloadbp.route("/download/<int:userid>/",methods=["GET"]) 
@getjson
def Home(userid,data):
    userid=str(userid)
    filepath=data.get("filepath") or data.get("filename")
    filepath,filesize,filetype=filedetails((userid),filepath)
    if filepath is None:
        return jsonify({"retutn":"WrongFile Inputed Tryagain"}),400
    
    SIZE=config.get("size",5) 
    if Fileoperation.isdirectory(filepath):
        headerdata={'Content-Disposition': 'attachment' ,"filename":f"{filepath}.zip"}
    else:
        headerdata={"filesize":filesize,"filetype":filetype}
        
    return Response(Fileoperation.readdata(filename=filepath,Sizeofdata=SIZE),
                    mimetype=filetype,headers=headerdata)
    
    
    





    
    

if __name__=="__main__":
    downloadbp.run(debug=True)
