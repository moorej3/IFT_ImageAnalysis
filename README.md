# IFT_ImageAnalysis

This project is for analyzing kymographs of Chlamydomonas flagella. 

Procedure:
  1. Generate kymograph of IFT motion using ImageJ. This program is designed to look for outputs from KymoClear. 
      so you will need to edit the control module to look for files from other programs.
  2. Put the IFTControlModule and IftAnalysis files in the folder containing your data. The program will search
      recursively for files, so it is alright if the files are within their own folders.
  3. Run the IFTControlModule
  4. Raw Data will be output in a folder called results. This folder will include an image of the tracks analyzed, 
      as well as a graphical representation of how velocities were calculated. There will also be data on each 
      individual track in the Results1.csv document, and overall results in the Summary1.csv document. Lastly,
      the data of all images in the program directory is compiled in a document one directory above Results in 
      a document called Data.csv
