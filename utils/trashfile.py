from .Storage import get_storage
import os
import shutil
Fileoperation=get_storage()


def recovertrash(userid,trashpath):
    userid=str(userid)
    data,filepath=Fileoperation.trashdata(userid=userid)
    if data is None or data == 0: return[0]
    trashpath=str(trashpath)
    
    def clean_path(p):
        p = p.replace("\\", "/").strip("/")
        trash_prefix = f"{Fileoperation.trash}/"
        if p.startswith(trash_prefix):
            p = p[len(trash_prefix):]
        return p

    target = clean_path(trashpath)
    matched_key = None
    oldpath = None
    
    for key, val in data.items():
        if clean_path(key) == target:
            matched_key = key
            oldpath = val
            break
            
    if oldpath is None:
        return 0
        
    toreturn= Fileoperation.recoverfromtrash(userid=userid,oldpath=oldpath,trashpath=matched_key)
    if not toreturn:
        return 0
    del data[matched_key]
    Fileoperation.jsonwrite(userid=userid,data=data,filepath=filepath)
    return 1

                
def addtotrash(userid,filepath):
    userid=str(userid)
    filepath=Fileoperation.getreativepath(userid=userid,filename=filepath)
    PATH=Fileoperation.gettrashjson(userid=userid)
    data=Fileoperation.jsonread(userid=userid,path=PATH)
    if data == 0:
        PATH.parent.mkdir(parents=True, exist_ok=True)
        data=dict()
    trashfile=Fileoperation.joinpath(Fileoperation.trash,filepath)
    data[str(trashfile)]=filepath
    return [Fileoperation.jsonwrite(userid=userid,data=data,filepath=PATH)]
        
        
        
        
def deletefromtrash(userid, trashpath):
    userid = str(userid)
    data, filepath = Fileoperation.trashdata(userid=userid)
    if data is None or data == 0:
        return 0
    trashpath = str(trashpath)
    
    def clean_path(p):
        p = p.replace("\\", "/").strip("/")
        trash_prefix = f"{Fileoperation.trash}/"
        if p.startswith(trash_prefix):
            p = p[len(trash_prefix):]
        return p

    target = clean_path(trashpath)
    matched_key = None
    
    for key, val in data.items():
        if clean_path(key) == target:
            matched_key = key
            break
            
    if matched_key is None:
        return 0
        
    abspath = Fileoperation.getfilepath(userid=userid, filename=matched_key)
    try:
        if Fileoperation.isdirectory(abspath):
            shutil.rmtree(abspath)
        else:
            os.unlink(abspath)
    except Exception:
        pass
        
    del data[matched_key]
    Fileoperation.jsonwrite(userid=userid, data=data, filepath=filepath)
    return 1


if __name__=="__main__":
    print(recovertrash("2",r"hello\README.md"))