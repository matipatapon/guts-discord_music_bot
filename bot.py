#UnicodeEncodeError: 'UCS-2' codec can't encode characters in position 83-83: Non-BMP character not supported in Tk
#https://stackoverflow.com/questions/32442608/ucs-2-codec-cant-encode-characters-in-position-1050-1050
#here i remove emoji from string and idle can handle it 
import sys
#1 i create dictionary with keys from Non - BMP unicodes and value : -> 0xFFFF
non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1) , 0xFFFF)
def dnbc(text):
   #2 i change any of out of range unicodes with 0xFFFF
    return text.translate(non_bmp_map)

from mute import *
import discord
from discord.ext import commands , tasks
import os
import asyncio
import time
import settings
import blacklist
import music_bot
#from file_save import ban_save
#It is uses to hide my bot token and load it from .env file ^^
from dotenv import load_dotenv
load_dotenv()
#Getting bot token from .env file 
TOKEN = os.getenv("TOKEN")

#Changing bot intents / priviliges idk 
intents = discord.Intents.default()
intents.members = True
intents.emojis = True

pre = os.getenv("PRE")

#Creating client object
client = discord.Client(intents = intents)
#On Ready function
@client.event
async def on_ready():
    #Report after getting ready
    print("I am Guts !")
    guilds = client.guilds
    print(f"I am connected to {len(guilds)} guilds :")
    for x in guilds:
        print(f" - {x.name} id : {x.id}")
        print("- - Members ")
        for y in x.members:          
            print(f" - - - {dnbc(y.name)} id : {y.id}")
        print("- - Channels ")
        for y in x.channels:          
            print(f" - - - {dnbc(y.name)} id : {y.id}")
    #get all roles
        print("- - Roles ")
        for y in x.roles:
            print(f" - - - {dnbc(y.name)} id : {y.id}")
    #checking for unban 
    client.loop.create_task(mute_loop(1,client))
#kill command param
author_kill = ""
@client.event
async def on_voice_state_update(*d):
    await music_bot.on_voice_state_update(*d)
@client.event
async def on_message(message):
    #Loging chat who what say
    channel = message.channel
    channel_type = str(channel.type)
    if channel_type == "private" :
        return
    author = message.author
    author_id = message.author.id
    content = message.content
    #if this message is from guts skip
    if message.guild.me.id == author_id:
        return
    print(f"{dnbc(author.name)} write \"{dnbc(content)}\" on {dnbc(channel.name)}")
    #Commands
    content = content.lower()
    if content.startswith(pre):
        content = content[1:]
        await music_bot.on_message(message,client)
        #kill command
        global author_kill
        if content.startswith("kill"):
            await channel.send("Who ?")
            author_kill = author
        elif author_kill == author:
            await channel.send(f"I am coming for you {content}")
            author_kill = ""
        #block commands
        #Get info
        elif content.startswith("blockinfo"):
            await blacklist.blockinfo(client,message)
        #User can block each ( block pinging etc ! )  i need to return after that becouse ( if somebody is blocked and i want unblock him i can't becouse i get mute)
        elif content.startswith("block"):
            await blacklist.main(client,message)
            return
        #also they can unblock each other
        elif content.startswith("unblock"):
            await blacklist.unblock(client,message)
            return
        await blacklist.violation_check(client,message)
        """
    #Mute for ping becouse ... my friends are idiots ... 
        teams = []
            #team a oshee , tujkolq etc 
        team_A = [340220586947117058,666724597076590603,485441372430794753]
        #teams.append(team_A)
            #team Marcin 
        team_B = [723474062499774514]
        #teams.append(team_B)
            #test team
        team_C = [301383145780150273,484744683436638219]
        teams.append(team_C)
        #for x in teams:
            if author_id in x :
                Autor Matuesz Piętka ^^
                for y in teams:
                   # print("y : ",y)
                    if y != x :
                        #print("It work")
                        for z in y:
                            if str(z) in content:
                                await mute_user(client,message,True,message.guild.id,message.author.id)

    """
        
        #mute_me
        if content.startswith("mute_me"):
            await mute_user(client,None,False,message.guild.id,message.author.id,10)
            await channel.send("If you say so ...")
        #help
        if content.startswith("help"):
            x = """
    :crossed_swords:  Hi I am Guts The Black Swordsman ! :crossed_swords: 
    version : 0.07 aka chce zdalne 27.10.2021
    **MUSIC**
    #!#play title/link <- play song from yt

    #!#skip <- skip current song

    #!#status <- info about what's playing etc

    #!#pause <- pause song

    #!#unpause <- unpause song

    #!#loop <- loop current song

    #!#come <- come to my channel

    #!#leave <- leave from vc 

    Commands :

    #!#help - getting help

    #!#settings - server settings only for admins : 
    s - show current settings
    example :
    #!#settings s 
    c - change settings
    mute_role - role for muted persons (name) 
    mute_time - for how many seconds mute persons ?
    example :
    #!#settings c mute_role muted - changing role for muted

    #!#kill - kill person ( don't work :slight_frown: #!# )

    #!#mute_me - mutting yourself for 10 s (good plan)

    #!#block - you can block user from pinging you !
    Syntax :
    #!#block @who can_ping_me?(yes/no[default:no])
    Example :
    #!#block @issar

    #!#unblock - unblock blocked user
    Syntax :
    #!#unblock @who
    Example :
    #!#unblock @issar

    #!#blockinfo - you can check who you have blocked or who blocked you !

    if you will find some bug write to me !!! what's broken !!! pls !!!
    Itam#9264
    (sorry for bad english)
    """
            x = x.replace("#!#",pre)
            await channel.send(x)
        #change settings
        if content.startswith("settings"):
            if not author.permissions_in(channel).administrator:
                channel.send("You are not admin-chan !")
            x = content.strip()
            x = x.split(" ",3)[1:]
            if len(x) < 1:
                x.append("s")
            if x[0] == "c":
                if x[1] == "mute_role":
                     found = False
                     print(x[2])
                     for y in message.guild.roles:
                         print(f"{x[2]} , {y.name}")
                         if x[2] in y.name.lower():
                             x[2] = int(y.id)
                             found = True
                             break
                     if not(found):
                         await channel.send("Incorect role name !\nEnsure the mute role name not contains emojii etc and exists !")
                         return 
                     d = {}
                     d[x[1]] = x[2]
                     settings.update("g"+str(message.guild.id),**d)
                     await channel.send(f"Mute role changed for : {message.guild.get_role(x[2]).name}")
                elif x[1] == "mute_time":
                    try:
                         x[2] = abs(int(x[2]))
                    except:
                        await channel.send("Incorect number of seconds !")
                        return
                    d = {}
                    d[x[1]] = str(x[2])
                    settings.update("g"+str(message.guild.id),**d)
                    await channel.send(f"Mute time changed for : {x[2]} seconds !")
            elif x[0] == "s":
                string = "Current settings : \n"
                guild_s = settings.read("g")
                print(f"len : {len(guild_s)}")
                for y in guild_s:
                    if message.guild.id == y.id_:
                        for z in y.settings :
                            string+=f"{z} = {y.settings[z]}\n"
                        break
                string +="Rest of the settings are default ( 0 )"
                await channel.send(string)
            else:
                await channel.send("Wrong syntax :(")
                return
    
        
client.run(TOKEN)
