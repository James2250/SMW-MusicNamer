import shutil
import time
import os.path
import sys

from zipfile import ZipFile 

SampleFolderName = ""
TxtFileWorkingOn = ""
ZipFileName = ""

ListOfTxtFilePaths = []  #text files per zip folder
ListOfTxtFileNames = []

ListOfBrrFiles = []
ListOfCopiedBrrFiles = []
ListOfCopiedBrrFolders = [] 
ListOfCopiedBrrNames = []

#Taken from AddMusicK
def SNESToPC(addr):			
	if addr < 0 or addr > 0xFFFFFF or (addr & 0xFE0000) == 0x7E0000 or (addr & 0x408000) == 0x000000:		
		return -1
		
	addr = ((addr & 0x7F0000) >> 1 | (addr & 0x7FFF))
	return addr

def ReadROMData(File, OutputFile):	
    address = SNESToPC(0x0E8000) #addmusic @amk
    address = address + 512  #200 hex header
    
    File.seek(address, 0)  #@amk 
    amkTest = File.read(4)
    
    if amkTest[0] == 64:  # @ symbol
        File.read(4) # skip forward to music pointer
        
    ##---------------------------------##
        data = File.read(1).hex()
        data2 = File.read(1).hex()
        data3 = File.read(1).hex()
        
        addr = data3 + data2 + data  #main music pointer
        addr = "0x" + addr

        IntAddr = int(addr, 0)
        
        IntAddr = SNESToPC(IntAddr) 
        IntAddr = IntAddr + 512  #header
        
        File.seek(IntAddr, 0) 
        File.read(30)   #specific song pointer we want is 30 bytes ahead, 00 00 00 00 before then
        
    ##---------------------------------##
        data4 = File.read(1).hex()
        data5 = File.read(1).hex()
        data6 = File.read(1).hex()
        
        NewAddr = data6 + data5 + data4  #main music pointer
        NewAddr = "0x" + NewAddr
        
        IntAddr2 = int(NewAddr, 0)
        
        IntAddr2 = SNESToPC(IntAddr2) 
        IntAddr2 = IntAddr2 + 512  #header
   
        IntAddr2 -= 4  #go back to size after STAR
        File.seek(IntAddr2, 0) 
        
        size1 = int("0x" + File.read(1).hex(), 0)    #STAR size 1  
        size2 = int("0x" + File.read(1).hex(), 0)    #STAR size 2 

        File.read(2)  #ignore inverse size
        
        TotalSize = size1 | size2 << 8
        FinalData = (File.read(TotalSize).hex())
        
        OutputFile.write(ZipFileName + " -- " + TxtFileWorkingOn + " : " + FinalData + "\n")
        
        File.close()
        
        os.remove("ROM.smc")	
        os.remove("ROM.msc")
        os.remove("ROM.smc~")
        
    else:
        OutputFile.write(ZipFileName + " -- " + TxtFileWorkingOn + " FAILED TO PATCH \n" )

def ExtractSongFromZip(path, OutputFile):
	global SampleFolderName
	global TxtFileWorkingOn
	
	brrFolderNames = set()
	
	for (dirpath, dirnames, filenames) in os.walk(path):
		if "__MACOSX" in dirnames:
			dirnames.remove("__MACOSX")
			
		if "SPCs" in dirnames:
			dirnames.remove("SPCs")
			
		for filename in filenames:
			if filename.endswith(".brr"):  # we are in samples folder
				ListOfBrrFiles.append(dirpath + "/" + filename)
				ListOfCopiedBrrNames.append(filename)
				
				#if not SeenBrrFile:
				if os.path.basename(dirpath) not in brrFolderNames:
					SeenBrrFile = True 
					NewFolder = "./samples/" + os.path.basename(dirpath)
					shutil.copytree(dirpath, NewFolder)
					
					ListOfCopiedBrrFolders.append(NewFolder)
					brrFolderNames.add(os.path.basename(dirpath))
					
					SampleFolderName = NewFolder
				
			if filename.endswith('.txt'): 
				if "readme" in filename.lower(): #ignore  
					continue
				
				elif "patterns" in filename.lower(): #ignore 
					continue
					
				else:  # .txt file song
					ListOfTxtFilePaths.append(dirpath + "/" + filename)
					ListOfTxtFileNames.append(filename)  
					
	count = 0
	brr_count = 0
	
	for File in ListOfBrrFiles:	
		shutil.copy(File, "./samples")
		ListOfCopiedBrrFiles.append("./samples/" + ListOfCopiedBrrNames[brr_count])
		
		brr_count +=1 
		
	for File in ListOfTxtFilePaths:	
		TxtFileWorkingOn = ListOfTxtFileNames[count]
		shutil.copy(File,  "./music")
		
		OldName = "./music/" + ListOfTxtFileNames[count]
		NewName = "./music/Song1.txt"
		
		if os.path.isfile(NewName):
			os.remove(NewName)
			
		os.rename(OldName, NewName)
		
		shutil.copy("ROMo.smc",  "ROM.smc")
		
		#-noblock needed so cmd doesn't wait for pressing enter
		os.system('cmd /c "AddmusicK ROM.smc" -noblock')
		
		File = open("ROM.smc", "rb")
		ReadROMData(File, OutputFile)
		
		count += 1 

def main():
    OutputFile = open('OutputFile.txt', 'a', encoding='utf-8')
    global ZipFileName

    for filename in os.listdir("./SONGS"):
        os.mkdir("./SONGS/TEMP")
        
        ListOfTxtFileNames.clear()  
        ListOfTxtFilePaths.clear()  

        ListOfBrrFiles.clear()
        ListOfCopiedBrrNames.clear()
        ListOfCopiedBrrFiles.clear()
        ListOfCopiedBrrFolders.clear()
        
        if filename.endswith(".zip"): 
            ZipFileName = filename
            
            with ZipFile("./SONGS/" + filename, 'r') as zipObj:
                try:
                    zipObj.extractall('./SONGS/TEMP')
                    ExtractSongFromZip("./SONGS/TEMP", OutputFile)
                    
                except OSError as e:
                    OutputFile.write(filename + " FAILED TO OPEN\n")  
            
        for File in ListOfCopiedBrrFiles:	
            if os.path.isfile(File):
               if File != "./samples/EMPTY.brr":  #don't remove default sample
                 os.remove(File)
            
        for Folder in ListOfCopiedBrrFolders:	
            if os.path.isdir(Folder):
                shutil.rmtree(Folder) 
                
        shutil.rmtree("./SONGS/TEMP")  #can't use os.rmdir, needs empty folder
        
    OutputFile.close()
        

if __name__== "__main__":
	main()
	