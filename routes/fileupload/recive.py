from flask import jsonify,request,Blueprint
import os 
from dotenv import load_dotenv
from utils.FileHelpers import CreateDir
from pathlib import Path
from utils.updatespace import updatespace
from utils.FolderStructure import updatefilestructure
load_dotenv()
uploadbp=Blueprint('FileUpload',__name__)


@uploadbp.route("/uploadfile/<int:Userid>",methods=["POST"]) 

def home(Userid):
    directory=request.form.get("directory")
    Stream=request.environ["wsgi.input"]
    Filename=os.getenv("DestinationFolder")
    if 'filepath' not in request.files:
        return jsonify({"return": "No file provided"}), 400
    Recivedfile=str(request.files['filepath'].filename)
    uploadsize = request.content_length
    if  not updatespace(Userid,+uploadsize):
        return jsonify({"return":"No space left \n Try Clearning Trash"}),400
    tosavepath=CreateDir(Userid=Userid,Directory=directory,Filename=Recivedfile)
    filesize=0
    if  tosavepath==0:
        return jsonify({"return":"Some Error in Creating the Directory"}),401
    uploaded_file = request.files["filepath"]
    tosavepath=Path(tosavepath)
    tosavepath=filecheck(tosavepath)
    if tosavepath==0:
        return jsonify({"Too Many files already exist try a diffrentname"}),401
    with open (file=Path(tosavepath),mode="ab") as File:

        while True:
            Chunk=uploaded_file.stream.read((1024*1024)*int(os.getenv("size"), 16)) #16MB
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