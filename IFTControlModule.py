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

#print(a)

for file in a:
    print("\n \n Analyzing " + file + "\n")
    filename = file.split("./")[1].split("/")[0]
    IftAnalysis.IFTTraj(file, filename)
