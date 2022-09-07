import zipfile     #for zip file
import pyunpack    #for .rar file
import os          #for creating the new directory
def zip_rar_extraction(file_name, output_folder):                 #two types of positional arguments
    if file_name.endswith('.zip'):                                #this works for .zip file
        with zipfile.ZipFile(file_name,"r") as zip_ref:           #Read the filename.zip
            zip_ref.extractall(output_folder)                     # Extract the file in your destination folder
    else:                                                         #If extension ends with .rar then here it works    
        os.mkdir(output_folder)                                   #Create your destination folder
        pyunpack.Archive(file_name).extractall(output_folder)     #read your .rar file and extract into your destination folder
file_name = input("file_name with directory :")                   #provide your filename with directory and extension must be .zip or .rar
output_folder = input("Extracted Folder Name :")                  #Your destination folder name
zip_rar_extraction(file_name, output_folder)                      #Calling your defind function