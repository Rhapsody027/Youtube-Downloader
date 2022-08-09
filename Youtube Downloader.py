from time import sleep
from tkinter import ttk
from tkinter import messagebox
from pytube import Playlist
from pytube import YouTube
from bs4 import BeautifulSoup
from youtube_search import YoutubeSearch
import tkinter as tk
import threading
import subprocess
import os
import requests

GENRE_DICT = {
              'Bass House': '91',
              'Deep House': '12',
              'Dubstep': '18',
              'Electronica': '3', 
              'Progressive House': '15',
              'Hardstyle': '8', 
              'Techno': '90', 
              'Trap': '38'
             }       
YT_BASE = 'https://www.youtube.com'
BEATPORT_BASE = 'https://www.beatport.com/genre/'
FILE_PATH = 'D:\\YouTube Download'
LOCK = threading.Lock()

count = 0 # count for the last to finish download
exist = 0 # check if the file has existed


# get tracklist from beatport
def get_bp_tracklist(url, n):
    r = requests.get(url)
    bs = BeautifulSoup(r.text, 'lxml')

    title_list = bs.select('span.buk-track-primary-title')
    remixer_list = bs.select('span.buk-track-remixed')
    artist_list = bs.select('p.buk-track-artists')
    artist_list.pop(0)

    for i in range(len(artist_list)):
        artist_group = artist_list[i]
        artist_group = artist_group.select('a')
        artist = ''
        for name in artist_group:
            artist += name.text + ', '
        artist_list[i] = artist.rstrip(', ')

    search_list = []
    for i in range(n):
        yt_search = title_list[i].text +\
            ' - ' + artist_list[i] +\
            ' (' + remixer_list[i].text + ')'
        search_list.append(yt_search)

    return search_list

# download tracklist (get list with func: get_tracklist)
def tracklist_dload(name, n):    
    global count, exist

    LOCK.acquire()
    size = listbox.size()
    sleep(0.05)
    listbox.insert(tk.END, f'{size+1:02d}:o Downloading......{name}')
    LOCK.release()

    results = YoutubeSearch(name, max_results=1).to_dict()
    video_url = results[0]['url_suffix']
    video_url = YT_BASE + video_url

    video = YouTube(video_url)
    forbidden = './\*?:"<>|\''
    for char in range(len(forbidden)):
        name = name.replace(forbidden[char], "")

    check_path = FILE_PATH + '\\' + name + '.wav'
    if not os.path.exists(check_path):
        out_file = video.streams.filter(
            only_audio=True).last().download(FILE_PATH)
        new_file = FILE_PATH + '\\' + name + '.wav'
        try:
            os.rename(out_file, new_file)
        except:
            try:
                os.remove(out_file)
            except:
                video = YouTube(video_url)
                video.streams.filter(
                    only_audio=True).last().download(FILE_PATH) 
    else:
        exist += 1
        print('File Existed')

    LOCK.acquire()
    listbox.delete(size)
    listbox.insert(size, f'{size+1:02d}:● Finished......{name}')
    var.set("Download Status (Click to Open File Folder)")
    LOCK.release()

    count += 1
    if count == n:
        messagebox.showinfo("Finally", "All Download has Finished")
        count = 0
        if exist > 0:
            messagebox.showerror("Idiot", f"{exist} file has existed")
            exist = 0
        var.set("Download Status (Click to Open File Folder)")

# func connect with button for tracklist
def click_for_tracklist():
    count = int(num.get())
    genre = gerne_list.get()
    genre_num = GENRE_DICT[genre]
    url = BEATPORT_BASE + genre + '/' + genre_num + '/top-100'

    search_list = get_bp_tracklist(url, count)
    n = len(search_list)
    t_list = []
    for i in range(count):        
        t = threading.Thread(target=tracklist_dload, args=(search_list[i], n))
        t_list.append(t)
        t.start()

# download youtube playlist
def yt_dload(url, listbox, n):
    global count, exist

    video = YouTube(url)
    name = video.title

    file_type = filetype_list.get()

    if len(name) > 57:
        xsbar.place(rely=0.86, relx=0.5, anchor='s', relwidth=0.75)

    LOCK.acquire()
    size = listbox.size()
    sleep(0.05)
    listbox.insert(tk.END, f'{size+1:02d}:o Downloading......{name}')
    LOCK.release()

    forbidden = """./\*?:'"<>|,"""
    for char in range(len(forbidden)):
        name = name.replace(forbidden[char], "")
    check_mp4_path = FILE_PATH + '\\' + name + '.mp4'
    check_wav_path = FILE_PATH + '\\' + name + '.wav'
    check_mp3_path = FILE_PATH + '\\' + name + '.mp3'

    if 'MP4' in file_type:
        if not os.path.exists(check_mp4_path):
            out_file = video.streams.get_highest_resolution().download(FILE_PATH)
        else:
            exist += 1
    else:
        if 'WAV' in file_type:
            if not os.path.exists(check_wav_path):
                out_file = video.streams.last().download(FILE_PATH)
                base, ext = os.path.splitext(out_file)    
                new_file = base + '.wav'
        elif 'MP3' in file_type:
            if not os.path.exists(check_mp3_path):
                out_file = video.streams.last().download(FILE_PATH)
                base, ext = os.path.splitext(out_file)    
                new_file = base + '.mp3'

        try:
            os.rename(out_file, new_file)
        except:
            print('File Existed')
            exist += 1

    LOCK.acquire()
    listbox.delete(size)
    listbox.insert(size, f'{size+1:02d}:● Finished......{name}')
    var.set("Download Status (Click to Open File Folder)")

    count += 1
    if count == n:
        messagebox.showinfo("Finally", "All Downloads has Finished")
        count = 0
        if exist > 0:
            messagebox.showerror("Idiot", f"{exist} file has existed")
            exist = 0
    LOCK.release()

