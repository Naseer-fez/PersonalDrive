from .Storage import get_storage
from dotenv import load_dotenv
from utils.FolderStructure import Createfilestructure
from config import config
Fileoperation=get_storage()
def getsize(node):
    # File
    if node["type"] != "Folder":
        return node["size"]

    # Folder
    total = 0
    for child in node["children"]:
        total += getsize(child)
    return total

def spacecalculator(userid,operation=0):
    try:
        DIR=Fileoperation.jsonread(userid=userid)
    except FileNotFoundError as e:
        Createfilestructure(userid=userid)
        DIR=Fileoperation.jsonread(userid=userid)
    except Exception as e:
        return 0
    total = 0

    for root in DIR:
        total += getsize(root)

    return total+operation


def totalspaceused(userid):
    PATH=Fileoperation.getstatsfile(userid)
    data=checkchanges(userid,path=PATH)

    if data[0]==1:
        if (data[1].get("usedspace") is not None) and data[1].get("update")==0:
            return data[1]
        
    #measn create the stats file first 
    # if data[0]==0:
    #     Createfilestructure(userid) # means reorgainse the files tructure
    
    space=spacecalculator(userid=userid) #recalut for the updation 
    data={"usedspace":int(space),"remaningspace":int(availabelforuser(userid)-space),
            "update":0}
    jsonoperation(userid=userid,data=data,path=PATH)
    return data

def jsonoperation(userid,data,path=None):
        if path is None:
            path=Fileoperation.getstatsfile(userid)      
        Fileoperation.jsonwrite(userid=userid,data=data,filepath=path)



def updatespace(userid,operation):
    currentspace=totalspaceused(userid)
    currentspace["usedspace"]=currentspace["usedspace"]+operation
    currentspace["remaningspace"]=currentspace["remaningspace"]-operation
    if currentspace["remaningspace"]>=0:
        jsonoperation(userid=userid,data=currentspace)
        return currentspace
    else: 
        return [0]
    

def checkchanges(userid,path=None):
    if path is None:
        path=Fileoperation.getstatsfile(userid)
    try:
        data=Fileoperation.jsonread(userid=userid,path=path)
        value=data.get("update")
        if (value is None) or (value==1):
            Createfilestructure(userid) #forsearch
            data["update"]=0 #means a new file 
            jsonoperation(userid=userid,path=path,data=data)
            return [0,data]
        else :
            return [1,data]
    except  (FileNotFoundError,TypeError) as e: #measn that the file is not created yet
        Createfilestructure(userid)
        return [-1]
    
        
    
    

def availabelforuser(userid):
    GB=1073741824
    if userid:
        return config.get("basic","15")*GB
    

        
        