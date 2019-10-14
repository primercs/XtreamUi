import paramiko, os, socket, time, json
from config import decrypt

# Status: 0 - Not Started       1 - Started         2 - Done

def getIP():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except: return None

rDownloadURL = "https://xtream-ui.com/install/balancer.py"
rPath = "/home/xtreamcodes/iptv_xtream_codes/adtools/balancer/"
rConfig = decrypt()
rIP = getIP()
rTime = time.time()

def writeDetails(rDetails):
    rFile = open("%s%d.json" % (rPath, int(rDetails["id"])), "w")
    rFile.write(json.dumps(rDetails))
    rFile.close()

def installBalancer(rDetails):
    rDetails["status"] = 1
    writeDetails(rDetails)
    rClient = paramiko.SSHClient()
    rClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try: rClient.connect(rDetails["host"], rDetails["port"], "root", rDetails["password"])
    except:
        rDetails["status"] = 0
        writeDetails(rDetails)
        return True
    try:
        rIn, rOut, rErr = rClient.exec_command("sudo apt-get install python -y")
        rStatus = rOut.channel.recv_exit_status()
        rIn, rOut, rErr = rClient.exec_command("sudo wget \"%s\" -O \"/tmp/balancer.py\"" % rDownloadURL)
        rStatus = rOut.channel.recv_exit_status()
        rIn, rOut, rErr = rClient.exec_command("sudo python /tmp/balancer.py \"%s\" \"%s\" \"%s\" \"%s\" \"%s\" %d" % (rIP, rConfig["db_port"], rConfig["db_user"], rConfig["db_pass"], rConfig["db_name"], int(rDetails["id"])))
        rStatus = rOut.channel.recv_exit_status()
    except: pass
    rDetails["status"] = 2
    writeDetails(rDetails)
    return True

if __name__ == "__main__":
    if rIP and rConfig:
        for rFile in os.listdir(rPath):
            try: rDetails = json.loads(open(rPath + rFile).read())
            except: rDetails = {"status": -1}
            if rDetails["status"] == 0: installBalancer(rDetails)