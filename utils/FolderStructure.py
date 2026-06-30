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
        # self.BASEDIR=os.path.join(os.getenv("DestinationFolder"),userid) or r"D:\CODE\PYTHON"
        # self.BASEDIR=r"D:\CODE\PYTHON\CODE\Backend"
        self.userid=str(userid)
        self.Directory=[]
        self.Folderdesign()
        # print(self.Directory)
    # def getbase(userid):
    #     File
    def Folderdesign(self):
        # Userdir=os.path.join(BASEDIR,Userid) Real userid
        # Userdir=File.getfilepath(userid=self.userid) 
        folderpath=Fileoperation.getfilepath(userid=self.userid,folderreq=1)
        # print(os.listdir(Userdir)
        
        self.Directory=self.FolderTraverse(Foldernames=Fileoperation.Allfiles(folderpath),Folderpath=folderpath)
        
        Fileoperation.jsonwrite(self.userid,data=self.Directory,fileindent=4)
    def FolderTraverse(self,Foldernames,Folderpath):
            # print(Foldernames)
            Data=[]
            for Folder in Foldernames:
                Dirpath=Fileoperation.joinpath(Folderpath,Folder) 
  
                if Fileoperation.isdirectory(Dirpath):
                    Data.append({
                        "Name":str(Folder),
                        "type":"Folder",
                        "path":str(Fileoperation.getreativepath(userid=self.userid,filename=Dirpath)),
                        "children":(self.FolderTraverse(Folderpath=Dirpath,
                                                       Foldernames=Fileoperation.Allfiles(Dirpath))) })
                    
                else:
                    currenttime=int(time.time())
                    Data.append({
                        "Name":str(Folder),
                        "path":str(Fileoperation.getreativepath(userid=self.userid,filename=Dirpath)),
                        "type":str(Fileoperation.getextenstion(Dirpath)),
                        "size":int(Fileoperation.Filesize(userid=self.userid,filepath=Dirpath)),
                        "createdtime":int(currenttime),
                        "updatedtime":int(currenttime)
                        
                    })
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