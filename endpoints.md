# API Reference Guide

This document provides a comprehensive and standardized reference for the PersonalDrive API. 

---

## Authentication & Global Configurations

### Header-Based JWT Authentication
Most endpoints in this API require authentication. PersonalDrive uses custom JWT authentication via the `auth` header.
- **Key**: `auth`
- **Value**: `<JWT_TOKEN>` (passed directly without a `Bearer` prefix)

### Authentication Responses
If a request is sent to a private endpoint without a valid token:
- **Status Code**: `401` (Used as unauthorized in the backend)
- **Response Body**:
  ```json
  {
    "error": "Unauthorized"
  }
  ```

### Response Status Codes
- `200 OK`: The process was successful.
- `400 Bad Request`: Incorrect input or missing parameters.
- `401 Unauthorized`: Authentication failed, invalid credentials, or operation-specific failure or invalid JWT token.
---

## Public Endpoints
These endpoints do not require the `auth` header.

### 1. Create Account
*Create a new user account.*

- **Endpoint**: `/createaccount/`
- **Method**: `POST`
- **Authentication**: None (Public)
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "username": "example_user",
    "password": "secure_password",
    "email": "user@example.com"
  }
  ```
- **Responses**:
  - **Success (`200 OK`)**:
    ```json
    {
      "return": "jwt_token_string_here",
      "userid": 123
    }
    ```
  - **Failure (`401 Unauthorized`)**:
    ```json
    {
      "return": "Error message explaining why creation failed"
    }
    ```

---

### 2. Login
*Authenticate an existing user.*

- **Endpoint**: `/login/`
- **Method**: `POST`
- **Authentication**: None (Public)
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "username": "example_user",
    "password": "secure_password",
    "email": "user@example.com"
  }
  ```
  > [!NOTE]
  > Login can accept either `username` or `email` along with the `password`.
- **Responses**:
  - **Success (`200 OK`)**:
    ```json
    {
      "return": "jwt_token_string_here",
      "userid": 123
    }
    ```
  - **Failure (`401 Unauthorized`)**:
    ```json
    {
      "return": "Invalid Credentials or user not found"
    }
    ```

---

### 3. Forgot Password (Send OTP)
*Initiate the password recovery process by requesting an OTP code.*

- **Endpoint**: `/forgot/`
- **Method**: `POST`
- **Authentication**: None (Public)
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "email": "user@example.com"
  }
  ```
- **Responses**:
  - **Success (`200 OK` or dynamic)**:
    ```json
    {
      "return": "OTP sent successfully"
    }
    ```
  - **Failure (`401 Unauthorized`)**:
    ```json
    {
      "return": "no email sent"
    }
    ```

---

### 4. Code Verification (Verify OTP)
*Verify the OTP received via email to obtain a temporary token for password reset.*

- **Endpoint**: `/forgot/code/`
- **Method**: `POST`
- **Authentication**: None (Public)
- **Content-Type**: `application/json`
- **Headers**:
  - `otp`: `<OTP_CODE>` (Required)
- **Request Body**:
  ```json
  {
    "email": "user@example.com"
  }
  ```
- **Responses**:
  - **Success (`200 OK`)**:
    ```json
    {
      "return": "verification_token_string"
    }
    ```
  - **Failure (`401 Unauthorized`)**:
    ```json
    {
      "return": "Invalid OTP code or email"
    }
    ```

---

### 5. Change Password (Reset Password)
*Reset the password using the token retrieved from the OTP verification.*

- **Endpoint**: `/verify/code/`
- **Method**: `POST`
- **Authentication**: None (Public)
- **Content-Type**: `application/json`
- **Headers**:
  - `token`: `<VERIFICATION_TOKEN>` (Required)
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "new_secure_password"
  }
  ```
- **Responses**:
  - **Success (`200 OK`)**:
    ```json
    {
      "return": "Password changed"
    }
    ```
  - **Failure (`401 Unauthorized`)**:
    ```json
    {
      "return": "Invalid token or password update failed"
    }
    ```

---

### 6. Access Shared File/Folder (Public Access Link)
*Retrieve a shared file or directory using a public access link.*

- **Endpoint**: `/share/<int:userid>/<string:filesharing>/<int:time>/<string:tooken>`
  > [!IMPORTANT]
  > Note the path spelling of `tooken` instead of `token` and `filesharing` representing the Base64-encoded file path.
