#Uploads cant be modulase by using the file class
from flask import jsonify,request,Blueprint
import os 
from pathlib import Path
from utils.updatespace import updatespace,totalspaceused
from utils.FolderStructure import updatefilestructure
from config import config
folderuploadbp=Blueprint('folderupload',__name__)


@folderuploadbp.route("/uploadfolder/<int:Userid>/",methods=["POST"]) 
def home(Userid):
    fileslist=request.files.getlist("files")
    if fileslist is None:
        return jsonify({"return":"No folder uploaded"}),400
    uploadsize = request.content_length
    if totalspaceused(Userid)["remaningspace"] < uploadsize:
        return jsonify({"return": "No space left"}), 400
    directory=request.form.get("directory")
    if directory is None:
        return  jsonify({"return":"No folder path mentioned"}),400
    Destiantion=config.get("DestinationFolder")
    directory=Path(os.path.join(Destiantion,str(Userid),directory))
    #first create the directory
    directory.mkdir(parents=True,exist_ok=True) #directory is created 
    #now stream the file
    CHUNK_SIZE=1024*1024*int(config.get("size",16))
    #now iterante over the files
    output="Folder upload done"
    statuscode=200
    total_size=0
    try:

        for file in fileslist:
            # Clean and normalize path to support subdirectories
            rel_path = file.filename.replace("\\", "/")
            filepath = directory / rel_path
            filepath.parent.mkdir(parents=True, exist_ok=True)
            newpath = filecheck(filepath)
            if newpath !=0:
                filepath=newpath #meaning replace the file
            with open(file=filepath,mode="wb") as f:
                while True:
                    chunk=file.stream.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    total_size += len(chunk)
                    f.write(chunk)
    except Exception as e:
        output=e   
        statuscode=401
    updatefilestructure(Userid=Userid,operation=total_size)
    updatespace(userid=Userid,operation=uploadsize)
    return jsonify({"return":str(output)}),statuscode



def filecheck(tosavepath):
        prefix=1
        attempt=10000
        original_stem=tosavepath.stem
        suffix=tosavepath.suffix
        while attempt:
                if not tosavepath.exists():
                    return tosavepath
                tosavepath=tosavepath.with_name(f"{original_stem}[{prefix}]{suffix}")
                prefix+=1
                attempt-=1
        return 0  