# func connect with button for yt
def click_for_yt():
    try:
        url = yt_url.get()
        playlist = Playlist(url)

        for url in playlist.video_urls:
            n = len(playlist.video_urls)  
            threading.Thread(
                target=yt_dload, args=(url, listbox, n)).start()
        
    except ConnectionResetError:
        messagebox.showerror(
            'Error', 'Pleace Check Your Internet Connection and Retry')
    except KeyError:
        yt_dload(yt_url.get(), listbox, 1)
    except:
        messagebox.showerror('Error', 'Wrong URL or No Internet Connect')

# show where the file are
def openfile(path):
    subprocess.Popen('explorer "' + FILE_PATH)


# make a window with tkinter
win = tk.Tk()
win.geometry('640x480')
win.title('Downloader for any song')
yt_url = tk.StringVar()

# change gui for tracklist
def tracklist_dload_gui():
    input_fm.pack_forget()
    lb.place_forget()
    entry.place_forget()
    filetype_list.place_forget()
    btn.place_forget()
    btn_change2.place_forget()
    listbox.place_forget()  
    listbox.delete(0,tk.END)  
    
    input_fm2.pack()
    lb2.place(rely=0.25, relx=0.5, anchor='center')
    gerne_list.place(rely=0.5, relx=0.5, anchor='center')
    num_list.place(rely=0.77, relx=0.5, anchor='center')
    btn2.place(rely=0.5,  relx=0.85, anchor='center')
    btn_change.place(rely=0.5,  relx=0.895, anchor='center')
    listbox.place(rely=0.5, relx=0.5, anchor='center')

# change gui for youtube download
def yt_dload_gui():
    input_fm2.pack_forget()
    lb2.place_forget()
    gerne_list.place_forget()
    num_list.place_forget()
    btn2.place_forget()
    btn_change.place_forget()
    listbox.delete(0,tk.END)

    input_fm.pack()
    lb.place(rely=0.25, relx=0.5, anchor='center')
    entry.place(rely=0.5, relx=0.5, anchor='center')    
    filetype_list.place(rely=0.75, relx=0.5, anchor='center')
    btn.place(rely=0.5,  relx=0.85, anchor='center')
    btn_change2.place(rely=0.5,  relx=0.895, anchor='center')
    listbox.place(rely=0.5, relx=0.5, anchor='center')


# youtube download gui setup
input_fm = tk.Frame(win, bg='lightblue', width=640, height=120)

lb = tk.Label(input_fm, text='YouTube Playlist Download', bg='lightblue',
              fg='black', font=('white', 12))

entry = tk.Entry(input_fm, textvariable=yt_url, width=50)

filetype_list = ttk.Combobox(input_fm, state='readonly',
                                values=['WAV (high quality music)',
                                        'MP3 (low quality music)',
                                        'MP4 (video)'])
filetype_list.current(0)

btn = tk.Button(input_fm, text="Start", command=click_for_yt,
                bg='blue', fg='White', font=('細明體', 10))

btn_change2 = tk.Button(input_fm, text="", command=tracklist_dload_gui,
                bg='blue', fg='Black', font=('細明體', 10))

input_fm.pack()
lb.place(rely=0.25, relx=0.5, anchor='center')
entry.place(rely=0.5, relx=0.5, anchor='center')
filetype_list.place(rely=0.75, relx=0.5, anchor='center')
btn.place(rely=0.5,  relx=0.85, anchor='center')
btn_change2.place(rely=0.5,  relx=0.895, anchor='center')

# tracklist download gui setup
input_fm2 = tk.Frame(win, bg='blue', width=640, height=120)

lb2 = tk.Label(input_fm2, text='Hit Song Download', bg='blue',
              fg='white', font=('white', 12))

gerne_list = ttk.Combobox(input_fm2, state='readonly',
                          values=list(GENRE_DICT.keys()))
gerne_list.current(0)

num = tk.StringVar()
num_list = ttk.Entry(input_fm2, textvariable=num, width=3)

btn2 = tk.Button(input_fm2, text="Start", command=click_for_tracklist,
                bg='lightblue', fg='Black', font=('細明體', 10))

btn_change = tk.Button(input_fm2, text="", command=yt_dload_gui,
                bg='lightblue', fg='Black', font=('細明體', 10))

# download status setup
dload_fm = tk.Frame(win, width=640, height=480-120)
dload_fm.place(rely=1, relx=0.5, anchor='s')

var = tk.StringVar()
var.set("Download Status")
lb3 = tk.Label(dload_fm, textvariable=var, fg='black', font=('細明體', 10))
lb3.place(rely=0.1, relx=0.5, anchor='center')

listbox = tk.Listbox(dload_fm, width=65, height=15)
listbox.bind('<Double-1>', openfile)
listbox.place(rely=0.5, relx=0.5, anchor='center')

ysbar = tk.Scrollbar(dload_fm)
ysbar.place(rely=0.5, relx=0.87, anchor='center', relheight=0.7)

xsbar = tk.Scrollbar(dload_fm, orient=tk.HORIZONTAL, width=7)

listbox.config(yscrollcommand=ysbar.set)
ysbar.config(command=listbox.yview)

listbox.config(xscrollcommand=xsbar.set)
xsbar.config(command=listbox.xview)

win.mainloop()