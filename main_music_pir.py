from music import *
from pixels import Pixels
import time
import _thread
from subprocess import call
import RPi.GPIO as GPIO

#Current state of motion detect
# 0: No motion detected
# 1: Motion detected and remain in frame
state = 0

stop_threads = False
#Setup player to play music
Instance = vlc.Instance()
player = Instance.media_player_new()

#RGB LED
pixels = Pixels() #To control the RGB LED

BUTTON_PIN = 17 #Power off button on top of ReSpeaker Hat
PIR_PIN = 12 #PIR Sensor Pin connection on ReSpeaker Hat
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN)
GPIO.setup(PIR_PIN, GPIO.IN)

#Function for blinking LED
def ledBlink():
    global pixels
    pixels.wakeup()
    pixels.think()
    time.sleep(8)
    pixels.off()

#Thread for running music in the background
def musicThread():
    global stop_threads
    global player
    global Instance
    while True:
        playMusic(Instance, player)
        if stop_threads:
            break
    print("Music thread stopped")

#Indicate program startup
pixels.wakeup()
pixels.speak()

_thread.start_new_thread(musicThread, ()) #Start music playlist
print("Initializing music player")
while(player.get_state()!=vlc.State.Playing):
    None #Wait for player to be initialized
time.sleep(2)
player.pause()
print("Music paused")
pixels.off()

previous_time = time.perf_counter() #Initialize music timer
while True:   
    #Power off button pressed
    if GPIO.input(BUTTON_PIN) == 0:
        pixels.wakeup()
        pixels.speak()
        media = vlc.MediaPlayer("sounds/poweroff.mp3")
        media.play()
        time.sleep(3)
        pixels.off()
        stop_threads = True
        break
    
    motion = GPIO.input(PIR_PIN) #Detect motion
    
    state = 0 if motion==0 else state #Update the current motion state
    
    current_time = time.perf_counter() #Update music timer
    duration = current_time - previous_time #Calculate duration of no motion
    
    #Pause music if the time is over
    if duration > 300 and player.get_state()==vlc.State.Playing:
        player.pause()
        print("Music paused")
    
    #Motion detected
    if motion==1 and state==0:
        
        _thread.start_new_thread(ledBlink, ()) #Play with LED
        player.play()
        print("Music continue for 5 minutes")
        previous_time = time.perf_counter() #Update music timer
        
        state = 1 #Update the current motion state

#Shutdown Raspi after poweroff button is pressed
call("sudo poweroff", shell=True)


