from flask import Blueprint,jsonify,request
from utils.acceptjson import getjson
from .codegen import OTP
from .memdb import STORAGE
forgotbp=Blueprint("forgot",__name__)

@forgotbp.route("/forgot/",methods=["POST"])
@getjson
def home(data):
    email=data.get("email")
    if not email:
        return jsonify({"return":"no email sent"}),401
    code=OTP(email=email)
    if not code[0]:
        return jsonify({"return":code[1]})
    STORE=STORAGE(email,code[1])
    return jsonify({"return":STORE[0]}),STORE[1]





@forgotbp.route("/forgot/code/",methods=["POST"])
@getjson
def verify(data):
    code=request.headers.get("otp")
    if not code:
        return jsonify({"return":"no otp sent"}),401
    email=data.get("email")
    if not email:
        return jsonify({"return":"no email sent"}),401
    info=STORAGE(email=email,otp=code,action="check")
    if(info[1])==400:
            return jsonify(info[0]),info[1]
    return jsonify(info[0]),info[1]
    
    