import time as t
filename = "log.txt"
class logger():
    def log(self,l):
        time = (t.localtime())
        time = list(time)
        i = 0
        for x in time:
            if len(str(x))<2:
                time[i] = "0"+str(x)
            i+=1
        text = f"{time[0]}-{time[1]}-{time[2]} {time[3]}:{time[4]}:{time[5]} | "
        text+=l+"\n"
        f = open(filename,"a")
        f.write(str(text))
        f.close()
    def reset(self):
        f = open(filename,"w")
        f.close()

