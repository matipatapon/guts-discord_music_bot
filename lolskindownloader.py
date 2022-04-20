 
import requests
def download(path = ""):
    url = 'http://leagueskin.net/p/download-mod-skin-2020-chn'
    print("Getting website ...")
    response = requests.get(url)
    if response.status_code == 200:
        for line in response.iter_lines():
            line = line.decode('UTF-8')
            if 'download3' in line:
                print("Extracting download link ...")
                start = line.find('href="')+6
                end = line.find('.zip')+3
                download_link = line[start:end+1]
                print(f"Download link get : {download_link}")
                break
        if download_link!="error":
            print("Downloading file ...")
            response = requests.get(download_link)
            if response.status_code == 200:
                print("Saving file ...")
                path = f"{path}lolskin.zip"
                f = open(path,"wb")
                f.write(response.content)
                f.close()
                print(f"Done ^^\nFile saved to {path}")
                return True
            else:
                print("Something went wrong :(")
    return False
def get_path():
    try:
        f = open("settings.txt","r")
    except:
        f = open("settings.txt","x")
        f.close()
        f = open("settings.txt","r")
    path = f.readline().replace("\n","")
    f.close()
    return path
def update_path():
    try:
        f = open("settings.txt","w")
    except:
        f = open("settings.txt","x")
        f.close()
        f = open("settings.txt","w")
    f.write(input("Type path where I should save lolskin \n(if nothing I will save to folder where lol_skin_upgrader is) ! \n : "))
    f.close()
def main():
    while True:
        path = get_path()
        instruction = f"""
Welcome in lol skin update !
Press enter to download lolskin to '{path}'
Type 'path' to change path where download lolskin !!! for example /home/itam/Desktop/
"""
        print(instruction)
        what = input("What are you wanna do ? ")
        if what == "path":
            update_path()
        else:
            download(path)
main()
