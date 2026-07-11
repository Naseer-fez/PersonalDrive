import os 
from dotenv import load_dotenv
from pathlib import Path
import json
import shutil
import zipfile
import io
load_dotenv()


class LocalStorage:
    def __init__ (self):
        self.source=Path(os.getenv("DestinationFolder"))
        self.userdetails=Path(os.getenv("Userfolder"))
        self.trash=str(os.getenv("trash","trash"))
        self.statsjson=str(os.getenv("stats","stats.json"))
        self.totalfiles=str(os.getenv("file","files.json"))
    def getfilepath(self,userid,filename=None,folderreq=0):
        if folderreq==1:
            basedir=self.source
            basedir=basedir/str(userid)
            return basedir
        if filename is None: #For json file
            basedir=self.userdetails/str(userid)
            return basedir/f"{userid}.json"
        basedir=self.source/str(userid)/filename

        return basedir

    
    def __openfile(self,userid,filename,filemode,Folderuse=1):
        if Folderuse ==0:
            filepath=filename
        else:
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
    
    def readdata(self,filename,Sizeofdata=None): #cannot be more modular 
            if (self.isdirectory(filename)):
                yield from self.readfolder(filename=filename,size=Sizeofdata)
                return
            if Sizeofdata is not None:
                with open(file=filename,mode="rb") as output:
                        while True:
                            chunk=output.read(1024*1024*int(Sizeofdata))
                            if not chunk:
                                break  
                            yield chunk
            else:
                with open(file=filename,mode="r") as output:
                    yield  output  ##full file
    def readfolder(self,filename,size):
            #first need to zip this 
                inmem=io.BytesIO()
                with zipfile.ZipFile(inmem,"w",zipfile.ZIP_DEFLATED) as zip:
                    for root,dirs,files in os.walk(filename):
                        for file in files:
                            filepath=os.path.join(root,file)
                            archfile=os.path.relpath(filepath,filename)
                            zip.write(filepath,arcname=archfile)
                chunksize=1024*1024*int(size)
                inmem.seek(0)
                try:
                    while True:
                        chunk=inmem.read(chunksize)
                        if not chunk:
                            break
                        yield chunk
                finally:                
                    inmem.close()
                
    def jsonwrite(self,userid,data,fileindent=4,filepath=None):
        if filepath is None:
            File=self.__openfile(userid,filename=None,filemode="w")
        else:
            File=self.__openfile(userid=userid,filename=filepath,filemode="w",Folderuse=0)
        with File:
            json.dump(data,File,indent=fileindent)
        return 1
    
    def jsonread(self,userid,path=None):
            if path is None:
                File=self.__openfile(userid,filename=None,filemode="r")
            else:
                File=path.open()
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
        try:
            if self.isdirectory(pathobj=filepath):
                shutil.rmtree(filepath)
            else:
                
                os.remove(filepath)
            return 1
        except Exception as e:
            return 0
    def createnewuser(self,userid):
        userid=str(userid)
        filepath=self.source/userid
        jsn=f"{userid}.json"
        jsonfilepath=self.userdetails/userid/jsn
        Path(filepath).mkdir(parents=True, exist_ok=True)
        Path(jsonfilepath).mkdir(parents=True, exist_ok=True)
        return 

    def fileexist(self,userid,filepath):
        filename=self.getreativepath(userid=userid,filename=filepath)
        filepath=self.getfilepath(userid=userid,filename=filename)
        return os.path.exists(filepath)
    
    def rename(self,userid,filepath,tochange):
        filename=self.getreativepath(userid=userid,filename=filepath) #Get the fileloaction in the savedirectory
        filepath=self.getfilepath(userid=userid,filename=filename) #get the root directory
        newfilepath=self.joinpath(filepath.parent,tochange) #new path using parent dir + new name
        os.rename(filepath,newfilepath)     #rename the file
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
            return 1
            
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
    def userexist(self,userid):
        userpath=(Path(self.source))/str(userid)
        return [self.isdirectory(userpath),userpath]
    def getfilestats(self,path):
        return  Path(path).stat()
    def filetiming(self,path):
        stats=self.getfilestats(path)
        return {"createdtime":int(stats.st_ctime),"updatedtime":int(stats.st_mtime)}
    def movetotrash(self,userid,filename):
        oldpath=Path(filename)
        newpath=self.trash/oldpath
        return self.locationchnage(userid=userid,oldpath=oldpath,tochange=newpath)
    def gettheprefix(self,userid,tosavepath):
        tosavepath=Path(tosavepath)
        tosavepath=self.trash/tosavepath
        attempts=1000
        prefix=0
        original_stemp=tosavepath.stem
        original_suffix=tosavepath.suffix
        tosavepath=self.getfilepath(userid=userid,filename=tosavepath)
        while attempts:
            if not self.fileexist(userid=userid,filepath=tosavepath):
                # self.__openfile(userid=userid,filename=tosavepath,filemode="w")
                return tosavepath
            attempts=attempts-1
            prefix=prefix+1
            tosavepath=tosavepath.with_name(f"{original_stemp}[{prefix}]{original_suffix}")
        return 0
    def getstatsfile(self,userid):
            PATH=self.getfilepath(userid=userid)
            PATH=PATH.parent/self.statsjson
            return PATH 
    def getfilesjson(self,userid):
        filepath=self.getfilepath(userid=userid,filename=None)
        filepath=filepath.parent/self.totalfiles
        return   filepath
def get_storage():
    return LocalStorage()


if __name__=="__main__":
    file=LocalStorage()
    # print(file.writedata("1","bzjk.txt","hheheh"))
    print(file.joinpath("1",["12","22"]))
    