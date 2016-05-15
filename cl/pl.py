# -*- coding: utf-8 -*-
import sys
from os import remove, getenv
import time
import subprocess as sp
import yt
import curses
import datetime
import random

#optionList = ["-url", "-chromehistory", "-file", "-help", "-screen", "-audio"]
isPlaylist = False
plToPlay = ""
idToPlay = ""
shuffleList = True
windowPos = "0 0 0 0"
audioOut = "both"

def printHelp():
    print """Usage:
    Play YouTube videos and playlists with omxplayer.
    Provide Yt URL after the -url argument:
        python ytube.py -url [URL]
    Provide path to textfile containing Yt URL after the -file argument:
        python ytube.py -file [PATH]
    Read last visited URL out of Chromium history:
        python ytube.py -chromehistory
    If more than one source is given hierachy is as follows:
        URL > FILE > CHROMEHISTORY
    List of other options:
    -audio <hdmi/local/both> -> force audio output of omxplayer (default: both)
    -screen <full/mini/none> -> set position of video window (default: full)"""

def copyDB():
    buffer_size = 1024*1024
    try:
        source = file(getenv("HOME")+".config/chromium/Default/History", "rb")
        dest = file(getenv("HOME")+"History.tmp", "wb")
        while True:
            copy_buffer = source.read(buffer_size)
            if copy_buffer:
                dest.write(copy_buffer)
            else:
                break
        source.close()
        dest.close()
    except IOError:
        raw_input("Could not find Chromium history database! Do you have Chromium installed?")
        quit()

def findOpt(opt, optArr):
    for x in range(len(optArr)):
        if optArr[x]==opt:
            return x

def getId():
    global isPlaylist
    global plToPlay
    global idToPlay
    global shuffleList
    global windowPos
    global audioOut
    urlToPlay = ""
    sffl = False
    if len(sys.argv)>1:
        if "-url" in sys.argv:
            urlToPlay = sys.argv[findOpt("-url", sys.argv)+1]
        elif "-file" in sys.argv:
            try:
                urlFile = file(sys.argv[findOpt("-file", sys.argv)+1], "r")
                fileStr = urlFile.readline()
                urlFile.close()
                fileStrArr = fileStr.split(":")
                for y in range(len(fileStrArr)):
                    if fileStrArr[y].strip()=="http":
                        urlToPlay = "http:"+fileStrArr[y+1]
                        break
            except IOError:
                raw_input("Could not find given file!")
                quit()
            except IndexError:
                raw_input("Could not retrieve URL from given file! Is your file formatted correctly?")
                quit()
        elif "-chromehistory" in sys.argv:
            copyDB()
            urlToPlay = sp.check_output(["sqlite3", getenv("HOME")+"History.tmp", "SELECT url FROM urls ORDER BY last_visit_time DESC LIMIT 1"])
            remove(getenv("HOME")+"History.tmp")
        if "-help" in sys.argv:
            printHelp()
        if "-screen" in sys.argv:
            y = findOpt("-screen", sys.argv)+1
            if sys.argv[y]=="mini":
                windowPos = "1440 785 1920 1055"
            elif sys.argv[y]=="none":
                windowPos = "0 0 1 1"
            elif sys.argv[y]=="full":
                windowPos = "0 0 0 0"
        if "-audio" in sys.argv:
            if sys.argv[findOpt("-audio", sys.argv)+1] in ["hdmi", "local", "both"]:
                audioOut = sys.argv[findOpt("-audio", sys.argv)+1]
        if urlToPlay!="":
            try:
                parts = urlToPlay.split("/")
                if parts[2].endswith(".com"):
                    parts = urlToPlay.split("?")
                    parts = parts[1].split("&")
                    for part in parts:
                        if part[:2]=="v=":
                            idToPlay = part[2:]
                        elif part[:5]=="list=":
                            plToPlay = part[5:]
                        elif part[:8]=="shuffle=":
                            sffl = True
                    if (idToPlay!="") & (plToPlay!=""):
                        if raw_input("Gefundene Playlist abspielen? (y/n) ")=="y":
                            isPlaylist = True
                    elif plToPlay!="":
                        isPlaylist = True
                    if isPlaylist and not sffl:
                        if raw_input("Zufällige Wiedergabe einschalten? (y/n) ")=="n":
                            shuffleList = False
                else:
                    idToPlay = parts[3]
            except:
                raw_input("Retrieved String seems not to be a YouTube URL!\nCheck for typos if using -url, formatting errors in your file if using -file and make sure the video page is your last visited site in Chromium if using -chromehistory !")
                quit()
    else:
        printHelp()

def makeascii(string):
    output = ""
    for x in string:
        if ord(x)>128:
            output = output + "?"
        else:
            output = output + x
    return output
            
