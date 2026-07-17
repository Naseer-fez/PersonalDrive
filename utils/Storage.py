from dotenv import load_dotenv
from pathlib import Path
import json
import shutil
from datetime import datetime
from stream_zip import stream_zip, ZIP_64
import os
from config import config

class LocalStorage:
    def __init__ (self):
        self.source = Path(config.get("DestinationFolder","Data"))
        self.userdetails = Path(config.get("Userfolder","userdetails"))
        self.trash = str(config.get("trash", "trash"))
        self.statsjson = str(config.get("stats", "stats.json"))
        self.totalfiles = str(config.get("file", "files.json"))
        self.trashjson = str(config.get("trashfile", "trash.json"))
    def getfilepath(self,userid,filename=None,folderreq=0):
        if folderreq==1:
            basedir=self.source/str(userid)
            return basedir
        if filename is None: #For json file
            basedir=self.userdetails/str(userid)
            return basedir/f"{userid}.json"
        # Sanitize the filename/path to prevent resetting base path to drive root or traversing directories
        clean_parts = []
        for part in Path(filename).parts:
            cleaned = part.rstrip('\\/')
            if cleaned.endswith(':') or cleaned in ('', '.', '..'):
                continue
            clean_parts.append(part)
        
        # Resolve path inside the main trash folder: DestinationFolder/trash/userid/
        if clean_parts and clean_parts[0] == self.trash:
            safe_filename = Path(*clean_parts[1:])
            return self.source / self.trash / str(userid) / safe_filename
            
        safe_filename = Path(*clean_parts)
        basedir=self.source/str(userid)/safe_filename

        return basedir

    
    def __openfile(self,userid,filename,filemode,Folderuse=1):
        if Folderuse ==0:
            filepath=filename
        else:
            filepath=self.getfilepath(filename=filename,userid=str(userid))
            
        # Auto-create user files/directories if accessing root structure and it doesn't exist
        if filename is None and "r" in filemode and not os.path.exists(filepath):
            self.createnewuser(userid)
            
        # Auto-create parent directory if opening in write/append mode
        if "w" in filemode or "a" in filemode:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
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
        def file_generator():
            for root,dirs,files in os.walk(filename):
                for file in files:
                    filepath=os.path.join(root,file)
                    archfile=os.path.relpath(filepath,filename).replace("\\","/")
                    stat_info=os.stat(filepath)
                    mtime=datetime.fromtimestamp(stat_info.st_mtime)
                    mode=stat_info.st_mode
                    def read_file_chunks(path):
                        with open(path,'rb') as f:
                            while True:
                                chunk=f.read(64*1024)
                                if not chunk:
                                    break
                                yield chunk
                    yield (archfile,mtime,mode,ZIP_64,read_file_chunks(filepath))
        chunksize=1024*1024*int(size)
        buffer=bytearray()
        for zipped_chunk in stream_zip(file_generator()):
            buffer.extend(zipped_chunk)
            while len(buffer)>=chunksize:
                yield bytes(buffer[:chunksize])
                del buffer[:chunksize]
        if buffer:
            yield bytes(buffer)
                
    def jsonwrite(self,userid,data,fileindent=4,filepath=None):
        if filepath is None:
            File=self.__openfile(userid,filename=None,filemode="w")
        else:
            File=self.__openfile(userid=userid,filename=filepath,filemode="w",Folderuse=0)
        with File:
            json.dump(data,File,indent=fileindent)
        return 1
    
    def jsonread(self,userid,path=None):
            try:
                if path is None:
                    File=self.__openfile(userid,filename=None,filemode="r")
                else:
                    File=path.open()
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
        
        def safe_relative(p):
            clean_parts = []
            for part in Path(p).parts:
                cleaned = part.rstrip('\\/')
                if cleaned.endswith(':') or cleaned in ('', '.', '..'):
                    continue
                clean_parts.append(part)
            return Path(*clean_parts)

        if isinstance(tojoin, list):
            for  path in tojoin:
                Currentpath=Currentpath/safe_relative(path)
            return Currentpath          
        return Currentpath/safe_relative(tojoin)

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
            return filepath
        except Exception as e:
            return 0
    def createnewuser(self,userid):
        userid=str(userid)
        filepath=self.source/userid
        jsn=f"{userid}.json"
        jsonfilepath=self.userdetails/userid/jsn
        Path(filepath).mkdir(parents=True, exist_ok=True)
        Path(jsonfilepath).parent.mkdir(parents=True, exist_ok=True)
        self.jsonwrite(userid=userid, data=[], filepath=jsonfilepath)
        trashpath = self.getfilepath(userid=userid, filename=self.trash)
        Path(trashpath).mkdir(parents=True, exist_ok=True)
        return 

    def fileexist(self,userid,filepath):
        filename=self.getreativepath(userid=userid,filename=filepath)
        filepath=self.getfilepath(userid=userid,filename=filename)
        return os.path.exists(filepath)
    
    def rename(self,userid,filepath,tochange):
        filename=self.getreativepath(userid=userid,filename=filepath) #Get the fileloaction in the savedirectory
        filepath=self.getfilepath(userid=userid,filename=filename) #get the root directory
        newfilename=self.getreativepath(userid=userid,filename=tochange)
        newfilepath=self.getfilepath(userid=userid,filename=newfilename)
        os.rename(filepath,newfilepath)     #rename the file
        return 1
    def trashdata(self,userid):
        userid=str(userid)
        filepath=self.gettrashjson(userid=userid)
        data=self.jsonread(userid,path=filepath)
        return [data,filepath]
        
        
    def locationchnage(self,userid,oldpath,tochange):
        # Resolve source absolute path
        oldpathlocation = self.getfilepath(userid=userid, filename=oldpath)
        
        # Resolve destination absolute path
        tochange_path = Path(tochange)
        if tochange_path.is_absolute():
            newlocation = tochange_path
        else:
            newlocation = self.getfilepath(userid=userid, filename=tochange)
        if os.path.isdir(newlocation):
            newlocation = newlocation / Path(oldpathlocation).name
            
        # Create destination parent directory if it does not exist
        newlocation.parent.mkdir(parents=True, exist_ok=True)
        
        # Move the file/folder
        os.rename(oldpathlocation, newlocation)
        return 1
            
        #    self.Createfolder(userid=userid,filepath=Path(newlocation))
    def __filecopy(self,source,destination):
        SIZE=1024*1024*int(config.get("size",16))
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
        filename = self.getreativepath(userid=userid, filename=filename)
        oldpath = self.getfilepath(userid=userid, filename=filename)
        newpath = self.getfilepath(userid=userid, filename=self.joinpath(self.trash, filename))
        newpath.parent.mkdir(parents=True, exist_ok=True) #create the directory
        os.rename(oldpath, newpath)
        
    def gettheprefix(self,userid,tosavepath):
        tosavepath=Path(tosavepath)
        tosavepath=Path(self.trash)/tosavepath
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
    def gettrashjson(self,userid):
            PATH=self.getfilepath(userid=userid)
            PATH=PATH.parent/self.trashjson
            return PATH 
    def recoverfromtrash(self,userid,trashpath,oldpath):
        trashpath = self.getfilepath(userid=userid, filename=trashpath)
        oldpath = self.getfilepath(userid=userid, filename=oldpath)
        oldpath.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.rename(trashpath,oldpath)
            return 1
        except OSError as e:        
            return 0
def get_storage():
    return LocalStorage()


if __name__=="__main__":
    file=LocalStorage()
    # print(file.writedata("1","bzjk.txt","hheheh"))
    print(file.recoverfromtrash('1',"12121","121"))
    
