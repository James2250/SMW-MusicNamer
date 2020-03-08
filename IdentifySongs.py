#Bad code is bad, but it technically works!  

SongDatabase = []  # Dasebase Song Data 
SongsInROM = []    # ROM Song Data
ListOfNameMatches = []  #contains lists of database names the songs in the ROM matched
DatabaseDic = {}  #Database Song Names -> Song Data

SongIDsInLevels = set() #Song IDs
StageMusicDic = {} #hex stage number -> song ID from level table 

#Taken from AddMusicK
def SNESToPC(addr):			
	if addr < 0 or addr > 0xFFFFFF or (addr & 0xFE0000) == 0x7E0000 or (addr & 0x408000) == 0x000000:		
		return -1
		
	addr = ((addr & 0x7F0000) >> 1 | (addr & 0x7FFF))
	return addr

#AddMusicK format - Stores table of music pointers.  Table found by 24 bit pointer at 0x0E8007 after @amk text.  
#FF FF FF ends the table.  
def Handle_AddMusicK(File):
	address = SNESToPC(0x0E8000) #addmusic @amk location
	address = address + 512  #200 hex header
	
	File.seek(address, 0)  #@amk 
	amkTest = File.read(4)

	if amkTest[0] == 64:  # @ symbol
		print("AddMusicK")
		
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
		FilePosition = File.tell()
		
		data4 = "AA" 
		data5 = "AA"
		data6 = "AA"

		SongNum = 0
		
		#should be a length check instead, oh well 
		while data4 != "ff" or data5 != "ff" or data6 != "ff":   #FF FF FF means end of song pointer data	
			File.seek(FilePosition + (SongNum * 3))
			
			data4 = File.read(1).hex()
			data5 = File.read(1).hex()
			data6 = File.read(1).hex()
		
			NewAddr = data6 + data5 + data4  #main music pointer
			NewAddr = "0x" + NewAddr
			
			IntAddr2 = int(NewAddr, 0)
			
			if IntAddr2 == 0xFFFFFF:  #end of table
				break 
				
			IntAddr2 = SNESToPC(IntAddr2) 
			IntAddr2 = IntAddr2 + 512  #header
			
			IntAddr2 -= 4  #go back to size after STAR
			
			try:
				File.seek(IntAddr2, 0) 
				
				size1 = int("0x" + File.read(1).hex(), 0)    #STAR size 1  
				size2 = int("0x" + File.read(1).hex(), 0)    #STAR size 2 

				File.read(2)  #ignore inverse size
				
				TotalSize = size1 | size2 << 8
				FinalData = (File.read(TotalSize).hex())
				
				SongsInROM.append(FinalData)
				SongNum += 1 
				
			except: 
				print("Error going to song address, ending early")
			
	else:
		print("Not MusicK")
		
	print("Test")
	
def Handle_AddMusicM(File):
	address = SNESToPC(0x8FB464) #addmusicM 70 77 07 00  
	address = address + 512  #200 hex header
	
	#Would need more testing but has most of the info here
	#Stores music table at 0x8FE000, Has same Song ID placement as AddMusicK but 69 69 before each ID instead of 40 60?
	'''
	File.seek(address, 0) 
	amTest = File.read(4)

	
	if hex(amTest[0]) == "0x70" and hex(amTest[1]) == "0x77":
		print("AddMusicM")
		
		MusicTablePointers = SNESToPC(0x8FE000) 
		MusicTablePointers = MusicTablePointers + 512  #200 hex header
	
		File.seek(MusicTablePointers, 0)

		data4 = "AA" 
		data5 = "AA"
		data6 = "AA"

		SongNum = 0
		FilePosition = File.tell()
		
		while SongNum < 255:   #original AddMusicM loops between 0 and FF
			File.seek(FilePosition + (SongNum * 3))
			
			data4 = File.read(1).hex()
			data5 = File.read(1).hex()
			data6 = File.read(1).hex()
		
			NewAddr = data4 + data5 + data6  #different endian than AddMusicK
			#print(str(NewAddr) + " " +  str(SongNum))   1ebf19 67 = Earthbound song
			
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
				
			SongsInROM.append(FinalData)
			SongNum += 1 
	'''

