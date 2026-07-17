from flask import request, jsonify, g
from flask_jwt_extended import decode_token
from flask_jwt_extended.exceptions import JWTExtendedException
import os
from config import config
PUBLIC = {
    "login.home", #Login 
    "createaccount.home", #Create account
    "public.Home", # filesharing
    "forgot.home", #forgotpassword
    "forgot.code",#codeofemail
    "forgot.verify",#verify page
    "docs.home",#API Documentation
    "health.home" #Health check
}

def enableauth(app):

    @app.before_request
    def enforcingauth():
        if request.method == "OPTIONS":
            return
        if request.endpoint in PUBLIC:
            return
        # return #For testing right now
        auth_header = request.headers.get("auth", "")
        
        api_key = config.get("api_key")
        if auth_header and (auth_header == os.getenv("accesstooken") or (api_key and auth_header == api_key)):
            return ## Meaning1 the backend has sent the request
        try:
           value=decode_token(auth_header)
           g.username = value.get("sub")
        except JWTExtendedException:
            return jsonify({"error": "Unauthorized"}), 401
        except Exception:
            return jsonify({"error": "Unauthorized"}), 401
        return

    return

