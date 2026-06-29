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
load_dotenv()
def Createapp():
    app = Flask(__name__)

    CORS(app=app)    
    #Register Blueprints
    routes=[uploadbp,downloadbp,structurebp]
    for blueprint in routes:
        app.register_blueprint(blueprint)
    # app.register_blueprint(uploadbp)
    # app.register_blueprint(downloadbp)
    return app


app=Createapp()




if __name__ == "__main__":
    app.run(debug=True)