#Super Mario All stars custom patch.  Means wont have AddMusicK
#https://www.smwcentral.net/?p=section&a=details&id=4175
def Handle_SMAS(File):
	SMAS_Address = SNESToPC(0x00D0DE)  #random check for SMAS data
	SMAS_Address = SMAS_Address + 512  #200 hex header
		
	File.seek(SMAS_Address, 0)  
	SMAS_Data = File.read(1).hex()
		
	if SMAS_Data == "0a":
		print("Using Super Mario All stars custom music patch")

def Handle_OverworldSongs(File):
	address = SNESToPC(0x04DBC8) #04DBC8 = Music tracks used by the different submaps, indexed by submap ID ($1F11).
	address = address + 512  #200 hex header
	
	File.seek(address, 0)  
	Index = 0
	
	while Index < 7:   #7 submaps 
		Data = File.read(1).hex()
		SongID = int("0x" + Data, 0)  
					
		#(Overworld convert doesn't -1)
		NewSongID = SongID 
		NewSongID = NewSongID & 0x00FF 
		NewSongID = NewSongID << 1
		NewSongID += SongID         #convert to the correct index for AddMusicK music table
					
		NewSongID -= 30   #we remove the 30 00s in AddMusicK table
		NewSongID /= 3    #SongsInROM indexed per song (aka per 3 bytes)
			
		SongIDsInLevels.add(int(NewSongID))
		StageMusicDic[Index + 900] = int(NewSongID)		 #Add 900 to show isn't a level number
				
		Index += 1 
	
def ReadROMData(File):	
	print("Reading ROM Data")
	
	Handle_AddMusicK(File)
	Handle_AddMusicM(File)
	Handle_SMAS(File)
	

#Applies to AddMusicK 
#Music IDs for stages stored in standard object list mentioned at https://smwspeedruns.com/Level_Data_Format#Pointer_Tables
#Uses the "LM - Music bypass" with 40 60 before each song ID.   
def ScanLevelDataForID(File, Index):
	data = "AA"
	data2 = "AA"
	data3 = "AA"
	
	while True:
		data = File.read(1).hex()
		
		if data == "40":
			data2 = File.read(1).hex()
			
			if data2 == "60":
				data3 = File.read(1).hex()  #40 60 before song ID

				SongID = int("0x" + data3, 0)  
					
				SongID -= 1 
				NewSongID = SongID 
				NewSongID = NewSongID & 0x00FF 
				NewSongID = NewSongID << 1
				NewSongID += SongID         #convert to the correct index for AddMusicK music table
					
				NewSongID -= 30   #we remove the 30 00s in AddMusicK table
				NewSongID /= 3    #SongsInROM indexed per song (aka per 3 bytes)
			
				SongIDsInLevels.add(int(NewSongID))
				StageMusicDic[Index] = int(NewSongID)  #Index = level number
				
				break
		
		if data == "53":
			data2 = File.read(1).hex()
			
			if data2 == "54":
				data3 = File.read(1).hex()   #STAR
				
				if data2 == "41":
						break
	
#Reading from Layer 1 pointers at 0x05E000.  https://smwspeedruns.com/Level_Data_Format#Pointer_Tables
def GetSongIDs(File):
	LevelDataAddress = 0x05E000 #goes to 05E600   	       
	
	Index = 0x0
	LevelAddresses = set()
	
	while Index < 512:  #0x600 /3 bytes = 1536 / 3 bytes = 512
		address = SNESToPC(LevelDataAddress)
		address = address + 512  #200 hex header
	
		File.seek(address + (Index * 3), 0) 
		
		data = File.read(1).hex()
		data2 = File.read(1).hex()
		data3 = File.read(1).hex()

		addr = data3 + data2 + data  
		
		if addr in LevelAddresses:  #seen before, means is a not used level 
			Index += 1
			continue
			
		LevelAddresses.add(addr)
		
		addr = "0x" + addr
		IntAddr = int(addr, 0)
		
		IntAddr = SNESToPC(IntAddr) 
		IntAddr = IntAddr + 512  #header
		
		File.seek(IntAddr, 0) 
		ScanLevelDataForID(File, Index)	
				
		Index += 1 
		
		
