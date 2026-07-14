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
from routes.fileoperations.recovertrash import recovertrash  ##used to move the file from the trash to its original postion
from routes.fileoperations.deletetrash import trashbp
from routes.publicacces.accesspublic import publicbp
from routes.publicacces.setpublic import setpublicbp
from routes.folderoperations.folderupload import folderuploadbp
from routes.docs.docs import docsbp
####################    CORE    FEATURES    DONE  ####################
#Acc Operations (Optional)
from routes.Useroperations.Login import loginbp
from routes.Useroperations.creatacc import accountcreationbp
from routes.Useroperations.deleteacc import deleteacc
from routes.Useroperations.update import updatebp
from routes.Useroperations.Forgotemail.forgotemail import forgotbp
from routes.health import healthbp
#Uttils
from utils.auth import enableauth
from utils.ratelimiter import enableratelimiter
from flask_jwt_extended import JWTManager
from datetime import timedelta
from routes.main import resetlink,startngrok
#Models
from models.database import db
load_dotenv()
from config import config
def Createapp():
    app = Flask(__name__)
    #Scerets
    app.config["secret"] = os.getenv("secret") 
    #Configs
    FrontendURL=[url.strip()
    for url in os.getenv("FrontendURL", "*").split(",")
    if url.strip()]
    if FrontendURL==['*']:
        CORS(app)
    else:
        CORS(app,resources={r"/*":{"origins":FrontendURL}},supports_credentials=True)
    if config.get("Ratelimiter",1):
        enableratelimiter(app)    
    
    #Register Blueprints
    loginoperations=loginbp,accountcreationbp,deleteacc,updatebp,forgotbp
    routes=[uploadbp,downloadbp,structurebp,deletefilebp,
                updatefilebp,createbp,postionbp,spacebp,filesearch,trashbp,
                setpublicbp,publicbp,folderuploadbp,healthbp
                recovertrash,docsbp]
    if config.get("allowusers", 1):
        app.config["JWT_SECRET_KEY"]=os.getenv("jwt") or os.getenv("secret") #Secret
        for endpoint in loginoperations:
            routes.append(endpoint)
        enableauth(app)
        JWTManager(app)
        app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(int(config.get("jwtduration",30)))
        #DATABASE
        app.config['SQLALCHEMY_DATABASE_URI']=os.getenv("Database","sqlite:///users.db")
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        with app.app_context():
            db.create_all()


    
    for blueprint in routes:
        app.register_blueprint(blueprint)
    LINK=resetlink()
    app.config["link"]=LINK
    return app
app=Createapp()



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=False)