- **Method**: `GET`
- **Authentication**: None (Public)
- **Responses**:
  - **Success (`200 OK`)**: File binary stream / zip archive (with headers for mimetype, filesize, or attachment disposition).
  - **Failure (`400 Bad Request`)**:
    ```json
    {
      "return": "link expired"
    }
    ```
    *or*
    ```json
    {
      "return": "the tooken which you have recived is invalid"
    }
    ```
    *or (typo in key `retutn`)*:
    ```json
    {
      "retutn": "WrongFile Inputed Tryagain"
    }
    ```

---
### 7. Interactive API Documentation (Playground)
*Access the Swagger-like interactive API documentation playground to view and test all endpoints.*

- **Endpoint**: `/docs`
- **Method**: `GET`
- **Authentication**: None (Public)
- **Responses**:
  - **Success (`200 OK`)**: HTML page (Single-Page Application).

---

## Private Endpoints
These endpoints require the JWT token passed in the `auth` header.

### 8. File Upload
*Upload a single file to the specified directory.*

- **Endpoint**: `/uploadfile/<int:Userid>`
- **Method**: `POST`
- **Authentication**: Required (`auth` header)
- **Content-Type**: `multipart/form-data`
- **Request Parameters**:
  - Form Fields:
    - `directory` (string, optional, default: `/`)
  - Files:
    - `filepath` (file binary, required)
- **Responses**:
  - **Success (`200 OK`)**:
    ```json
    {
      "return": "File Saved in the server"
    }
    ```
  - **Failure (`400 Bad Request`)**:
    ```json
    {
      "return": "No file provided"
    }
    ```
    *or*
    ```json
    {
      "return": "No space left \n Try Clearning Trash"
    }
    ```
  - **Failure (`401 Unauthorized/Error`)**:
    ```json
    {
      "return": "Some Error in Creating the Directory"
    }
    ```
    *or*
    ```json
    {
      "return": "Too Many files already exist try a diffrentname"
    }
    ```

---

### 9. Folder Upload
*Upload multiple files preserving folder structure.*

- **Endpoint**: `/uploadfolder/<int:Userid>/`
- **Method**: `POST`
- **Authentication**: Required (`auth` header)
- **Content-Type**: `multipart/form-data`
- **Request Parameters**:
  - Form Fields:
    - `directory` (string, required)
  - Files:
    - `files` (array of file binaries, required)
- **Responses**:
  - **Success (`200 OK`)**:
    ```json
    {
      "return": "Folder upload done"
    }
    ```
  - **Failure (`400 Bad Request`)**:
    ```json
    {
      "return": "No folder uploaded"
    }
    ```
    *or*
    ```json
    {
      "return": "No folder path mentioned"
    }
    ```
  - **Failure (`401 Error`)**:
    ```json
    {
      "return": "Error details message"
    }
    ```

---

### 10. File/Folder Download
*Download a file or a folder (compressed as a zip).*

- **Endpoint**: `/download/<int:userid>/`
- **Method**: `GET`
- **Authentication**: Required (`auth` header)
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "filename": "path/to/file_or_folder"
  }
  ```
- **Responses**:
  - **Success (`200 OK`)**: File binary stream / zip archive.
    - Files return headers: `filesize` and `filetype`.
    - Folders return header: `Content-Disposition: attachment; filename=...zip`.
  - **Failure (`400 Bad Request`)**:
    ```json
    {
      "retutn": "WrongFile Inputed Tryagain"
    }
    ```

---

### 11. Share File or Folder (Generate Public Link)
*Generate a shareable public access link for a file or folder.*

- **Endpoint**: `/access/<int:userid>/`
- **Method**: `POST`
- **Authentication**: Required (`auth` header)
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "filepath": "path/to/file_or_folder",
    "time": 604800
  }
  ```
  > [!NOTE]
  > `time` is optional and specifies expiration duration in seconds. Defaults to `604800` (1 week).
- **Responses**:
  - **Success (`200 OK`)**:
    ```json
    {
      "return": "http://yourserver.com/share/userid/encodedpath/expiry/token"
    }
    ```
  - **Failure (`400 Bad Request`)**:
    ```json
    {
      "return": "no filepath sent"
    }
    ```

---

### 12. Folder Structure
*Get the JSON structure of user directories.*