def converttoiso(timeinsec):
    secs = timeinsec%60
    hours = (timeinsec-timeinsec%3600)/3600
    mins = (timeinsec-hours*3600-secs)/60
    time = datetime.time(hours, mins, secs)
    return time.isoformat()

def generateSubs(title, lenght):
    endtimestr = converttoiso(lenght)
    subFile = file(getenv("HOME") + "omxplayytSubs.srt", "w")
    if lenght>60:
        preendtimestr = converttoiso(lenght-30)
        subFile.write("1\n00:00:00,000 --> 00:00:15,000\n"+title+"\n\n2\n"+preendtimestr+",000 --> "+endtimestr+",000\n"+title)
    else:
        subFile.write("1\n00:00:00,000 --> "+endtimestr+",000\n"+title+"\n")
    subFile.close()

def play(scr):
    scr.clear()
    scr.nodelay(1)
    scr.keypad(1)
    startPos = 0
    if isPlaylist:
        scr.addstr("Loading Playlist... ")
        scr.refresh()
        pl = yt.Playlist(plToPlay)        
        toPlay = pl.videos
        if shuffleList:
            random.shuffle(toPlay)
            vidBuffer = toPlay[0]
            for vid in toPlay:
                if vid.id==idToPlay:
                    toPlay[0] = vid
                    vid = vidBuffer
                    vidBuffer = None
                    break
        else:
            for x in range(len(toPlay)):
                if toPlay[x].id==idToPlay:
                    startPos = x
                    break
        scr.addstr("Done ("+str(len(toPlay))+" Videos queued)\nNow playing: " + pl.title + "\nStarting Position is " + str(startPos+1) + "\n")
        scr.refresh()
    else:
        toPlay = [yt.Video(idToPlay)]
    scr.addstr("Loading Stream for: "+makeascii(toPlay[startPos].title)+"... ")
    scr.refresh()
    getStream = sp.Popen(["youtube-dl", "-g", "http://www.youtube.com/watch?v=" + toPlay[startPos].id], stdout=sp.PIPE)
    streamNow, err = getStream.communicate()
    x = startPos+1
    y = startPos
    scr.addstr("Done\n")
    scr.refresh()
    while y < len(toPlay):
        if isPlaylist & (x<len(toPlay)):
            playNext = True
            scr.addstr("Loading Stream for: "+makeascii(toPlay[x].title)+"... ")
            scr.refresh()
            streamProc = sp.Popen(["youtube-dl", "-g", "http://www.youtube.com/watch?v=" + toPlay[x].id], stdout=sp.PIPE, stderr=sp.PIPE)
            x = x+1
        if streamNow!="":
            generateSubs(makeascii(toPlay[y].title), int(float(toPlay[y].duration)))
            omxProc = sp.Popen(["omxplayer", "-o", audioOut, "--subtitles", "/root/omxplayytSubs.srt", "--align", "center", "--win", windowPos, streamNow.strip()], stdin=sp.PIPE, stdout=sp.PIPE)
            while True:
                time.sleep(0.5)
                if omxProc.poll()!=None:
                    break
                try:
                    key = scr.getkey()
                    #if (key!="n")&(key!="KEY_RIGHT")&(key!="KEY_LEFT")&(key!="KEY_UP")&(key!="KEY_DOWN"):
                    #    omxProc.stdin.write(key)
                    if key=="q":
                        omxProc.stdin.write("q")
                        playNext = False
                        break
                    elif key=="n":
                        omxProc.stdin.write("q")
                        break
                    elif (key=="KEY_UP")&(toPlay[y].duration>700):
                        omxProc.stdin.write("\x1B[A")
                    elif (key=="KEY_DOWN")&(toPlay[y].duration>700):
                        omxProc.stdin.write("\x1B[B")
                    elif key=="KEY_RIGHT":
                        omxProc.stdin.write("\x1B[C")
                    elif key=="KEY_LEFT":
                        omxProc.stdin.write("\x1B[D")
                    else:
                        omxProc.stdin.write(key)
                except:
                    key = None
        y = y+1
        if isPlaylist:
            if playNext==False:
                if streamProc.poll()==None:
                    streamProc.terminate()
                break
            elif streamProc.poll()==None:
                scr.addstr("Finishing loading of stream in background... ")
                scr.refresh()
                streamProc.wait()
            elif streamProc.poll()==1:
                y=y+1
            streamNow = streamProc.stdout.read()
            scr.addstr("Done\n")
            scr.refresh()
        else:
            break
            

        
getId()
#print isPlaylist
#print plToPlay
#print idToPlay
#print shuffleList
#raw_input("blubb")
if (idToPlay!="")|(isPlaylist):
    curses.wrapper(play)
print "Done"
