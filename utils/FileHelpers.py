from .Storage import get_storage

Fileoperation=get_storage()

def CreateDir(Userid,Directory,Filename):
    try:
        DIR=Fileoperation.source
        Userid=str(Userid)
        if Directory is None:
            DIR=Fileoperation.joinpath(DIR,Userid)
        else:
            DIR=Fileoperation.joinpath(DIR,[Userid,Directory])
        Fileoperation.Createfolder(DIR)
        Filename=Fileoperation.getfilename(Filename)
        return str(Fileoperation.joinpath(DIR,Filename)) #Returnt the paths where the file is supposed to store
    
            

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
    