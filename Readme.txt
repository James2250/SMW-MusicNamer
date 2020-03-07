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

- Add Song1.txt to the end of Addmusic_list.txt in the AddmusicK folder.  
  Is what ConvertMusic renames each of the song text files to when going through the zip folders.
  
- Needs to have an expanded ROM called ROMo.smc in the same directory (save a level in lunar magic or use lunar expand)  
  Not provided here.  

- Doesn't handle songs with sample groups, but handles all other samples.  Copies any samples found to the AddMusicK samples
  folder and then deletes them after use.  
  
- Does not support any of the __MACOSX songs.  


AddMusicK
https://www.smwcentral.net/?p=section&a=details&id=17546