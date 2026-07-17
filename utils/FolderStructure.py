# import os 
# from pathlib import Path
# import json
from .Storage import get_storage
from dotenv import load_dotenv
import time
load_dotenv()
Fileoperation=get_storage()

class FolderStructure:
    def __init__(self,userid:str):
        self.userid=str(userid)
        self.Directory=[]
        self.allfiles=dict()
        self.trash=dict()
        self.currenttime=int(time.time())
        self.Folderdesign()
    def Folderdesign(self):
        #For folderstructure
        folderpath=Fileoperation.getfilepath(userid=self.userid,folderreq=1) 
        filepath=Fileoperation.getfilepath(userid=self.userid,filename=None)
        statspath=filepath.parent/"files.json" 
        self.Directory=self.FolderTraverse(Foldernames=Fileoperation.Allfiles(folderpath),Folderpath=folderpath)
        Fileoperation.jsonwrite(self.userid,data=self.Directory,fileindent=4)  ##Forfolderstructure
        # print(statspath)
        Fileoperation.jsonwrite(self.userid,data=self.allfiles,fileindent=4,filepath=statspath)
        
        # Reset the update flag to 0 in stats.json
        statfile = Fileoperation.getstatsfile(self.userid)
        try:
            statsdata = Fileoperation.jsonread(userid=self.userid, path=statfile)
            if not isinstance(statsdata, dict):
                statsdata = {}
        except Exception:
            statsdata = {}
        statsdata["update"] = 0
        Fileoperation.jsonwrite(self.userid, data=statsdata, filepath=statfile)
    def FolderTraverse(self,Foldernames,Folderpath):
            Data=[]
            for Folder in Foldernames:
                Dirpath=Fileoperation.joinpath(Folderpath,Folder) 
  
                if Fileoperation.isdirectory(Dirpath) :
                    Data.append({
                        "Name":str(Folder),
                        "type":"Folder",
                        "path":str(Fileoperation.getreativepath(userid=self.userid,filename=Dirpath)),
                        "children":(self.FolderTraverse(Folderpath=Dirpath,
                                                       Foldernames=Fileoperation.Allfiles(Dirpath))) })
                    
                else:
                    
                    path=str(Fileoperation.getreativepath(userid=self.userid,filename=Dirpath))
                    stat=Fileoperation.filetiming(Dirpath)
                    Data.append({
                        "Name":str(Folder),
                        "path":path,
                        "type":str(Fileoperation.getextenstion(Dirpath)),
                        "size":int(Fileoperation.Filesize(userid=self.userid,filepath=Dirpath)),
                        "createdtime":stat["createdtime"],
                        "updatedtime":stat["updatedtime"]
                        
                    })
                    if Folder not in self.allfiles:
                        self.allfiles[Folder]=[path]
                    else:
                        self.allfiles[Folder].append(path)
                    # self.allfiles.append({
                    #     "filename":str(Folder),
                    #     "path":path
                    # })

            return Data
    

def Createfilestructure(userid):
    # FolderStructure(userid=str(userid))
    try:
        FolderStructure(userid=str(userid))
        return 1
    except Exception as e:
        print(e)
        return 0 #User Donot exist


def updatefilestructure(Userid,Updates=None,operation=None):
    # Createfilestructure(Userid)  ##Just for the timebeing
    PATH=Fileoperation.getstatsfile(Userid)
    try:
        data=Fileoperation.jsonread(userid=Userid,path=PATH)
        data["update"]=1
       
    except (FileNotFoundError,TypeError,Exception) as e:
        data = {}
        Createfilestructure(Userid)
        data["update"]=0  ##measn file is updated 
    jsonoperation(userid=Userid,path=PATH,data=data)
    return 
        
#solution for circular import
def jsonoperation(userid,data,path=None):
        if path is None:
            path=Fileoperation.getstatsfile(userid)      
        Fileoperation.jsonwrite(userid=userid,data=data,filepath=path)

if __name__=="__main__":
    print(Createfilestructure(1))