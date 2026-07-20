from utils.Storage import get_storage
from utils.FolderStructure import Createfilestructure
from utils.updatespace import jsonoperation,checkchanges
from rapidfuzz import process,fuzz
Fileoperation=get_storage()

def searchfile(userid,tofind):
    # Check if the user exists
    exists, _ = Fileoperation.userexist(str(userid))
    if not exists:
        return [-1, "User not found"]
        
    filepath=Fileoperation.getfilesjson(userid) #create a substitute of this
    checkchanges(userid=userid) #Because i need accurate files so , the createfolder will do that for me 
    filedata=Fileoperation.jsonread(userid=userid,path=filepath) #meaning reading the cache file path
    if not isinstance(filedata, dict):
        filedata=createfilescache(userid,filepath)
        if filedata==-1:
            return [-1,"User not found"]
        if not isinstance(filedata, dict):
            return [-1, "Failed to load files cache"]
    filedata=filelookup(filename=tofind,source=filedata)
    return filedata[0],filedata[1]
    
def createfilescache(userid,path):


    #First verify that the user is available
    result,filepath=(Fileoperation.userexist(str(userid)))
    if not  result:
        return -1
    Createfilestructure(userid=userid)
    return Fileoperation.jsonread(userid=userid,path=path)
    #Now start searching for the user

def filelookup(filename,source):
    #time to search this si better for eact search 
    # if filename  in source:
    #     return [1,source[filename]]
    # else:
    #     return [-1,"No file found"]
    matches=process.extract(
        query=filename,
        choices=source.keys(),
        scorer=fuzz.WRatio,
        limit=20,
        score_cutoff=60
        
    )
    if not matches:
        return [-1,"No file found"]
    results=[]
    for name,_,__ in matches:
        paths = source.get(name, [])
        if isinstance(paths, list):
            results.extend(paths)
        else:
            results.append(paths)
    return [1,results]


if __name__=="__main__":
    pass