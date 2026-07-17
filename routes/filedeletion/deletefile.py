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
    
    trash_val = data.get("trash")
    try:
        operation = 1 if trash_val is None else int(trash_val)
    except (ValueError, TypeError):
        operation = 1 if str(trash_val).lower() == 'true' else 0

    replace_val = data.get("replace")
    try:
        replace = 0 if replace_val is None else int(replace_val)
    except (ValueError, TypeError):
        replace = 1 if str(replace_val).lower() == 'true' else 0
        
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
            return [1,"Moved successfully",filesize]
        Fileoperation.movetotrash(userid,filename)
        addtotrash(userid=userid,filepath=filename)
        return [1,"Moved to trash",None]
    except FileNotFoundError as e:
        return [0,"Filenotfound",None]
    except FileExistsError as e: #means a file already of same name is in trash
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
            addtotrash(userid=userid,filepath=filename)
            return [1,"Moved to trash",None]
        return [0,"similar files already exist",None]
    except PermissionError as e:
        return [0, "Something went wrong please try again",None]

    except Exception as e:

        return [0, str(e),None]


    