#Songs from Feb 22nd 2020 - July 28 2011
def ReadSongDatabase():
	File = open("SMW_Songs.txt", "r")
	content = File.readlines()
	
	for line in content:
		if ':' in line:
			Name =  line.split(':')[0]
			Notes = line.split(':')[1]
	
			SongDatabase.append(Notes) 
			DatabaseDic[Notes] = Name

MatchingSongLengths = []
ListsOfMatchingSongLengths = []

def MatchSong(StartIndex, EndIndex):		
	ListofSegmentMatches = []

	for i, list in enumerate(ListsOfMatchingSongLengths):
		for SongNum, ROMSong, DatabaseSong in list: 
			CheckPart = ROMSong[(StartIndex):(EndIndex)]  
			CheckPart2 = DatabaseSong[(StartIndex+1):(EndIndex+1)]    #+1 because space at the front of database + \n at the end of database song
			
			if CheckPart == CheckPart2:    
				ListofSegmentMatches.append((DatabaseDic[DatabaseSong], SongNum))  #list of songs in database that match this song
			
	ListOfNameMatches.append(ListofSegmentMatches)


def MatchSongLengths():
	ListOfNames = []
	
	for i, ROMSong in enumerate(SongsInROM):
		Length = len(ROMSong)

		for SongData in SongDatabase: 
			Length2 = len(SongData)
			
			if Length == (Length2 - 2):   #-2 because space at the front of database + \n at the end of database song
				MatchingSongLengths.append((i, ROMSong, SongData))  #song place in AddMusicK table, ROM song, database song name)
				
	ListsOfMatchingSongLengths.append(MatchingSongLengths)
		
def MatchSongSegments():
	for i in range(11):   #bytes to check, start of song normally different to database
		StartIndex = 70
		MatchSong(StartIndex + (i * 10), StartIndex + (i * 10) + 10)

def FilterResults(DatabaseNameList, ROMSongNums):
	for NameList in	ListOfNameMatches:
		for Name, i in NameList:  # for each song in the ROM, Name = Database song
			if Name not in DatabaseNameList.keys():  
				DatabaseNameList[Name] = 0
				ROMSongNums[Name] = (i)  #i = song place in AddMusicK table
				
			else:
				DatabaseNameList[Name] += 1 
				
def PrintResults(DatabaseNameList, ROMSongNums):
	OutputString = ""
	
	for key, value in DatabaseNameList.items():
		if value > 1:  #if Match Song found at least twice
			OutputString = OutputString + ("Song in Game " + str(ROMSongNums[key]) + " : " + key) + "\n"  #<--  key is song name

	#Remove if statement below to get Stage XX has song YY for every stage
	
	for StageNum, SongID in StageMusicDic.items():      #Song ID in StageMusicDic =  ID from level table
		if SongID in ROMSongNums.values():				#ROMSongNums.values only has IDs from songs matched with a name
			if StageNum > 900:  #check for overworld
				OutputString = OutputString + ("Submap " + hex(StageNum - 900) + " has song " + str(SongID)) + "\n"

			else:
				OutputString = OutputString + ("Stage " + hex(StageNum) + " has song " + str(SongID)) + "\n"
			
	return OutputString
		
def main():
	print("ROM Filename: ")
	ROM_Name = input()
		
	try:
		ReadSongDatabase()
	
		File = open(ROM_Name, "rb")
		OutputString = ""
		
		ReadROMData(File)
		MatchSongLengths()  #Might as well match against song length before doing more specific searching
		MatchSongSegments()
		
		DatabaseNameList = {}    #SongName in database -> number of matches in MatchSong
		ROMSongNums = {}      #SongName in ROM -> song place in AddMusicK table
	
		Handle_OverworldSongs(File)	
		GetSongIDs(File)

		FilterResults(DatabaseNameList, ROMSongNums)
		OutputString = PrintResults(DatabaseNameList, ROMSongNums)
		
		File.close()
				
		OutputFile = open("Output.txt", 'w')
		OutputFile.write(OutputString)
		OutputFile.close()
		
		print("Program finished, data put in Output.txt")
		input()
		
	except:
		print("File not found")
		input()
		
	
if __name__== "__main__":
	main()
	