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
from routes.fileoperations.gettrash import gettrashbp
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
from utils.logs import logs
from flask_jwt_extended import JWTManager
from datetime import timedelta
from routes.main import resetlink
#Models
from models.database import db
import secrets
load_dotenv()
from config import config
def Createapp():
    app = Flask(__name__)
    #Scerets
    app.config["secret"] = os.getenv("secret",secrets.token_urlsafe(32)) 
    #Configs
    FrontendURL=[url.strip()
    for url in os.getenv("FrontendURL", "*").split(",")
    if url.strip()]
    
    CORS(
        app,
        resources={r"/*": {"origins": "*" if FrontendURL == ['*'] else FrontendURL}},
        allow_headers=["*"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        supports_credentials=False,
    )
    if config.get("Ratelimiter",1):
        enableratelimiter(app)    
    
    #Register Blueprints
    loginoperations=loginbp,accountcreationbp,deleteacc,updatebp,forgotbp
    routes=[uploadbp,downloadbp,structurebp,deletefilebp,
                updatefilebp,createbp,postionbp,spacebp,filesearch,trashbp,
                setpublicbp,publicbp,folderuploadbp,healthbp,
                recovertrash,docsbp,gettrashbp]
    if config.get("allowusers", 0):
        app.config["JWT_SECRET_KEY"]=os.getenv("jwt") or os.getenv("secret") #Secret
        for endpoint in loginoperations:
            routes.append(endpoint)
        enableauth(app)
        JWTManager(app)
        app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(int(config.get("jwtduration",30)))
        #DATABASE
        database_url = os.getenv("Database", "sqlite:///users.db")
        if database_url and database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)
        with app.app_context():
            db.create_all()
    else:
        from utils.Storage import LocalStorage
        User=LocalStorage()
        User.createnewuser(userid=0)

    
    for blueprint in routes:
        app.register_blueprint(blueprint)
    
    logs(app)

    return app
app=Createapp()



if __name__ == "__main__":
    import threading
    import time
    
    def background_setup():
        time.sleep(5)  # Give Flask a moment to bind the port
        LINK = resetlink()
        with app.app_context():
            app.config["link"] = LINK

    threading.Thread(target=background_setup, daemon=True).start()
    port=config.get("port",5002)
    host=config.get("host","0.0.0.0")
    app.run(host=host, port=int(port), debug=False)
