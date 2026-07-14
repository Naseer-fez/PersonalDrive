from flask import Blueprint,jsonify


healthbp=Blueprint("health",__name__)



@healthbp.route("/",methods=["GET"])
@healthbp.route("/health",methods=["GET"])
def home():
    return jsonify({"return":"server running"}),200