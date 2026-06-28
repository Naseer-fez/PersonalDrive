# import os 
# from pathlib import Path
# import json
from Storage import get_storage
from dotenv import load_dotenv
load_dotenv()

File=get_storage()
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
        folderpath=File.getfilepath(userid=self.userid,folderreq=1)
        # print(os.listdir(Userdir)
        
        self.Directory=self.FolderTraverse(Foldernames=File.Allfiles(folderpath),Folderpath=folderpath)
        
        # Userdetails=os.getenv("Userfolder") or r"D:\CODE\PYTHON\CODE\Projects\Personaldrive\userdetails"
        # UserFile=os.path.join(Userdetails,self.userid)
        # with open(file=f"{UserFile}.json",mode="w") as Output:
        #     json.dump(self.Directory,Output,indent=4)
        
        File.jsonwrite(self.userid,data=self.Directory,fileindent=4)
    def FolderTraverse(self,Foldernames,Folderpath):
            # print(Foldernames)
            Data=[]
            for Folder in Foldernames:
                Dirpath=File.joinpath(Folderpath,Folder) 
  
                if File.isdirectory(Dirpath):
                    Data.append({
                        "Name":str(Folder),
                        "type":"Folder",
                        "path":str(Dirpath),
                        "children":str(self.FolderTraverse(Folderpath=Dirpath,
                                                       Foldernames=File.Allfiles(Dirpath))) })
                    
                else:
                    Data.append({
                        "Name":str(Folder),
                        "path":str(Dirpath),
                        "Type":str(File.getextenstion(Dirpath))
                        
                    })
            return Data
    

def Createfilestructure(userid):
    # FolderStructure(userid=str(userid))
    try:
        FolderStructure(userid=str(userid))
        return 1
    except Exception as e:
        # print(e)
        return 0 #User Donot exist

 
if __name__=="__main__":
    print(Createfilestructure(1))