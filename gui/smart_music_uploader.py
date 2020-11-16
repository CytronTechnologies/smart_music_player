"""
Smart Music Player with Raspberry Pi | Tutorials of Cytron Technologies
Python version: 3.8.6
Update: 13 November 2020
"""

from tkinter import *
from tkinter import Tk
from tkinter import simpledialog
from tkinter import messagebox
import os
import json

#Constants
HOSTNAME_HINT = "Enter Hostname or IP"

#Initialize variables
index = 0 #Musiclist selection index
data = None #Data for storing music playlist

#Add a music into the list
def addMusic():
    global data
    global musiclist
    
    if data == None:
        messagebox.showwarning(title="Invalid steps", message="You must download the music playlist first.")
        return

    #Get music name and Youtube URL
    name = simpledialog.askstring("Music Name", "Please enter music name:")
    url = simpledialog.askstring("Music URL", "Please enter music URL (youtube):")

    #Cancel button pressed
    if name==None or url==None:
        return

    #Update JSON variable and listbox
    if name!="" and url!="":
        data["music"].append({"name":name,"url":url})
        musiclist.insert(END, str(len(data["music"])) + ". " + name)

#Delete a music list item
def deleteMusic():
    global musiclist
    global data
    global index
    data["music"].pop(index)
    generateList(data)
    index = 0

#Check if destination device is selected
def noDestination():
    if edit_hostname.get() == HOSTNAME_HINT: #Destination device not selected
        messagebox.showwarning(title="Invalid steps", message="You must enter Hostname or IP adress first.")
        return True

#Upload music list to the device
def upload():
    global data

    if noDestination():
        return
    
    elif len(data["music"]) == 0: #Music playlist empty
        messagebox.showwarning(title="Playlist empty", message="You must have at least one music in the playlist.")
        return

    #Create JSON File
    with open('playlist.json', 'w') as outfile:
        json.dump(data, outfile)
    
    #Upload playlist
    command = "scp playlist.json pi@" + edit_hostname.get() + ":~/smart_music_player/playlist.json"
    out = os.system(command)

    if out==0: #Upload success
        messagebox.showinfo(title="Success", message="Playlist updated.")
    else: #Upload failed
        messagebox.showerror(title="Failed to connect", message="Please make sure you have connected\
 to the network and the destination device is on.")

#Listbox item on selected
def onselect(evt):
    global index
    w = evt.widget
    try:
        index = int(w.curselection()[0]) #Get selection index
    except:
        None

#Update listbox showing the list of musics
def generateList(data):
    global musiclist
    musics = data["music"]

    musiclist.delete(0,END) #Clear all items in the list
    for i, m in enumerate(musics): #Add music list from json
        name = m["name"]
        musiclist.insert(END, str(i+1) + ". " + name)

#Destination device selection
def download():
    if noDestination():
        return
    
    global data

    #Download playlist JSON file
    command = "scp pi@" + edit_hostname.get() + ":~/smart_music_player/playlist.json ./playlist.json"
    out = os.system(command)

    if out!=0: #SCP command failed
        messagebox.showerror(title="Failed to connect", message="Please make sure you have connected\
 to the network and the destination device is on.")
        return
        root.focus_force()

    #Load json data
    with open('.\playlist.json') as f:
        data = json.load(f)

    generateList(data)
    root.focus_force()

#Readme button pressed
def readme():
    messagebox.showinfo(title="How to use", 
    message=
"Step 1: Enter Hostname or IP address at the panel.\n\
Step 2: Press \"Download\" button and enter password.\n\
\tMusic playlist will show up if successfull.\n\
Step 3: Press \"-\" to delete and \"+\" to add music.\n\
Step 4: Press upload and enter password again.\n\n\
Enjoy!\n\
NOTE: Only Youtube URL is allowed")

#Remove hints for hostname entry
def on_entry_click(event):
    if edit_hostname.get() == HOSTNAME_HINT: #Unedited entry
       edit_hostname.delete(0, "end") #Delete all the text in the entry
       edit_hostname.insert(0, '') #Insert blank for user input
       edit_hostname.config(fg = 'black')

#Add hints for hostname entry
def on_focusout(event):
    if edit_hostname.get() == '': #Blank entry
        edit_hostname.insert(0, HOSTNAME_HINT)
        edit_hostname.config(fg = 'grey')

#-----Main Window-----
root = Tk()
root.title("Smart Music Uploader")
root.geometry("300x220")

#-----Top Panel-----
frame_top = Frame(root)
edit_hostname = Entry(frame_top) #Edit field for entering hostname or IP addess
edit_hostname.insert(0, HOSTNAME_HINT) #Add text as hint
edit_hostname.bind('<FocusIn>', on_entry_click)
edit_hostname.bind('<FocusOut>', on_focusout)
edit_hostname.config(fg = 'grey')

edit_hostname.pack(side=LEFT, fill=X, padx=2, pady=2)
Button(frame_top, text="READ ME", bg="#579aff", command=readme).pack(side=RIGHT, padx=2, pady=2) #Read me button
Button(frame_top, text="Download", bg="#579aff", command=download).pack(side=RIGHT, padx=2, pady=2) #Download playlist button
frame_top.pack(side=TOP, fill=X)

#-----Scrollbar for Music List-----
frame_scroll = Frame(root)
scrollbar = Scrollbar(frame_scroll)
scrollbar.pack(side = RIGHT, fill = X)

#Create listbox for displaying music list
musiclist = Listbox(frame_scroll, yscrollcommand = scrollbar.set)
musiclist.insert(END, "Please download the playlist from destination device.")
musiclist.pack( side = LEFT, fill = BOTH, expand = True)
musiclist.bind('<<ListboxSelect>>', onselect)
scrollbar.config(command = musiclist.yview)

frame_scroll.pack(side=TOP, fill=BOTH, expand = True)

#-----Bottom button panels-----
frame_button = Frame(root)

button_del = Button(frame_button, text="-", command=deleteMusic, bg="#ff5757")
button_del.pack(side=LEFT, padx=2, pady=2)
button_add = Button(frame_button, text="+", command=addMusic, bg="#83f781")
button_add.pack(side=LEFT, padx=2, pady=2)
button_upload = Button(frame_button, text="Upload", command=upload)
button_upload.pack(side=RIGHT, padx=2, pady=2)

frame_button.pack(side=BOTTOM, fill=X)

root.mainloop()