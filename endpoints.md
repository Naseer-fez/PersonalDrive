# API ENDPOINT GUIDE:
___

## File upload
### <u>Endpoint</u>:
#### uploadfile/<int:Userid>
Method:POST
### <u>Data accepted</u>: 
#### Form: directory and files
### <u>Return:</u> JSON(key)->return 
___
## Folder Upload
### <u>Endpoint</u>:
#### uploadfolder/ <int:Userid>
Method:POST
### <u>Data accepted</u>: 
#### directory and List of files  
### <u>Return:</u> JSON(key)->return 
___
## File/Folder Download
### <u>Endpoint</u>:
#### download/ <int:Userid>
Method:GET
### <u>Data accepted</u>: 
#### JSON: filename(key) :could be file or folder 
### <u>Return:</u> 
#### Failure:JSON(key)->return 
#### Success:File (mimetype,size,file,header),              Folder (zip)  
___
## Share File or Folder 
### <u>Endpoint</u>:
#### share/ <int:Userid>
Method:POST
### <u>Data accepted</u>: 
#### JSON: filename(key) :could be file or folder 
### <u>Return:</u> 
#### JSON(key)->return :LINK 
___
## Access  File or Folder Through link *
### <u>Endpoint</u>:
#### share/<int:userid>/<string:filesharing>/<int:time>/<string:token>
 **All these are part of the Link**<br>
Method:GET
### <u>Data accepted</u>: 
#### NONE 
### <u>Return:</u> 
#### Failure:JSON(key)->return 
#### Success: File (mimetype,size,file,header),              Folder (zip) 
___
## Folder Structure
### <u>Endpoint</u>:
#### structure/ <int:Userid>
#### structure/ <int:Userid> / <int:folder>
Method:GET
### <u>Data accepted</u>: 
#### NONE
### <u>Return:</u> 
#### Failure:JSON(key)->return 
#### Success:  JSON file structure
**NOTE:No folder send the complete folder structure** 

### **GET NUM OF FOLDERS**:
### <u>Endpoint</u>:
####folders/<int:userid>
Method:GET
### <u>Data accepted</u>: 
#### NONE
### <u>Return:</u> 
#### JSON(key)->return 
**NOTE:Return the number of folders of the user**
___
## File/Folder Delete
### <u>Endpoint</u>:
#### deletefile/<int:userid>/
Method:DELETE
### <u>Data accepted</u>:
#### JSON: filepath(key) ,trash(key) 
**Trash is optional if it is 1 means delete the file completely** 
### <u>Return:</u> 
#### JSON(key)->return 
___
## Delete From Trash
### <u>Endpoint</u>:
#### trash/<int:userid>/
Method:DELETE
### <u>Data accepted</u>:
#### JSON: filepath(key) 
### <u>Return:</u> 
#### JSON(key)->return 
___
## File/Folder Rename
### <u>Endpoint</u>:
#### updatefile/<int:userid>/
Method:PUT
### <u>Data accepted</u>:
#### JSON: filename(key) ,newname(key) 
### <u>Return:</u> 
#### JSON(key)->return 
___
## Folder Directory (empty)
### <u>Endpoint</u>:
#### createfolder/<int:userid>/
Method:PUT
### <u>Data accepted</u>:
#### JSON: filename(key) (The directory)
### <u>Return:</u> 
#### JSON(key)->return 
___
## Change File Location
### <u>Endpoint</u>:
#### changefilelocation/<int:userid>/
Method:PUT
### <u>Data accepted</u>:
#### JSON: oldpath(key) ,newpath(key) 
### <u>Return:</u> 
#### JSON(key)->return 
___
## File Search
### <u>Endpoint</u>:
#### searchfile/<int:userid>/<string:filename>/
Method:GET
### <u>Data accepted</u>:
#### NONE
### <u>Return:</u> 
#### JSON(key)->return :List of all the file 
___
## Get User Space Usage
### <u>Endpoint</u>:
#### userstats/<int:userid>/
Method:GET
### <u>Data accepted</u>:
#### NONE
### <u>Return:</u> 
#### JSON(key)->return :<int:space> 
___
## Create Account *
### <u>Endpoint</u>:
#### createaccount/
Method:POST
### <u>Data accepted</u>:
#### JSON(Keys): username,password,email(optional) 
### <u>Return:</u>
#### Failure:JSON(key)->return 
#### Success:   JSON(key)->return :token:<JWT:> ,userid:<int:userid>
___
## LOGIN *
### <u>Endpoint</u>:
#### login/
Method:POST
### <u>Data accepted</u>:
#### JSON(Keys): username,password,email(optional) 
**Email login also is available as a choice**
### <u>Return:</u>
#### Failure:JSON(key)->return 
#### Success:   JSON(key)->return :token:<JWT:> ,userid:<int:userid>
___
## DELETE Account
### <u>Endpoint</u>:
#### deleteacc/
Method:DELETE
### <u>Data accepted</u>:
#### JSON(Keys): username,password,email(optional) 
### <u>Return:</u>
#### JSON(key)->return 
___
## Update Account
### <u>Endpoint</u>:
#### updateacc/
Method:PUT
### <u>Data accepted</u>:
#### JSON(Keys): username,password,email(optional) 
### <u>Return:</u>
#### Failure:JSON(key)->return 
#### Success:   JSON(key)->return:token:<JWT:> ,userid:<int:userid>
**Can be used for changed the password ,username or the email **
___
___
## Forgot Password *
### <u>Endpoint</u>:
#### forgot/
Method:POST
### <u>Data accepted</u>:
#### JSON(Keys): email
### <u>Return:</u>
#### JSON(key)->return 

## Code Verification:*  
### <u>Endpoint</u>:
#### forgot/code/
Method:POST
### <u>Data accepted</u>:
#### JSON(Keys): email .Header-> opt
### <u>Return:</u>
#### Failure:JSON(key)->return :Message
#### Success: JSON(key)->return:token:
**This token to be sent in the header of the for the next endpoint**

## Change Password:*  
### <u>Endpoint</u>:
#### verify/code/
Method:POST
### <u>Data accepted</u>:
#### JSON(Keys):Header-> token,email,password 
### <u>Return:</u>
#### Failure:JSON(key)->return :Message
#### Success: JSON(key)->return:token:

___

### PUBLIC LINKS: login,createacc,forgot,forgot/code,verify/code,share
### * Denotes public links which can be accesed without the JWT token
### If not public then :
### . Always send JWT token through the header file
### .  ** "auth"** is the key which need the JWT token
### . Send the JWT directly.
___
### JSON STRUCTURE

```json
{
    keyᵢ: valueᵢ
} 
```
## ** The Process is only sucessful when the status code is 200**






















