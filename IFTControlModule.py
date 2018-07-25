from os import walk
import IftAnalysis


def listfiles(directory, extension):
    filelist = []
    for(dirpath, dirnames, filenames) in walk(directory):
        for f in filenames:
             if f.endswith(extension):
                 #print(dirpath+"/"+ f)
                 filelist.append(dirpath+"/" + f)
    return(filelist)

a = listfiles("./", "filtered_forward.tif")


for file in a:
    file2 = file.rsplit("/",1)
    file2 = file2[0] + "/" + file2[1].replace(" filtered_forward","").replace("_","")
    #print(file2)
    print("\n \n Analyzing " + file + "\n")
    filename = file.split("./")[1].split("/")[0]
    IftAnalysis.IFTTraj(file, file2, filename)
