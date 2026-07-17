from flask import Blueprint, jsonify
from utils.Storage import get_storage
from pathlib import Path
import os

gettrashbp = Blueprint("gettrash", __name__)
Fileoperation = get_storage()

@gettrashbp.route("/trashdata/<int:userid>/", methods=["GET"])
def Home(userid):
    userid = str(userid)
    PATH = Fileoperation.gettrashjson(userid=userid)
    try:
        data = Fileoperation.jsonread(userid=userid, path=PATH)
        if not isinstance(data, dict):
            data = {}
    except Exception:
        data = {}
        
    trash_items = []
    # data is a dictionary of {trashpath: originalpath}
    # e.g., {"trash/hello.txt": "hello.txt"}
    for trashpath, originalpath in data.items():
        # Get filename (basename of original path)
        name = Path(originalpath).name
        # Get absolute path to check details
        abspath = Fileoperation.getfilepath(userid=userid, filename=trashpath)
        
        # Get size and modified time if exists, otherwise defaults
        size = 0
        modified = 0
        is_dir = False
        if Fileoperation.pathexist(abspath):
            try:
                stat = os.stat(abspath)
                size = stat.st_size
                modified = int(stat.st_mtime)
                is_dir = Fileoperation.isdirectory(abspath)
            except Exception:
                pass
                
        trash_items.append({
            "name": name,
            "path": trashpath,
            "type": "Folder" if is_dir else "file",
            "originalPath": originalpath,
            "size": size,
            "modified": modified
        })
        
    return jsonify(trash_items), 200
