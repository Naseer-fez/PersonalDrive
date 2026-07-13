from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from config import config
db=SQLAlchemy()
SPACEINGB=config.get("basic",15)
class User(db.Model):
    __tablename__="User"
    userid=db.Column(db.Integer,primary_key=True,autoincrement=True)
    username=db.Column(db.String(256),nullable=False,unique=True)
    password=db.Column(db.String(256),nullable=False)
    email=db.Column(db.String(256),nullable=True,unique=True)
    plan=db.Column(db.String(10),default="basic")
    storage=db.Column(db.Float,default=SPACEINGB)