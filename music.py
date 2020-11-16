import pafy
import vlc
import time
import json
import random

def playMusic(Instance, player):
    #Read the playlist from json
    with open('playlist.json') as f:
        data = json.load(f)

    musics = data["music"] #Get the playlist as JSON array
    random.shuffle(musics) #Shuffle the music playlist
    length = len(musics)

    #Load and play each music from the playlist
    for m in musics:
        #Extract music data
        name = m["name"]
        url = m["url"]
        
        #Load audio from youtube url
        try:
            video = pafy.new(url)
        except: #Error
            print("Unable to play \""+ name + "\": Incorrect URL or no internet access")
            media = vlc.MediaPlayer("sounds/nomusic.mp3")
            media.play()
            time.sleep(12)
            continue
        
        #Get audio source from YouTube
        source = video.getbestaudio()
        playurl = source.url
        
        #Load music into the player
        Media = Instance.media_new(playurl)
        Media.get_mrl()
        player.set_media(Media)
        player.play()
        
        #Show play data
        print("Playing:",name)
        time.sleep(2)
        duration = player.get_length() / 1000
        print("Duration:", duration)
        
        #Wait until music finished or playlist updated
        playlist_updated = False
        while(player.get_state()!=vlc.State.Stopped and player.get_state()!=vlc.State.Ended):
            #Read playlist.json again
            try:
                with open('playlist.json') as f:
                  data_new = json.load(f)
            except:
                None #Ignore error due to playlist.json being updated
            
            #Check if playlist being updated
            if(len(json.dumps(data)) != len(json.dumps(data_new))):
                print("Playlist updated!")
                playlist_updated = True
                data = data_new
                length = len(musics)
                player.stop()
            
            time.sleep(1) #Reduce strain on CPU
        
        #Refresh music with the new playlist
        if playlist_updated:
            break
        
        print("Ended:", name)
        time.sleep(1)
