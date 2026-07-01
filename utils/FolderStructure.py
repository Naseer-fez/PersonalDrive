# import os 
# from pathlib import Path
# import json
from .Storage import get_storage
from dotenv import load_dotenv
load_dotenv()
import time
Fileoperation=get_storage()
class FolderStructure:
    def __init__(self,userid:str):
        self.userid=str(userid)
        self.Directory=[]
        self.allfiles=dict()
        self.currenttime=int(time.time())
        self.Folderdesign()
    def Folderdesign(self):
        #For folderstructure
        folderpath=Fileoperation.getfilepath(userid=self.userid,folderreq=1) 
        filepath=Fileoperation.getfilepath(userid=self.userid,filename=None)
        statspath=filepath.parent/"stats.json" 
        self.Directory=self.FolderTraverse(Foldernames=Fileoperation.Allfiles(folderpath),Folderpath=folderpath)
        Fileoperation.jsonwrite(self.userid,data=self.Directory,fileindent=4)  ##Forfolderstructure
        print(statspath)
        Fileoperation.jsonwrite(self.userid,data=self.allfiles,fileindent=4,filepath=statspath)
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

 
if __name__=="__main__":
    print(Createfilestructure(1))