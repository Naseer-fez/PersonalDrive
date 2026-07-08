from flask import Flask
import os 
from dotenv import load_dotenv
from flask_cors import CORS
#ImportBlueprints
from routes.fileupload.recive import uploadbp
from routes.filedownload.download import downloadbp
from routes.filestructure.structure import structurebp
#File operations
from routes.filedeletion.deletefile import deletefilebp
from routes.fileoperations.updatefile import updatefilebp
from routes.fileoperations.createdir import createbp
from routes.fileoperations.postionchnage import postionbp
from routes.filestats.spaceleft import spacebp
from routes.filesearch.searchfile import filesearch 
from routes.fileoperations.removetrash import trashbp
from routes.publicacces.accesspublic import publicbp
from routes.publicacces.setpublic import setpublicbp
from routes.folderoperations.folderupload import folderuploadbp
####################    CORE    FEATURES    DONE  ####################
#Acc Operations
from routes.Useroperations.Login import loginbp
from routes.Useroperations.creatacc import accountcreationbp
#Uttils
from utils.auth import enableauth
from flask_jwt_extended import JWTManager
from datetime import timedelta
load_dotenv()
def Createapp():
    app = Flask(__name__)
    #Scerets
    app.config["secret"] = os.getenv("secret")
    app.config["JWT_SECRET_KEY"]=os.getenv("jwt")
    #Configs
    CORS(app=app)    
    enableauth(app)
    jwt = JWTManager(app)
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(int(os.getenv("jwtduration")))
    #Register Blueprints
    routes=[uploadbp,downloadbp,structurebp,deletefilebp,
            updatefilebp,createbp,postionbp,spacebp,filesearch,trashbp,
            setpublicbp,publicbp,folderuploadbp,loginbp,accountcreationbp]
    for blueprint in routes:
        app.register_blueprint(blueprint)
    

    return app
app=Createapp()



if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)

