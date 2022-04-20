"""
1. Create ytdl to download songs and find them ! <-
2. Create function / object to play stop etc songs !
3. Upgrade bot
"""



import discord
from discord.ext import commands,tasks
import ctypes
import os
import asyncio
import youtube_dl
import _thread as thread
import log
l = log.logger()
l.reset()
help(youtube_dl)
#Importing opus
x = ctypes.util.find_library("opus")
discord.opus.load_opus(x)
#l.loging manual of youtube dl
#yt download
class MyLogger(object):
    def debug(self,msg):
        pass
    def warning(self,msg):
        pass
    def error(self,msg):
        l.log(msg)
#dictionary of bots on diffrent dc !!!
#guild_id:bot
bots = {}
#removing uneccesary songs !!!
cleaning_first = True
async def cleaning_songs():
    global cleaning_first
    l.log("Start cleaning")
    needed_songs = set()
    for key,value in bots.items():
        #getting songs names from queue
        for y in value.queue:
            y = y.get("filename")
            needed_songs.add(y)
        #getting songs names from what's actually is playing !!!
        actual_playing = value.actual_playing
        needed_songs.add(actual_playing)
    l.log(f"needed songs : {needed_songs}")
    files = set()
    for x in os.listdir():
        files.add(x)
    l.log(f"Files in folder : {files}")
    #what should i remove ?
    files_to_check = files.difference(needed_songs)
    files_to_remove = set()
    for x in files_to_check:
        if  ("m4a" in x or  "webm" in x) and (".part" not in x or cleaning_first) :
            files_to_remove.add(x)
    l.log(f"I should remove : {files_to_remove}")
    cleaning_first = False
    #removing uneccesarry files !!!
    for x in files_to_remove: 
        try:
            os.remove(x)
        except:
            l.log(f"Can't remove file : {x}")
#Represent a bot  ! 
class music_bot():
    #Don't do something stupid unless ready !!!
    ready = False
    def __init__(self,client,guild_id):

        l.log("start __init__")
        
        self.client = client
        self.guild_id = guild_id
        #settings default values !!!
        #youtube dl options for links 
        self.ydl_options ={
        'format': 'bestaudio/best',
        'extractaudio': True,   
        'audioformat': "mp3",   
        'progress_hooks':[
        self.progress],
        'logger': MyLogger(),
        'default_search':"auto",
        }
        '''
        #this one is for searching by title !
        self.ydl_options_title={
        'format': 'bestaudio/best',
        'extractaudio': True,   
        'audioformat': "mp3",   
        'progress_hooks':[
        self.progress],
        'logger': MyLogger(),
        }
        '''
        self.ydl = youtube_dl.YoutubeDL(self.ydl_options)
        #self.ydl_title = youtube_dl.YoutubeDL(self.ydl_options_title)
        self.channel_to_connect = None
        #setting voice_client to none disconnected if needed
        self.voice_client = None
        self.client.loop.create_task(self.loopy())
        self.prev_message = None
        self.ready = True
        
        l.log("I am ready")
        #
    async def on_message(self , message):
        #if bot is not ready don't do anything !!!!
        l.log(f"on message !!!")
        if not self.ready:
            await asyncio.sleep(1)
            await self.on_message(message)
            return
        await self.control(message)
#control <- get message and check if do something !!!
    #commands !!!
    commands ={
        "add_song_to_queue":"play",
        "skip_song":"skip",
        "pause_song":"pause",
        "unpause_song":"unpause",
        "loop_song":"loop",
        "move_to_another_channel":"come",
        "status":"status",
        "disconnect":"leave",
        }
#reporting status and send info about somethinng
    actual_playing = "Nothing ..."
    async def report(self,message,what = 0 ):
        string = "I shouldn't write this ..."
        #status 
        if what == 0 :
            string = "__**My Status**__\n"
            #what i am actual playing ?
            string+=f"**I actually play** :\n {self.actual_playing}\n"
            #did music is paused looped etc
            if self.pause == True:
                pause = "Yes"
            else:
                pause = "No"
            string+=f"**Am i paused ?** :\n {pause}\n"
            if self.loop_play == True:
                loop = "Yes"
            else:
                loop = "No"
            string+=f"**Am i looped ?** :\n {loop}\n"
            #queue of thesongs !!
            string+="**Queue** : \n"
            if len(self.queue) > 0 :
                i = 1
                for x in self.queue:
                    x_name = x.get("filename")
                    if x_name == None:
                        x_name = "something"
                    string+=f"#{i} - {str(x_name)}\n"
                    i+=1
            else:
                string+="empty..."
        #Can't connect to vc !!!
        if what == 1:
            string = "I can't join to your channel ... sorry ..."
        if what == 2:
            string = "I can't leave ..."
        if what == 3:
            string = "Paused !!!"
        if what == 4:
            string = "Unpaused !!!"
        if what == 5:
            string = "Loop enabled !"
        if what == 6:
            string = "Loop disabled !"
        if what == 7:
            string = "I start downloading song please be patient !\n(! sometimes it take very long !)"
        if what == 8:
            string = "Sorry i broke song try again !"
        try:
            await message.channel.send(string)
        except:
            l.log("Can't send message")

