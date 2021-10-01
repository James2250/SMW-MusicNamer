Using Python 3 

--- IdentifySongs.py --- 

Just need to run and give it "ROMName".smc.  Will create an output file with all of the known songs for levels/submaps as 
long as the ROM used AddMusicK.  Can use Lunar Magic to find the level numbers.  

- Needs the SMW_Songs.txt database file in the same directory.  




--- ConvertMusic.py --- 

Doesn't need to be used unless you are trying to add more custom songs into the database.  

Helped create the SMW_Songs database. Will take a folder of custom songs in zip format from 
https://www.smwcentral.net/?p=section&s=smwmusic and output 1 file of all of the songs in SMW format (OutputFile.txt).   

- Needs a folder called SONGS with all of the zips in it to be converted.   

- Needs to be in the same folder as AddmusicK.exe.  

- Delete all songs under Locals/Globals and add "0A Song1.txt" to the Locals section in Addmusic_list.txt in the AddmusicK folder.  
  
- Needs to have an expanded US ROM (at least 1MB) called ROMo.smc in the same directory (save a level in lunar magic or use lunar expand)  
  Not provided here.  

- Doesn't handle songs with sample groups, but handles all other samples.  Copies any samples found to the AddMusicK samples
  folder and then deletes them after use.  
  
- Does not support any of the __MACOSX songs.  


AddMusicK 1.0.8 
https://www.smwcentral.net/?p=section&a=details&id=17546