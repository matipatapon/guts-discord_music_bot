#i am going use this to save settings , information about mutes etc
import time
import discord
import asyncio
import settings
#UnicodeEncodeError: 'UCS-2' codec can't encode characters in position 83-83: Non-BMP character not supported in Tk
#https://stackoverflow.com/questions/32442608/ucs-2-codec-cant-encode-characters-in-position-1050-1050
#here i remove emoji from string and idle can handle it 
import sys
#1 i create dictionary with keys from Non - BMP unicodes and value : -> 0xFFFF
non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1) , 0xFFFF)
def dnbc(text):
   #2 i change any of out of range unicodes with 0xFFFF
    return text.translate(non_bmp_map)
def safe_p(string = "nothing"):
    print(dnbc(str(string)))
def check_if_exists(what):
    try :
        file = open(f"{what}.txt","xt")
        file.close()
        safe_p(f"Created {what}.txt file")
    except:
        #safe_p(f"{what}.txt already exists")
        pass
        
#list of guilds and id mute role on this dc
check_if_exists("mute_roles")
mute_roles = []
f = open("mute_roles.txt")
c = f.read().split("\n")

for x in c:
    safe_p(x.split(" "))

#mutes
class mute:
    #creating mute info class
    def __init__(self,guild_id = 0,user_id = 0,mute_time = 0, long = 0, roles = list()):

        self.guild_id = guild_id
        self.user_id = user_id
        self.long = long
        #reading settings from file
        guild_s = settings.read()
        for x in guild_s:
            if int(self.guild_id) == int(x.id_):
                try:
                    mute_role = x.settings["mute_role"]
                except:
                    mute_role = 0
                if long == 0:
                    try:
                        self.long = x.settings["mute_time"]
                    except:
                        self.long = 0
        self.mute_role = int(mute_role)
        if mute_time == 0:
            self.mute_time = time.time()
        else:
            self.mute_time = mute_time
            #safe_p(self.mute_time)
        self.roles = roles
    #saving mute info to the file
    def save(self):
        check_if_exists("mutes")
        file = open("mutes.txt","a")
        #Structure of mute info :
        #Id_of_guilt | Id_of_users | 
        file.write(self.get_string()+"\n")
        file.close()
    #mute user / remove specified roles and add mute role
    async def mute_user(self,client):
        guild = client.get_guild(int(self.guild_id))
        member = guild.get_member(int(self.user_id))
        roles_to_return = []
        safe_p(dnbc(f"Muting : {member.name} in {guild.name} for {self.long} seconds !"))
        for x in member.roles:
            remove = False
            if x.permissions.send_messages == True:
                remove =True
            elif x.permissions.administrator == True:
                remove = True
            if remove == True:
               try:
                   await member.remove_roles(x)
                   safe_p(dnbc(f"    removed role : {x.name}"))
                   roles_to_return.append(x.id)
               except:
                   safe_p(dnbc(f"    Can't remove role : {x.name}"))
        self.roles = roles_to_return
        try:
            await member.add_roles(guild.get_role(self.mute_role))
            safe_p(dnbc(f"Succesfully muted : {member.name}"))
            self.save()
        except:
            safe_p(f"Can't add mute role with id : {self.mute_role}")
            self.long = -999
            await self.unmute(client)
        
    #return True if user is unmuted or False if not 
    async def unmute(self,client):
        x =  round( time.time()  - float(self.mute_time)  )
        if x >= int(self.long) :
            guild = client.get_guild(int(self.guild_id))
            member = guild.get_member(int(self.user_id))
            for y in self.roles:
                try:
                    y = guild.get_role(int(y))
                    try:
                        await member.add_roles(y)
                    except:
                        safe_p(f"    Can't return role {y.name} to self.user_id")
                except:
                    safe_p(dnbc(f"   Can't get role {y}"))
            try:
                await member.remove_roles(guild.get_role(self.mute_role))
            except:
                safe_p(f"    Can't remove mute role from : {self.user_id}")
                return False 
            return True
        return False
    #return ready to save to the file string 
    def get_string(self):
        string = f"{self.guild_id} {self.user_id} {self.mute_time} {self.long}"
        #safe_p(self.roles)
        if len(self.roles) > 0:
            roles = " "
            for x in self.roles:
                #safe_p(f"    saving roles : {x}")
                roles += str(x)+" "
            string+=roles
        #safe_p(f"    Saving : {string}")
        return string
#Checking if somebody should be unmutened on specified interval of time 
async def mute_loop(interval,client):
    while True:
        #safe_p("! Starting mute loop !")
        check_if_exists("mutes")
        #reading list of mutes 
        f = open("mutes.txt","rt")
        l = f.read()
        f.close()
        l = l.split("\n")
        mutes = []
        new_file = ""
        #transport mutes to list of objects 
        for x in l:
            y = x.split(" ")
            if len(y) < 4:
                continue
            roles = []
            for z in y[4:]:
                if len(z)<1:
                    continue
                roles.append(z)
                
            #safe_p(y)
            y = mute(y[0],y[1],y[2],y[3],roles)
            mutes.append(y)
        #checking if any mutes should be unmuteenned
        for x in mutes:
            if await x.unmute(client):
                safe_p(f"    Sucesfully unmuted : {x.user_id}")
            else:
                new_file += x.get_string()+"\n"
        #saving to file
        f = open("mutes.txt","w")
        f.write(new_file)
        f.close()
        #await asyncio.sleep(10)
        #safe_p("! Ending mute loop !")
        await asyncio.sleep(interval)
#Mute
async def mute_user(client,message = None,remove = False,guild_id = 0,member_id = 0,long = 0):
    if guild_id == 0 or member_id == 0 :
        if message == None:
            return
        else:
            guild_id = message.guild.id
            member_id = message.author.id
    guild_s = settings.get_settings_of("g"+str(guild_id))
    if long == 0:
        long = guild_s.settings.get("long")
        if long == None:
            long = 0
    mute_object = mute(guild_id,member_id,0,long)
    await mute_object.mute_user(client)
    try:
        await message.delete()
    except:
        pass
    try :
        await message.author.send("Really !?\nDo you don't have anything more intresting to do ?\nYou are muted for :  "+str(mute_object.long)+" seconds "+str(message.author.name)+" !\n https://tenor.com/view/guts-berserk-cringe-too-strong-gif-19635652")
    except:
        pass
