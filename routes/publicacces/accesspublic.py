from flask import Blueprint,jsonify,Response
import os
import binascii
from utils.Storage import get_storage
from .tookengeneration import verification,verify_token,maplink,path64
from utils.FileHelpers import filedetails
from dotenv import load_dotenv
from config import config
publicbp=Blueprint("public",__name__)


Fileoperation=get_storage()
@publicbp.route("/share/<int:userid>/<string:filesharing>/<int:time>/<string:tooken>",methods=["GET"])
def Home(userid,filesharing,time,tooken):
    userid=str(userid)
    timeverfication=verification(time)
    if timeverfication == 0:
        return jsonify({"return":"link expired"}),400   
    data = maplink(userid=userid, filepath=filesharing, exptime=time, change=0, encode=None)
    if not verify_token(data=data,token=tooken):
        return jsonify({"return":"the token which you have received is invalid"}),400
    try:
        decoded_filepath = path64(filesharing, encode=0)
    except (binascii.Error, UnicodeDecodeError, ValueError):
        return jsonify({"return":"Invalid file path token."}),400
    #direclty copied from downlaods
    #can redirect to the link need to think about that    
    filepath,filesize,filetype=filedetails((userid),decoded_filepath)
    if filepath is None:
        return jsonify({"return":"Wrong file input. Try again."}),400
    if Fileoperation.isdirectory(filepath):
        folder_name = os.path.basename(str(filepath).rstrip('/\\')) or "download"
        headerdata={'Content-Disposition': f'attachment; filename="{folder_name}.zip"'}
    else:
        headerdata={"filesize": str(filesize) if filesize is not None else "0", "filetype": str(filetype) if filetype is not None else "unknown"}
    SIZE=config.get("size",5) 
    return Response(Fileoperation.readdata(filename=filepath,Sizeofdata=SIZE),
                    mimetype=filetype,headers=headerdata)
    
    
    


        