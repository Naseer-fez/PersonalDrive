from flask import Blueprint,jsonify
from utils.Storage import get_storage
from utils.acceptjson import getjson
from utils.updatespace import updatespace
from utils.FolderStructure import updatefilestructure
from utils.trashfile import addtotrash
deletefilebp=Blueprint("delete",__name__)

Fileoperation=get_storage()
@deletefilebp.route("/deletefile/<int:userid>/",methods=["DELETE"])
@getjson
def Home(userid,data):
    userid=str(userid)
    filename=str(data.get("filepath"))
    operation=operation = 1 if data.get("trash") is None else data.get("trash")
    replace= 0 if data.get("replace") is None else data.get("replace")
    tosend=deletefile(userid=(userid),filename=filename,operation=operation,replace=replace)
    filesize=tosend[2]
    if tosend[0] ==0:
        return jsonify({"return":tosend[1]}),400
    if not operation:
        updatespace(userid=userid,operation=-filesize)
    #The frontend should update the 
    updatefilestructure(Userid=userid,Updates=filename,operation="delete")        
    return jsonify({"return":tosend[1]}),200
    
    
    
def deletefile(userid,filename,operation,replace=0):

    try:
        filesize=Fileoperation.Filesize(userid=userid,filepath=filename)
        if not operation:
            Fileoperation.deletefile(userid=userid,filepath=filename)
            return [1,"Moved succesfully",filesize]
        Fileoperation.movetotrash(userid,filename)
        addtotrash(userid=userid,filepath=filename)
        return [1,"Moved to trash",None]
    except FileNotFoundError as e:
        return [0,"Filenotfound",None]
    except FileExistsError as e: #measn a file arely of smae name is in trash
        if replace:
            try:
                import shutil
                import os
                trash_item_path = Fileoperation.getfilepath(userid=userid, filename=Fileoperation.joinpath(Fileoperation.trash, filename))
                if Fileoperation.isdirectory(trash_item_path):
                    shutil.rmtree(trash_item_path)
                else:
                    os.unlink(trash_item_path)
                Fileoperation.movetotrash(userid, filename)
                addtotrash(userid=userid, filepath=filename)
                return [1, "Moved to trash (replaced existing)", None]
            except Exception as delete_ex:
                return [0, f"Failed to replace existing trash item: {str(delete_ex)}", None]
        oldpath=filename
        filename=Fileoperation.gettheprefix(userid=userid,tosavepath=filename)
         ##copying the data from that file to another file 
        if filename:
            Fileoperation.locationchnage(userid=userid,tochange=filename,oldpath=oldpath)
            return [1,"Moved to trash",None]
        return [0,"similar files already exist",None]
    except PermissionError as e:
        return [0, "Something went wrong please try again ",None]

    except Exception as e:

        return [0, str(e),None]


    