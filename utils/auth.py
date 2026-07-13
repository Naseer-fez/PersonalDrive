from flask import request, jsonify
from flask_jwt_extended import decode_token
from flask_jwt_extended.exceptions import JWTExtendedException
import os
PUBLIC = {
    "login.home", #Login 
    "createaccount.home", #Create account
    "public.Home", # filesharing
    "forgot.home", #forgotpassword
    "forgot.code",#codeofemail
    "forgot.verify",#verify page
    "docs.home"#API Documentation
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
        if auth_header==os.getenv("accesstooken") and auth_header is not None:
            return ## Meaning1 the backend has sent the request
        try:
           value=decode_token(auth_header)
           
        except JWTExtendedException:
            return jsonify({"error": "Unauthorized"}), 401
        except Exception:
            return jsonify({"error": "Unauthorized"}), 401
        return

    return
