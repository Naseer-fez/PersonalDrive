from flask import Flask,request,jsonify
import os 
from dotenv import load_dotenv
from utils.FileHelpers import CreateDir
from pathlib import Path
from flask_cors import CORS
#ImportBlueprints
from routes.fileupload.recive import uploadbp
from routes.filedownload.download import downloadbp
from routes.filestructure.structure import structurebp
#File operations
from routes.fileoperations.deletefile import deletefilebp
from routes.fileoperations.updatefile import updatefilebp
from routes.fileoperations.createdir import createbp
from routes.fileoperations.postionchnage import postionbp
from utils.auth import enableauth
load_dotenv()
def Createapp():
    app = Flask(__name__)

    CORS(app=app)    
    enableauth(app)
    #Register Blueprints
    routes=[uploadbp,downloadbp,structurebp,deletefilebp,updatefilebp,createbp,postionbp]
    for blueprint in routes:
        app.register_blueprint(blueprint)
    

    return app
app=Createapp()



if __name__ == "__main__":
    app.run(debug=True)