- **Endpoint**: 
  - `/structure/<int:userid>/`
  - `/structure/<int:userid>/<int:folder>`
- **Method**: `GET`
- **Authentication**: Required (`auth` header)
- **Responses**:
  - **Success (`200 OK`)**:
    ```json
    {
      "folder_structure_details": "..."
    }
    ```
  - **Failure (`400 Bad Request`)**:
    ```json
    {
      "return": "No folders left ",
      "instruction": "create a file before gettig the structure"
    }
    ```
    *or*
    ```json
    {
      "return": "fileopeningerror",
      "instruction": "tryagain"
    }
    ```

---

### 13. Get Total Number of Folders
*Get the number of folders for a user.*

- **Endpoint**: `/folders/<int:userid>/`
- **Method**: `GET`
- **Authentication**: Required (`auth` header)
- **Responses**:
  - **Success (`200 OK`)**:
    ```json
    {
      "return": 5
    }
    ```
  - **Failure (`400 Bad Request`)**:
    ```json
    {
      "return": "No folders left ",
      "instruction": "create a file before gettig the structure"
    }
    ```

---

### 14. File/Folder Delete
*Delete a file/folder or move it to trash.*

- **Endpoint**: `/deletefile/<int:userid>/`
- **Method**: `DELETE`
- **Authentication**: Required (`auth` header)
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "filepath": "path/to/file_or_folder",
    "trash": 1,
    "replace": 0
  }
  ```
  > [!NOTE]
  > - `trash` is optional (default: `1`). Setting to `1` moves to trash, while `0` deletes it permanently.
  > - `replace` is optional (default: `0`). Set to `1` to overwrite a file in trash if it already exists.
- **Responses**:
  - **Success (`200 OK`)**:
    ```json
    {
      "return": "Moved to trash"
    }
    ```
    *or*
    ```json
    {
      "return": "Moved succesfully"
    }
    ```
  - **Failure (`400 Bad Request`)**:
    ```json
    {
      "return": "Filenotfound"
    }
    ```
    *or*
    ```json
    {
      "return": "similar files already exist"
    }
    ```

---

### 15. Delete From Trash
*Permanently delete a file or folder from the trash directory.*

- **Endpoint**: `/trash/<int:userid>/`
- **Method**: `DELETE`
- **Authentication**: Required (`auth` header)
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "filepath": "path/to/file_in_trash"
  }
  ```
- **Responses**:
  - **Success (`200 OK`)**:
    ```json
    {
      "return": "removedsuccesully from trash"
    }
    ```
    > [!NOTE]
    > Note the typo in the success response string `removedsuccesully`.
  - **Failure (`200 OK`)**:
    ```json
    {
      "return": "Some error is removing the trash"
    }
    ```

---

### 16. File/Folder Rename
*Rename an existing file or directory.*

- **Endpoint**: `/updatefile/<int:userid>/`
- **Method**: `PUT`
- **Authentication**: Required (`auth` header)
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "filename": "path/to/old_name",
    "newname": "path/to/new_name"
  }
  ```
- **Responses**:
  - **Success (`200 OK`)**:
    ```json
    {
      "return": "file renamed"
    }
    ```
  - **Failure (`400 Bad Request`)**:
    ```json
    {
      "return": "Filenotfound"
    }
    ```
    *or*
    ```json
    {
      "return": "filedonotexist"
    }
    ```
    *or*
    ```json
    {
      "return": "permissiondenied"
    }
    ```

---

### 17. Create Folder
*Create an empty folder.*

- **Endpoint**: `/createfolder/<int:userid>/`
- **Method**: `PUT`
- **Authentication**: Required (`auth` header)
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "filename": "path/to/new_folder"
  }
  ```
- **Responses**:
  - **Success (`200 OK`)**:
    ```json
    {
      "return": "file renamed"
    }
    ```
    > [!NOTE]
    > Although this endpoint creates a folder, the backend returns `"file renamed"` upon success.
  - **Failure (`400 Bad Request`)**:
    ```json
    {
      "return": "permissiondenied"
    }
    ```

---

### 18. Change File Location (Move File/Folder)
*Move a file or folder to a new destination.*

