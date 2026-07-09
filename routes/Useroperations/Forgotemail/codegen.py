import secrets
import string
from utils.sendemail import Messages_to_send


def OTP(email,length=4):
    Code=__digitcode()
    # (to,content:str,subject=None,frm=email)
    Subject="Your Verfication Code For Tap Nap"
    Content=f"""
    You Verfication Code to Log in Cloud Storage  is {Code}
    Dont Share your otp with anyone else.
    This code is only valid for  10 Mins only,After that u have to send the code again.
    
    """
    statement=Messages_to_send(to=email,subject=Subject,content=Content) 
    if not statement[0]:
        return [0,statement[1]]
    return [1,Code]
    


def __digitcode(length=4):
    characters = string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))
    

