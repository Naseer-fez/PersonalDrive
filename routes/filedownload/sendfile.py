from pathlib import Path
import os 
from dotenv import load_dotenv



def Filedowload(filepath):
        SIZE=int(os.getenv("size")) or 5
        with open (file=filepath,mode="rb") as output:
            while True:
              chunk=output.read(1024*1024*SIZE)
              print(1024*1024*SIZE)
              if not chunk:
                  break
              yield chunk  


def filedetails(userid,filepath):
    Source=os.getenv("DestinationFolder") or r"D:/CODE/PYTHON/CODE/Projects/Personaldrive/test"
    filepath=Path(os.path.join(Source,userid,filepath))
    if not os.path.exists(filepath):
        return [None]
    Filesize=os.path.getsize(filepath)
    Fileextenstion=os.path.splitext(filepath)[1]
    return [filepath,Filesize,Fileextenstion]
    
    
    
    
    
    
if __name__=="__main__":
    filepath=r"D:\CODE\PYTHON\CODE\Projects\Personaldrive\test\1\Live.mp4"
    print(Filedowload(filepath))
