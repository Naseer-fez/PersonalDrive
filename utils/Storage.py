import os 
from dotenv import load_dotenv
from pathlib import Path
import json
load_dotenv()


class LocalStorage:
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
        basedir=self.source/str(userid)/filename

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
    
    def readdata(self,filename,Sizeofdata): #cannot be more modular 
            with open(file=filename,mode="rb") as output:
                    while True:
                        chunk=output.read(1024*1024*Sizeofdata)
                        if not chunk:
                            break  
                        yield chunk

    
    def jsonwrite(self,userid,data,fileindent=4):
        File=self.__openfile(userid,filename=None,filemode="w")
        with File:
            json.dump(data,File,indent=fileindent)
        return 1
    
    def jsonread(self,userid):
            File=self.__openfile(userid,filename=None,filemode="r")
            Data={}
            try:
                with File:
                    Data=json.load(File)
                    return Data
            except Exception as e:
                print(e)
                return 0
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

    def getreativepath(self,userid,filename):
        filepath=Path(filename)
        Breakthepath=filepath.parts

        if userid in Breakthepath:
            finalpath=Breakthepath.index(userid)
            newpath=Path(*Breakthepath[finalpath+1:])
            return str(newpath)    
        else:
            
            return str(filepath)
    
    def getextenstion(self,filepath):
        return os.path.splitext(filepath)[1]
    
    def Allfiles(self,Folderpath):
        return os.listdir(path=Folderpath)
    
    def pathexist(self,dirpath):
        return os.path.exists(dirpath)
    
    def Filesize(self,userid,filepath):
        filename=self.getreativepath(userid=userid,filename=filepath)
        filepath=self.getfilepath(userid=userid,filename=filename)
        return os.path.getsize(filepath)

    def Createfolder(self,userid,filepath):
        filename=self.getreativepath(userid=userid,filename=filepath)
        filepath=self.getfilepath(userid=userid,filename=filename)
        return Path(filepath).mkdir(parents=True, exist_ok=True)
    
    def getfilename(self,userid,filepath):
        filename=self.getreativepath(userid=userid,filename=filepath)
        filepath=self.getfilepath(userid=userid,filename=filename)
        return Path(filepath).name

    def deletefile(self,userid,filepath):
        filename=self.getreativepath(userid=userid,filename=filepath)
        filepath=self.getfilepath(userid=userid,filename=filename)
        file=Path(self.joinpath(filepath,filename))

        os.remove(file)

    def fileexist(self,userid,filepath):
        filename=self.getreativepath(userid=userid,filename=filepath)
        filepath=self.getfilepath(userid=userid,filename=filename)
        return os.path.exists(filepath)
    
    def rename(self,userid,filepath,tochange):
        filename=self.getreativepath(userid=userid,filename=filepath) #Get the fileloaction in the savedirectory
        filepath=self.getfilepath(userid=userid,filename=filename) #get the root directory
        file=Path(self.joinpath(filepath,filename))        # join the path d://user
        newfilepath=self.joinpath(filepath,tochange) #this ifot the new apth
        os.rename(file,newfilepath)     #reanem the file
        return 1
    
    def locationchnage(self,userid,oldpath,tochange):
           #First get the file paths
            basepath=(self.getfilepath(userid=userid,filename=oldpath)).parent
            oldpathlocation=self.joinpath(basepath,oldpath)
            tochangeparent=Path(tochange).parent
            newlocation=self.joinpath(basepath,tochangeparent)
            #First create the directory
            Path(newlocation).mkdir(parents=True, exist_ok=True) #Folder is created 
            filename=(Path(tochange).name) #extract the filename 
            #Now copy the files
            newlocation=newlocation/filename
            # self.__filecopy(source=oldpathlocation,destination=newlocation) #Binnary chunking
            os.rename(oldpathlocation,newlocation)
            
        #    self.Createfolder(userid=userid,filepath=Path(newlocation))
    def __filecopy(self,source,destination):
        SIZE=1024*1024*int(os.getenv("size"), 16)
        with open (source,mode="rb") as SRC:
            with open(destination,mode="wb") as DES:
                while True:
                    Chunk=SRC.read(SIZE)
                    if not Chunk:
                        break
                    DES.write(Chunk)
        os.remove(source)

def get_storage():
    return LocalStorage()


if __name__=="__main__":
    file=LocalStorage()
    # print(file.writedata("1","bzjk.txt","hheheh"))
    print(file.joinpath("1",["12","22"]))
    