#react to commands and say what do 
    async def control (self,message):
        content = message.content[1:]
        c = self.commands
        #add song to queue and if necessary join channel !!!!
        if content.startswith(f"{c['add_song_to_queue']} "):
            
            await self.connection(message.author.voice)
            
            search = content.replace(f"{c['add_song_to_queue']} ","")
            self.report_download_channel = message.channel
            await self.add_to_queue(search = search, message = message)
            await cleaning_songs()
        elif content.startswith(f"{c['skip_song']}"):
            self.skip = True
        elif content.startswith(f"{c['pause_song']}"):
            self.pause = True
            await self.report(message,3)
        elif content.startswith(f"{c['unpause_song']}"):
            self.pause = False
            await self.report(message,4)
        elif content.startswith(f"{c['move_to_another_channel']}"):
            await self.connection(message.author.voice)
        elif content.startswith(f"{c['loop_song']}"):
            if self.loop_play == True:
                l.log("looping song disabled !")
                self.loop_play = False
                await self.report(message,6)
            elif self.loop_play == False:
                l.log("looping song enabled !")
                self.loop_play = True
                await self.report(message,5)
                
        elif content.startswith(f"{c['status']}"):
                await self.report(message)
        elif content.startswith(f"{c['disconnect']}"):
                await self.disconnect()

    async def connection(self,voice = None,channel = None):
        if voice == None and channel ==None:
            l.log("connection Channel not specified")
            return
        if channel == None:
            channel = voice.channel
        l.log(f"Connecting to {channel.name}")
        if self.voice_client == None :
            l.log("connection #1 try connect ...")
            try:
                l.log("Trying connect to channel !")
                self.voice_client = await channel.connect()
                self.channel_to_connect = channel
            except:
                l.log("Can't connect to channel")
                #saving to what channel be "bounded"
                self.channel_to_connect = channel
        else:
                l.log("Connection when vc is not null")
            #ignore if try connect to the same channel where is !
            #if not self.voice_client.channel.id == channel.id:
                #if is connected just move to another channel ! ! !
                if self.voice_client.is_connected():
                    l.log("moving to another channel !")
                    if self.voice_client.channel.id == channel.id:
                        l.log("It's the same channel ! I just skip this !")
                        return
                    await self.voice_client.move_to(channel)
                    self.channel_to_connect = channel
                else:
                    l.log("connecting to another channel !")
                    await self.disconnect()
                    try:
                        await self.voice_client.move_to(channel)
                    except:
                        l.log("can't switch to another change")
                    self.channel_to_connect = channel
        
                
        

    async def disconnect(self):
        if self.voice_client == None:
            return
        try:
            x = self.voice_client.is_connected()
        except:
            x = False
        if x :
            try:
                await self.voice_client.disconnect()
                self.voice_client = None
                self.channel_to_connect = None
                await self.report(2)
            except:
                l.log("Can't disconnect !")

#queue of song to play !!!
    queue = []
