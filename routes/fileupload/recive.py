from flask import jsonify,request,Blueprint
from dotenv import load_dotenv
from utils.FileHelpers import CreateDir
from pathlib import Path
from utils.updatespace import updatespace,totalspaceused
from utils.FolderStructure import updatefilestructure
from config import config
uploadbp=Blueprint('FileUpload',__name__)


@uploadbp.route("/uploadfile/<int:Userid>",methods=["POST"]) 

def home(Userid):
    directory=request.form.get("directory") or "/"
    if 'filepath' not in request.files:
        return jsonify({"return": "No file provided"}), 400
    Recivedfile=str(request.files['filepath'].filename)
    uploadsize = request.content_length
    if totalspaceused(Userid)["remaningspace"] < uploadsize:
        return jsonify({"return": "No space left"}), 400
    tosavepath=CreateDir(Userid=Userid,Directory=directory,Filename=Recivedfile)
    filesize=0
    if  tosavepath==0:
        return jsonify({"return":"Some Error in Creating the Directory"}),401
    uploaded_file = request.files["filepath"]
    tosavepath=Path(tosavepath)
    tosavepath=filecheck(tosavepath)
    if tosavepath==0:
        return jsonify({"return":"Too Many files already exist try a diffrentname"}),401
    with open (file=Path(tosavepath),mode="wb") as File:

        while True:
            Chunk=uploaded_file.stream.read((1024*1024)*int(config.get("size",10))) #10MB
            if not Chunk :
                break
            File.write(Chunk)
            filesize += len(Chunk)
    updatefilestructure(Userid,Updates=tosavepath,operation="add")
    updatespace(userid=Userid,operation=uploadsize)
    
    return jsonify({"return":"File Saved in the server"}),200



def filecheck(tosavepath):
        prefix=1
        attempt=1000
        original_stem=tosavepath.stem
        suffix=tosavepath.suffix
        while attempt:
                if not tosavepath.exists():
                    return tosavepath
                tosavepath=tosavepath.with_name(f"{original_stem}[{prefix}]{suffix}")
                prefix+=1
                attempt-=1
        return 0  