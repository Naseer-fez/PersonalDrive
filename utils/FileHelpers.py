import os 
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

def CreateDir(Userid,Directory,Filename):
    try:
        DIR=Path(os.getenv("DestinationFolder"))   #FEZ
        # DIR=Path(r"D:\CODE\PYTHON\CODE\Projects\Personaldrive\test")
        #Check if Userid exists
        Userid=str(Userid)    
        if Directory is None:
            DIR=os.path.join(DIR,Userid)
        else:
            DIR=os.path.join(DIR,Userid,Directory)
        # print(DIR)
        Path(DIR).mkdir(parents=True, exist_ok=True) #Dir is created 
        Filename=Path(Filename).name
        # print(Filename)
        return Path(os.path.join(DIR,Filename))
    except Exception as e:
        return 0

    
if __name__=="__main__":
    print(CreateDir(Directory=None,Filename=r"Live.mp4",Userid="1"))
    import shutil
#     shutil.rmtree(
#     os.path.join(
#         r"D:\CODE\PYTHON\CODE\Projects\Personaldrive\test",
#         "1",
#         "1"
#     )
# )
    