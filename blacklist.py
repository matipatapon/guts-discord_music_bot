#User can block each other ( settings will be save in settings.py )
#library
import settings
from mute import mute_user
#error message
async def error_send(channel,et = 0):
    #invalid syntax
    if et == 1:
        await channel.send("Invalid syntax ! \nSyntax :\n#block @who? can_ping_me?(yes/no)\nExample : #block @issar no")
    if et == 2:
        await channel.send("Invalid syntax ! \nSyntax :\n#unblock @who??")
#command syntax : #block @who? can_ping_me can_remove_my_message
#Main funcition 
async def main(client , message ):
    parameters = message.content.split(" ",3)
    try:
        await message.delete()
    except:
        print("Error can't remove message !")
    try:
        parameters.remove("")
    except:
        pass
    p_count = len(parameters)
    if p_count < 2:
        await error_send(message.channel,1)
        return
    #removing <@! > from parameter
    parameters[1] = parameters[1].replace("<@!","").replace(">","").strip()
    #trying find person !
    try:
        blocked_user = message.guild.get_member(int(parameters[1]))
    except:
        await message.channel.send("You can't block ghosts !...\nTrust me ...")
        return
    if blocked_user.id == message.author.id:
        await message.channel.send("You can't block yourself !")
    #checking if parameter 2 exists can ping me ?
    p2 = False
    if len(parameters) > 2:
        if parameters[2].lower().strip() == "yes":
            p2 = True
        elif parameters[2].lower().strip() == "no":
            p2 = False
        else:
            await error_send(message.channel,1)
            return
    else:
        parameters.append("")
    parameters[2] = p2    
    user_settings = settings.get_settings_of("u"+str(message.author.id))
    #string to save to the guild settings
    d = {}
    #gettings blocked dictionary from user settings !!!!
    if user_settings == None:
        blocked = {}
    else:
        blocked = user_settings.settings.get("blocked")
        if blocked == None:
            blocked = {}
        else:
            pass
    #updating !!!
    #blocked user dict template !!!
    #id:{ping:yes/no}
    user_block = {"ping":p2}
    blocked.update( {str(blocked_user.id) : user_block })
    settings.update("u"+str(message.author.id),**{"blocked":blocked})
    #telling what have you done !
    string = f"You blocked {blocked_user.name} !\n"
    await message.channel.send(string)
#getting info about who i have blocked ?
async def blockinfo(client,message):
    content = "Your block settings :"
    user_settings = settings.get_settings_of("u"+str(message.author.id))
    #if user settings don't exist well nothing to do right ?
    if user_settings == None:
        pass
    else:
        blocked = user_settings.settings.get("blocked")
        if blocked == None:
            pass
        else:
            for x in blocked:
                user = message.guild.get_member(int(x))
                if user == None:
                    continue
                new_line = f"\n{user.name} : "
                dictio = blocked[x]
                if dictio.get("ping") == False:
                    new_line += "\ncan't ping you"
                else:
                    new_line += "\ncan ping you "
                content += new_line
    #checking who have author on mute
    user_settings = settings.read("u")
    content+= "\nYou are blocked by : "
    for o in user_settings:
        x = o.settings.get("blocked")
        print(f"x : {x}")
        if x == None:
            continue
        y = x.get(str(message.author.id))
        if y == None:
            continue
        user = message.guild.get_member(int(o.id_))
        if user == None:
            continue
        content+=f"\n{user.name} : "
        ping = y.get("ping")
        if ping == True:
            content+="\nYou can ping him !"
        else:
            content+="\nYou can't ping him !"
        
    await message.channel.send(content)
    
        
    
#unblocking user
async def unblock(client,message):
    content = message.content
    if "<@!" in content and ">" in content:
        content = content.replace("<@!","").replace(">","").replace("#unblock","").strip()
        if content.isnumeric():
            unblocked = message.guild.get_member(int(content))
            if unblocked != None:
                user_settings = settings.get_settings_of("u"+str(message.author.id))
                blocked = user_settings.settings.get("blocked")
                await message.delete()
                try:
                    blocked.pop(str(unblocked.id))
                except:
                    await message.channel.send("He is not blocked")
                    return
                settings.update("u"+str(message.author.id),**{"blocked":blocked})
                await message.channel.send(f"{unblocked.name} get unblocked !")
            else:
                await message.channel.send("Can't find user")
        else:
            await error_send(message.channel,2)
    else:
        await error_send(message.channel,2)
#if somebody violate the rules mute him ! and kill ! 
async def violation_check(client,message):
    content = message.content
    author = message.author
    #checking if somebody pinged user  who block him if yes mute him ! and kill ! or mention him !
    id_list = ""
    for x in message.mentions:
        id_list += str(x.id)+" "
    #getting settings about users
    user_settings = settings.read("u")
    #checking if somebody don't block author and check if it's him
    for x in user_settings:
        if str(author.id) in id_list or not str(x.id_) in id_list:
        # if 123 in 1234141313131(text) 
            continue
        blocked = x.settings.get("blocked")
        if blocked == None:
            continue
        for y in blocked:
            #checking if author is on somebody blacklist
            if str(message.author.id) == str(y):
                #checking can that person ping me ???
                if blocked[y].get("ping") == False:
                    await mute_user(client,message,True)
                    print(f"User with id : {message.author.id} got muted becouse pinged user with id : {x.id_}")
                    return
       