# checking of the downloading file progress !!!
    def progress(self,d):
        status = d["status"]
        if status == "downloading":
            speed = d['speed']
            if speed != None:
                speed = str(round(speed/1024/1024/8))+"MB/S"
            downloaded_bytes = d['downloaded_bytes']
            total_bytes_estimate = d['total_bytes']
            if downloaded_bytes == None:
                downloaded_bytes = 1
            if total_bytes_estimate == None:
                total_bytes_estimate = 1
            percent = round((downloaded_bytes / total_bytes_estimate)*100)
            l.log(f"percent : {percent}")
            report_download_info = f"Downloading with **speed** of {speed} **Title** : {d['filename']} | **Percent** : {percent}% | **Will be ready for** : {d['eta']} seconds !"
            l.log(f"rep : {report_download_info}")
            if report_download_info != None:
                self.report_download_info = report_download_info
                self.report_download_progress = True
            
        elif status == "error":
            pass
        elif status == "finished":
            self.last_download_message = None
            l.log(f"Downloading complete of {d['filename']} file !")
            self.queue.append(d)
            l.log(f"{d['filename']} has been added to queue !")
            self.report_download_info = f"{d['filename']} has been added to queue !!!"
            self.report_download_progress = True
    #adding song to queue
    async def add_to_queue(self,search,message):
        if not message.author.voice:
            return
        #adding song to queue !!!
        #checking if it isn't a link ? 
        try:
            await self.report(message,7)
            thread.start_new_thread(self.ydl.download,([search],))
        except:
            await self.report(message,8)
            l.log("Something goes wrong ...")

    channel_switch = False
    ignore = False
    state_update = False
    disconnected = False
    async def on_voice_state_update(self ,*d):
        #gettings voice state
        l.log("!!!on_voice_state_update !!!")
        d_length = len(d)
        l.log(f"*d count : {d_length} ")
        member = d[0]
        for x in range(d_length):
            l.log(f"{x} element {str(d[x])}\n")                
        if member.id == self.client.user.id:
            l.log("It was me !\nKono dio da !")
            self.disconnected = False
            if d_length == 3:
                if d[2].channel != None and not self.ignore == True:
                    l.log("Channel where i moved is not Null")
                    if self.voice_client != None:
                        l.log(f"Is playing ? :{self.voice_client.is_playing()}")
                        if self.voice_client.is_playing():
                            #for now if channel changed just skip song for now ...! 
                            self.skip = True
                            self.state_update = True
                else:
                    l.log("Voice client is null so i got disconnected !!!")
                    self.disconnected = True

                    
        else:
            l.log("It wasn't me !")
        l.log("### on_voice_state_update ###")
    
    #default settings to play
    skip = False
    pause = False
    loop_play = False
    loop_song = None

    report_download_channel = None
    report_download_progress = True
    report_download_info= None

    #main loop of the bot
    async def loopy(self,interval = 1):
        while True:
            #try:
            await self.play()
            #except:
                #l.log(f"Play loop broke error ")
            await self.alone()

            await asyncio.sleep(interval)

    alone_second = 60
    alone_how_long = 0
    async def alone(self):
        if self.voice_client == None:
            return
        if not self.voice_client.is_connected():
            return
        members = self.voice_client.channel.members
        somebody = False
        for x in members:
            if not x.bot and not x.voice.self_deaf and not x.voice.deaf:
                somebody = True
                break
        if somebody:
            self.alone_how_long = 0
        elif not somebody:
            self.alone_how_long += 1
            l.log(f"I was left alone for : {self.alone_how_long} seconds !")
            if self.alone_how_long > self.alone_second:
                l.log("I disconnect becouse you monsters left me alone ! ")
                await self.disconnect()
                self.alone_how_long = 0
            
            
                
        
            
    def return_self(self):
        return self
    async def play(self,interval = 1):
            l.log("!!! play !!!")
            self = self.return_self()
            #reporting about status of downloading
            if self.report_download_progress and self.report_download_info and self.report_download_channel:
                try:
                    await self.report_download_channel.send(self.report_download_info)
                    l.log("Reporting about status of downloading !")
                    self.report_download_progress = False
                except:
                    self.report_download_progress = False
                    l.log("Can't report about status of downloading !")
            if self.voice_client == None:
                l.log("voice clinet is null during play !")
                return
            if not self.voice_client.is_connected():
                l.log("voice client is not connected !")
                #l.log("Trying recconect to {self.channel_to_cennect.name}!")
                #await self.connection(channel=self.channel_to_connect)
                return
            #when music plays !!!  
            if self.voice_client.is_playing():
                #pauseing
                if self.pause == True:
                    self.voice_client.pause()
                    await asyncio.sleep(interval)
                    return
                #skiping
                if self.skip == True:
                    self.skip = False
                    #setting loop_song for none to block looped skipped song !
                    if not self.state_update:
                        self.loop_song = None
                    self.voice_client.stop()
                    await self.play(interval)
            #playing next song 
            else: 
                song_name = None
                self.actual_playing = "Nothing ..."
                report = f"""
Playing next song !
self.state_update : {self.state_update}
self.loop_play:{self.loop_play}
self.skip:{self.skip}
self.queue:{self.queue}
self.loop_song:{self.loop_song}
"""
                l.log(report)
                #getting song name from loop 
                if (self.loop_play == True or self.state_update) and self.loop_song != None and self.skip == False:
                    self.state_update = False
                    song_name = self.loop_song
                #getting next song from queue
                elif len(self.queue) > 0:
                    self.loop_song = self.queue[0]["filename"]
                    song_name = self.loop_song
                    self.queue.pop(0)
                if song_name != None:
                    audio = discord.FFmpegOpusAudio(song_name,  executable='ffmpeg/ffmpeg', pipe=False, stderr=None, before_options=None, options=None)
                    #os.remove(song_name)
                    try:
                        self.voice_client.play(audio)
                        l.log(f"audio is opus ? : {audio.is_opus()}")
                        self.actual_playing = song_name
                    except Exception as e:
                        l.log(f"Can't play song error : \n {e}")
            #unpausing
            if self.voice_client.is_paused():
                if self.pause == False:
                    self.voice_client.resume()
            await asyncio.sleep(interval)
            l.log("### play ###")

async def on_ready():
    pass

async def on_message(message,client):
    if message.author.id != 301383145780150273:
        #return
        pass
    guild = message.guild
    bot = bots.get(str(guild.id))
    if bot == None:
        bots.update({str(guild.id):music_bot(client,guild.id)})
        bot = bots.get(str(guild.id))
    await bot.on_message(message)

async def on_voice_state_update(*d):
    l.log(f"on_voice_state_update something changed !!! ")
    member = d[0]
    if member == None:
        return
    key = str(member.guild.id)
    l.log(f"key : {key}")
    bot = bots.get(key)
    if bot == None:
        return
    await bot.on_voice_state_update(*d)
    if bot.disconnected:
        l.log(f"I got disconnected I should perish !")
        del bots[key]

