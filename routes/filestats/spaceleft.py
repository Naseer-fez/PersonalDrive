from flask import Blueprint,jsonify
from utils.Storage import get_storage
from utils.acceptjson import getjson

spacebp=Blueprint("spacebp",__name__)

Fileoperation=get_storage()
@spacebp.route("/spaceleft/<int:userid>/",methods=["GET"])
def Home(userid):
    usedspace=totalspaceused(userid)
    if usedspace==-1:
        return jsonify({"return":"The user do not exist"}),400
    return jsonify({"retutn":int(usedspace)}),200
    


def getsize(node):
    # File
    if node["type"] != "Folder":
        return node["size"]

    # Folder
    total = 0
    for child in node["children"]:
        total += getsize(child)
    return total


def totalspaceused(userid):
    try:
        DIR = Fileoperation.jsonread(userid=userid)
    except FileNotFoundError as e:
        return -1
    total = 0

    for root in DIR:
        total += getsize(root)

    return total
    
    


# def getspace():