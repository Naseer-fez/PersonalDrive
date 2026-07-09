import time 
from utils.Databaseop import getemail
Data={}
def __inputval(email,otp):
    global Data
    Data[email]={"OTP":otp,"ALLOW":int(time.time())+(60*10)}
    
    
def __Validiator(email,otp):
    global Data
    curnt=int(time.time())
    statuscode=400
    if email not in Data:
        return [{"Report":"No Record of that email"},statuscode]
    values= Data[email]
    if values["OTP"]!=otp:
        return [{"Report":"Wrong OTP"},statuscode]
    if values["ALLOW"]<curnt:     
        del Data[email]
        return [{"Report":"Time Exceded"},statuscode]
    statuscode=200
    #Now i need to check the db for the availablity of the users email
    
    code=getemail(email=email)
    if not code[0]:
        return [{"Report":f"Their has been a error:{code[1]}"},400]
    return [1,{
             "code":code[0],
             "userid":code[1]}],200


def STORAGE(email,otp,action="Create"):
    if action=="check":
        info=__Validiator(email,otp)
        return info[0],info[1]
    values=__inputval(email,otp)
    return "code has been sent to your email",200