- **Endpoint**: `/changefilelocation/<int:userid>/`
- **Method**: `PUT`
- **Authentication**: Required (`auth` header)
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "oldpath": "path/to/current_location",
    "newlocation": "path/to/new_location"
  }
  ```
  > [!IMPORTANT]
  > Ensure the payload key is `newlocation` (not `newpath` as indicated in older documents).
- **Responses**:
  - **Success (`200 OK`)**:
    ```json
    {
      "return": "file postion changed"
    }
    ```
    > [!NOTE]
    > Note the typo in the success response string `postion`.
  - **Failure (`400 Bad Request`)**:
    ```json
    {
      "return": "Filenotfound"
    }
    ```
    *or*
    ```json
    {
      "return": "filedonotexist"
    }
    ```

---

### 19. File Search
*Search for files by name.*

- **Endpoint**: `/searchfile/<int:userid>/<string:filename>/`
- **Method**: `GET`
- **Authentication**: Required (`auth` header)
- **Responses**:
  - **Success (`200 OK`)**:
    ```json
    {
      "return": "File Found",
      "path": ["/path/to/matched/file1", "/path/to/matched/file2"]
    }
    ```
  - **Failure (`400 Bad Request`)**:
    ```json
    {
      "return": "File Not Found"
    }
    ```

---

### 20. Get User Space Usage
*Get stats regarding user storage space utilization.*

- **Endpoint**: `/userstats/<int:userid>/`
- **Method**: `GET`
- **Authentication**: Required (`auth` header)
- **Responses**:
  - **Success (`200 OK`)**:
    ```json
    {
      "return": {
        "usedspace": 1048576,
        "remaningspace": 524288000,
        "update": 0
      }
    }
    ```
  - **Failure (`400 Bad Request`)**:
    ```json
    {
      "return": "The user do not exist"
    }
    ```

---

### 21. Update Account Details
*Modify account details (e.g. username, password, or email).*

- **Endpoint**: `/updateacc/`
- **Method**: `PUT` (also accepts `POST`)
- **Authentication**: Required (`auth` header)
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "username": "updated_user",
    "password": "updated_password",
    "email": "updated_email@example.com"
  }
  ```
- **Responses**:
  - **Success (`200 OK`)**:
    ```json
    {
      "return": "Account updated successfully"
    }
    ```
  - **Failure (`401 Unauthorized`)**:
    ```json
    {
      "return": "Error message details"
    }
    ```

---

### 22. Delete Account
*Permanently delete user account.*

- **Endpoint**: `/deleteacc/`
- **Method**: `DELETE`
- **Authentication**: Required (`auth` header)
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "username": "example_user",
    "password": "secure_password",
    "email": "user@example.com"
  }
  ```
- **Responses**:
  - **Success (`200 OK`)**:
    ```json
    {
      "return": "Account deleted successfully"
    }
    ```
  - **Failure (`401 Unauthorized`)**:
    ```json
    {
      "return": "Invalid credentials or delete failed"
    }
    ```

---

### 23. Recover File/Folder from Trash
*Recover a file or folder from the trash directory back to its original location.*

- **Endpoint**: `/recovertrash/<int:userid>/`
- **Method**: `PUT`
- **Authentication**: Required (`auth` header)
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "trashpath": "path/to/file_in_trash"
  }
  ```
  > [!NOTE]
  > The `trashpath` value can be the relative path of the item inside the trash (either including or excluding the `trash/` prefix, and using either `/` or `\\` as separators). For example, both `"Fileees"` and `"trash/Fileees"` are accepted.
- **Responses**:
  - **Success (`200 OK`)**:
    ```json
    {
      "return": "File transfred"
    }
    ```
    > [!NOTE]
    > Note the typo in the success response string `transfred`.
  - **Failure (`400 Bad Request`)**:
    ```json
    {
      "return": "Missing or invalid JSON payload."
    }
    ```
    *or*
    ```json
    {
      "return": "Error recovering  the files"
    }
    ```
    > [!NOTE]
    > Note the double space in the error response string `recovering  the`.

---

### 24. Get Trash Data
*Retrieve the list of all items currently in the trash directory, along with metadata.*

- **Endpoint**: `/trashdata/<int:userid>/`
- **Method**: `GET`
- **Authentication**: Required (`auth` header)
- **Content-Type**: `application/json`
- **Responses**:
  - **Success (`200 OK`)**:
    ```json
    [
      {
        "name": "filename.txt",
        "path": "trash/filename.txt",
        "type": "file",
        "originalPath": "folder/filename.txt",
        "size": 1234,
        "modified": 1783626681
      }
    ]
    ```

