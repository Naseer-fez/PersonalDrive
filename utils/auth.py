from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended.exceptions import JWTExtendedException
PUBLIC = {
    "login.home", #Login 
    "createaccount.home", #Create account
    "public.Home", # filesharing
    "forgot.home" #forgotpassword
    "forgot.verify"#codeofemail
}

def enableauth(app):

    @app.before_request
    def enforcingauth():
        if request.endpoint in PUBLIC:
            return
        return #For testing right now
        auth_header = request.headers.get("auth", "")
        try:
            verify_jwt_in_request()
        except JWTExtendedException:
            return jsonify({"error": "Unauthorized"}), 401
        except Exception:
            return jsonify({"error": "Unauthorized"}), 401

        return

    return
