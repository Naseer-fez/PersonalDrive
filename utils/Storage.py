import os 
from dotenv import load_dotenv
from pathlib import Path
import json
load_dotenv()


class Storage:
    def __init__ (self):
        self.source=Path(os.getenv("DestinationFolder"))
        self.userdetails=Path(os.getenv("Userfolder"))
    def getfilepath(self,userid,filename=None,folderreq=0):
        if folderreq==1:
            basedir=self.source
            basedir=basedir/userid
            return basedir
        if filename is None: #For json file
            basedir=self.userdetails
            return basedir/f"{userid}.json"
        basedir=self.source/str(userid)
        return basedir

    
    def __openfile(self,userid,filename,filemode,Folderuse=1):
        filepath=self.getfilepath(filename=filename,userid=str(userid))
        output= open(filepath,mode=filemode) 
        return output
    
    def writedata(self,userid,filename,data):
        File=self.__openfile(userid=userid,filename=filename,filemode="w")
        with File:
            File.write(data)
        return 1
    
    def appendata(self,userid,filename,data):
        File=self.__openfile(userid=userid,filename=filename,filemode="ab")
        with File:
            File.write(data)
        return 1
    
    def readdata(self,userid,filename,Chunks):
        File=self.__openfile(userid=userid,filename=filename,filemode="rb")
        with File:
            File.read(Chunks)
        return 1
    
    def jsonwrite(self,userid,data,fileindent=4):
        File=self.__openfile(userid,filename=None,filemode="w")
        with File:
            json.dump(data,File,indent=fileindent)
        return 1
    
    def jsonread(self,userid):
            File=self.__openfile(userid,filename=None,filemode="r")
            Data={}
            with file:
                Data=json.load()
            return 1
    #Small operations
    def isdirectory(self,pathobj):
        return os.path.isdir(pathobj)
    
    def joinpath(self,Currentpath,tojoin):
        Currentpath=Path(Currentpath)
        if isinstance(tojoin, list):
            for  path in tojoin:
                Currentpath=Currentpath/path
            return Currentpath          
        return Currentpath/tojoin
    
    def getextenstion(self,filepath):
        return os.path.splitext(filepath)[1]
    
    def Allfiles(self,Folderpath):
        return os.listdir(path=Folderpath)
    
    def pathexist(self,dirpath):
        return os.path.exists(dirpath)
    
    def Filesize(self,Filepath):
        return os.path.getsize(Filepath)

    def Createfolder(self,filepath):
        return Path(filepath).mkdir(parents=True, exist_ok=True)
    
    def getfilename(self,filepath):
        return Path(filepath).name

    def deletefile(self,filepath):
        return os.remove(filepath)


def get_storage():
    return Storage()


if __name__=="__main__":
    file=Storage()
    # print(file.writedata("1","bzjk.txt","hheheh"))
    print(file.joinpath("1",["12","22"]))