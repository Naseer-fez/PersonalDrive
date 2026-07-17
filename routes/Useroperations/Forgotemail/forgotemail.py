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
def code(data):
    code=request.headers.get("otp")
    if not code:
        return jsonify({"return":"no otp sent"}),401
    email=data.get("email")
    if not email:
        return jsonify({"return":"no email sent"}),401
    info=STORAGE(email=email,otp=code,action="check")
    if not (info[0]):
            return jsonify(info[1]),401
    return jsonify(info[1]),200
    
    
@forgotbp.route("/verify/code/",methods=["POST"])
@getjson
def verify(data):
    code=request.headers.get("token")
    if not code:
        return jsonify({"return":"no token sent"}),401
    password=data.get("password")
    email=data.get("email")
    value=STORAGE(email=email,password=password,token=code,action="token")
    if not value[0]:
        return jsonify(value[1]),401
    return jsonify({"return":"Password changed"}),200
    
    

    