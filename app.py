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
from routes.Useroperations.deleteacc import deleteacc
from routes.Useroperations.update import updatebp
from routes.Useroperations.Forgotemail.forgotemail import forgotbp
#Uttils
from utils.auth import enableauth
from flask_jwt_extended import JWTManager
from datetime import timedelta
#Models
from models.database import db
load_dotenv()
def Createapp():
    app = Flask(__name__)
    #Scerets
    app.config["secret"] = os.getenv("secret")
    app.config["JWT_SECRET_KEY"]=os.getenv("jwt")
    #Configs
    CORS(app=app)    
    jwt = JWTManager(app)
    enableauth(app)
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(int(os.getenv("jwtduration")))
    #DATABASE
    try:
        app.config['SQLALCHEMY_DATABASE_URI']=os.getenv("Database")
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    except Exception as e:
        print(e)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    db.init_app(app)
    with app.app_context():
        db.create_all()
    #Register Blueprints
    routes=[uploadbp,downloadbp,structurebp,deletefilebp,
            updatefilebp,createbp,postionbp,spacebp,filesearch,trashbp,
            setpublicbp,publicbp,folderuploadbp,
            loginbp,accountcreationbp,deleteacc,updatebp,forgotbp]
    for blueprint in routes:
        app.register_blueprint(blueprint)
    

    return app
app=Createapp()



if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)

