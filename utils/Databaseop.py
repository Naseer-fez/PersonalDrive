from models.database import db,User
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_
import hashlib

def writedb(data,update=0):
    #first extract the nesscary
    username=data.get("username")
    password=data.get("password")
    if(not username or not password):
        return [0,"username or password not available"]
    email=data.get("email")
    password=__hashing(password)
    ROW=User(username=username,password=password,email=email)
    try:
        db.session.add(ROW)
        db.session.commit()
        
    except  IntegrityError:
        db.session.rollback()
        return [0,"The username already exists"]
    except Exception as e:
        db.session.rollback()
        return [0,str(e)]
    return [1,ROW.userid]
        
        
        
    
def updatedb(data):
    logged_in_username = data.get("logged_in_username")
    if logged_in_username:
        try:
            ROW = db.session.query(User).filter_by(username=logged_in_username).first()
        except Exception as e:
            return [0, str(e)]
    else:
        result=readdb(data,input=1)
        if not result[0]:
            return [0,"No user found"]
        ROW=result[1]
        
    if not ROW:
        return [0,"No user found"]
    
    email=data.get("email")
    if email:
        ROW.email=email
    pasword=data.get("password")
    if pasword:
        pasword=__hashing(pasword)
        ROW.password=pasword
    username=data.get("username")
    if username:
        ROW.username=username
    
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return [0, "Username or email already exists"]
    except Exception as e:
        db.session.rollback()
        return [0,str(e)]
    return [1,"Updated successfully"]
    
    
    
def readdb(data,input=0):
    username=data.get("username")
    logged_in_username=data.get("logged_in_username")
    password=data.get("password")
    if(not password):
        return [0,"password not available"]
    email=data.get("email")
    
    try:
        if logged_in_username:
            ROW=db.session.query(User).filter_by(username=logged_in_username).first()
        else:
            ROW=db.session.query(User).filter(
                or_(User.username==username,User.email==email) ).first()
        if not ROW and not input:
            userid=data.get("userid")
            if not userid: #means data is completely wrong
                return [0,"No user found"]
            try: #also check by username also 
                ROW=db.session.query(User).filter_by(userid=userid).first()
            except Exception as e:
                return [0,str(e)]
        if not ROW:
            return[0,"No user found"]
        if input:
            return [1,ROW]
        ROWPASS=ROW.password
        USERID=ROW.userid
    
    except Exception as e:
        return [0,str(e)]
    
    password=__hashing(password)
    if ROWPASS==password:
           return [1,USERID]
    else:
        return [0,"username and password are incorrect"]
        


def getemail(email):
    try:
        ROW=db.session.query(User).filter_by(email=email).first()
        if not ROW:
            return [0,"No email found"]
        else:
            return [1,ROW.userid]
    except Exception as e:
        return [0,str(e)]
    
    
def changepwd(useid,password):
        ROW=db.session.query(User).filter_by(userid=useid).first()
        password=__hashing(password)
        try:
            if not ROW:
                return [0, "No user found with the given ID"]
            ROW.password=password
            db.session.commit()
            return [1,"Password changed successfully"]
        except Exception as e:
                db.session.rollback()
                return [0,f"There has been an error: {e}"]


def deletedb(data):
    result=readdb(data,input=1)
    if not result[0]:
        return [0,"No user found"]
    ROW=result[1]
    if not ROW:
        return[0,"No user found"]
    try:
        db.session.delete(ROW)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return [0,str(e)]
    return [1,"Deleted successfully"]


def __hashing(password):
    return hashlib.sha256(password.encode()).hexdigest()