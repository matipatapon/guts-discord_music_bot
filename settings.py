#This file will save / read settings from settings.txt  ver 2.0
#making sure that file exist
try:
    f = open("settings.txt","xt")
    f.close()
except:
    pass
"""
Structure of file
id_#settingsname:value#...

...
"""
#Guild and User settings object :
#Guild id : g User id : u
class setting:
    def __init__(self,id_ = "0",**settings):
       #checking of type of the settings
        if str(id_)[0].isalpha():
            self.type_of = f"{id_[0]}"
            self.id_ = int(id_.replace(f"{self.type_of}",""))
        else:
            self.id_ = int(id_)
            self.type_of = "g"
        self.settings = settings
#read settings
# type_off what type of settings return
"""
structure of saving settings 2.0
dict = {id : dict_settings{ something : value , etc } , id2: .....}
"""
def read(type_of = "g"):
    guild_s = []
    f = open("settings.txt","rt")
    file = f.readline()
    try:
        dict_of_settings = eval(file)
    except:
        dict_of_settings = {}
    
    f.close()
    for x in dict_of_settings:
        y = dict_of_settings[x]
        o = setting(x,**y)
        if o.type_of == type_of or type_of == "a":
            guild_s.append(o)
    return guild_s
#Saving settings to file !!! (also update settings )
#type_of = "" <- any type 
def update(id_,**k):
    guild_s = read("a")
    new_file = ""
    dict_of_settings = {}
    #Updating settings !!!!
    exists = False
    for x in guild_s:
        if id_ == x.type_of+str(x.id_) :
            x.settings.update(k)
            exists = True
    if not exists:
        guild_s.append(setting(id_,**k))
        print("not exists !")
    #!!!
    #Saving settings !!!
    for x in guild_s:
        dict_of_settings[x.type_of+str(x.id_)] = dict(x.settings)
    new_file = str(dict_of_settings)+"\n"
    f = open("settings.txt","wt")
    f.write(new_file)
    f.close()
#Gettings specified settings ! ! !
def get_settings_of(id_ = ""):
    if id_ == "":
        return None
    #Gettings type of settings
    first_letter = str(id_[0])
    if not first_letter.isalpha():
        print("Error ! no type specified in get_settings_of !!! None returned")
        return None
    else:
        s = read(first_letter)
    for x in s:
        if str(id_) == x.type_of+str(x.id_) :
            return x
    return None

"""
example ={"s1":1,"s2":2,"s3":3}
list_of_settings = {}
list_of_settings["a"] = setting(1,**example).settings
f = open("settings.txt","at")
f.write(str(list_of_settings)+"\n")
f.close()
f = open("settings.txt","rt")
print(type(eval(f.readline())))
f.close()
"""
