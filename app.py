from flask import Flask,request,jsonify
import os 
from dotenv import load_dotenv
from utils.FileHelpers import CreateDir
from pathlib import Path
load_dotenv()
app = Flask(__name__)


##FILESAVE IN THE SERVER
@app.route("/<int:Userid>",defaults={"directory":None},methods=["GET","POST"]) 
@app.route("/<int:Userid>/<string:directory>",methods=["GET","POST"]) 
def home(Userid,directory):
    Stream=request.environ["wsgi.input"]
    Filename=os.getenv("DestinationFolder")
    Recivedfile=str(request.files['filename'].filename)
    Tosave=CreateDir(Userid=Userid,Directory=directory,Filename=Recivedfile)
    if  Tosave==0:
        return jsonify({"return":"Some Error in Creating the Directory"}),401
    with open (file=Path(Tosave),mode="ab") as File:
        while True:
            Chunk=request.stream.read((1024)*16) #16MB
            if not Chunk :
                break
            File.write(Chunk)
    # with open() as File:
    return jsonify({"return":"File Saved in the server"}),200


if __name__ == "__main__":
    app.run(debug=True)
