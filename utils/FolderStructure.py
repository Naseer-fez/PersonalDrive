import os 
from pathlib import Path
import json 
from dotenv import load_dotenv
load_dotenv()


class FolderStructure:
    def __init__(self,userid:str):
        self.BASEDIR=os.path.join(os.getenv("DestinationFolder"),userid) or r"D:\CODE\PYTHON"
        # self.BASEDIR=r"D:\CODE\PYTHON\CODE\Backend"
        self.userid=userid
        self.Directory=[]
        self.Folderdesign()
        # print(self.Directory)
    def Folderdesign(self):
        # Userdir=os.path.join(BASEDIR,Userid) Real userid
        Userdir=Path(os.path.join(self.BASEDIR) ) #For testing 
        # print(os.listdir(Userdir)
        
        self.Directory=self.FolderTraverse(Foldernames=os.listdir(Userdir),Folderpath=self.BASEDIR)
        Userdetails=os.getenv("Userfolder") or r"D:\CODE\PYTHON\CODE\Projects\Personaldrive\userdetails"
        UserFile=os.path.join(Userdetails,self.userid)
        with open(file=f"{UserFile}.json",mode="w") as Output:
            json.dump(self.Directory,Output,indent=4)
        
    def FolderTraverse(self,Foldernames,Folderpath):
            # print(Foldernames)
            Data=[]
            for Folder in Foldernames:

                Dirpath=os.path.join(Folderpath,Folder) 
                if os.path.isdir(Dirpath):
                    Data.append({
                        "Name":Folder,
                        "type":"Folder",
                        "path":Dirpath,
                        "children":self.FolderTraverse(Folderpath=Dirpath,
                                                       Foldernames=os.listdir(Dirpath))})
                    
                else:
                    Data.append({
                        "Name":Folder,
                        "path":Dirpath,
                        "Type":os.path.splitext(Dirpath)[1]
                        
                    })
            return Data
    

def Createfilestructure(userid):
    try:
        FolderStructure(userid=str(userid))
        return 1
    except Exception as e:
        # print(e)
        return 0 #User Donot exist

 
if __name__=="__main__":
    print(Createfilestructure(2))