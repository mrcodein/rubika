from rubika.client import Bot,clients
from random import randint
from json import loads, dumps
from requests import post,get
from pathlib import Path

# شناسه اکانتتون
bot = Bot("app_name",auth="AUTH",displayWelcome=False)

# چتی که میخواید فایل در اون آپلود بشه
target = "guid"

# مسیر فایل مورد نظر رو وارد کنید
path = ""


def requestSendFile(file):
    while True:
        try:
            return loads(bot.enc.decrypt(post(json={"api_version":"5","auth": bot.auth,"data_enc":bot.enc.encrypt(dumps({
                "method":"requestSendFile",
                "input":{
                    "file_name": str(file.split("/")[-1]),
                    "mime": file.split(".")[-1],
                    "size": str(499999)
                },
                "client": clients.web
            }))},url=Bot._getURL()).json()["data_enc"]))["data"]
            break
        except: continue


def uploadFile(file):
    frequest = requestSendFile(file)
    bytef = open(file,"rb").read()

    hash_send = frequest["access_hash_send"]
    file_id = frequest["id"]
    url = frequest["upload_url"]

    header = {
        'auth':bot.auth,
        'Host':url.replace("https://","").replace("/UploadFile.ashx",""),
        'chunk-size':str(Path(file).stat().st_size),
        'file-id':str(file_id),
        'access-hash-send':hash_send,
        "content-type": "application/octet-stream",
        "content-length": str(Path(file).stat().st_size),
        "accept-encoding": "gzip",
        "user-agent": "okhttp/3.12.1"
    }

    if len(bytef) <= 131072:
        header["part-number"], header["total-part"] = "1","1"

        while True:
            try:
                j = post(data=bytef,url=url,headers=header).text
                j = loads(j)['data']['access_hash_rec']
                break
            except Exception as e:
                continue

        return [frequest, j]
    else:
        t = round(len(bytef) / 131072)
        f = round(len(bytef) / t + 1)
        for i in range(1,t+1):
            if i != t:
                k = i - 1
                k = k * f
                while True:
                    try:
                        header["chunk-size"], header["part-number"], header["total-part"] = str(len(bytef[k:k + f])), str(i),str(t)
                        o = post(data=bytef[k:k + f],url=url,headers=header).text
                        print(f"part :{i} -> {t}")
                        o = loads(o)['data']
                        break
                    except Exception as e:
                        continue
            else:
                k = i - 1
                k = k * f
                while True:
                    try:
                        header["chunk-size"], header["part-number"], header["total-part"] = str(len(bytef[k:k + f])), str(i),str(t)
                        p = post(data=bytef[k:k + f],url=url,headers=header).text
                        print(f"part :{i} -> {t}")
                        p = loads(p)['data']['access_hash_rec']
                        break
                    except Exception as e:
                        continue
                return [frequest, p]

def sendDocument(chat_id, file, caption=None, message_id=None):
    # Bot.sendDocument("guid","./file.txt", caption="anything", message_id="12345678")
    uresponse = uploadFile(file)

    file_id = str(uresponse[0]["id"])
    mime = file.split(".")[-1]
    dc_id = uresponse[0]["dc_id"]
    access_hash_rec = uresponse[1]
    file_name = file.split("_")[-1]
    size = str(len(get(file).content if "http" in file else open(file,"rb").read()))

    inData = {
        "method":"sendMessage",
        "input":{
            "object_guid":chat_id,
            "reply_to_message_id":message_id,
            "rnd":f"{randint(100000,999999999)}",
            "file_inline":{
                "dc_id":str(dc_id),
                "file_id":str(file_id),
                "type":"File",
                "file_name":file_name,
                "size":size,
                "mime":mime,
                "access_hash_rec":access_hash_rec
            }
        },
        "client": clients.web
    }

    if caption != None: inData["input"]["text"] = caption

    data = {
        "api_version":"5",
        "auth":bot.auth,
        "data_enc":bot.enc.encrypt(dumps(inData))
    }

    while True:
        try:
            return loads(bot.enc.decrypt(loads(post(json=data,url=Bot._getURL()).text)['data_enc']))
            break
        except: continue

def sendmovie(chat_id, file, caption=None):
        uresponse = uploadFile(file)
        thumbnail = "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"
        file_id = str(uresponse[0]["id"])
        mime = file.split(".")[-1]
        dc_id = uresponse[0]["dc_id"]
        access_hash_rec = uresponse[1]
        file_name = file.split("/")[-1]
        size = str(len(get(file).content if "http" in file else open(file,"rb").read()))		
            
        inData = {
            "file_inline":{
                "access_hash_rec":access_hash_rec,
                "auto_play":False,
                "dc_id":dc_id,
                "file_id":file_id,
                "file_name":file_name,
                "height":426,
                "mime":mime,
                "size":size,
                "thumb_inline":thumbnail,
                "time":5241,
                "type":"Video",
                "width":424
            },
            "is_mute":False,
            "object_guid":chat_id,
            "rnd":f"{randint(100000,999999999)}"
            }
        if caption != None: inData["input"]["text"] = caption

        data = {"api_version":"4","auth":bot.auth,"client":clients.android,"data_enc":bot.enc.encrypt(dumps(inData)),"method":"sendMessage"}
        while True:
            try:
                return loads(bot.enc.decrypt(post(json=data,url=Bot._getURL()).json()["data_enc"]))
                break
            except: continue

def sendmusic(chat_id, file):
        uresponse = uploadFile(file)

        file_id = str(uresponse[0]["id"])
        mime = file.split(".")[-1]
        dc_id = uresponse[0]["dc_id"]
        access_hash_rec = uresponse[1]
        file_name = file.split("/")[-1]
        size = str(len(get(file).content if "http" in file else open(file,"rb").read()))		
            
        inData = {
            "file_inline":{
                "access_hash_rec":access_hash_rec,
                "auto_play":False,
                "dc_id":dc_id,
                "file_id":file_id,
                "file_name":file_name,
                "height":0,
                "mime":mime,
                "music_performer":"♥️ Rubika",
                "size":size,
                "time":249,
                "type":"Music",
                "width":0
            },"is_mute":False,
            "object_guid":chat_id,
            "rnd":f"{randint(100000,999999999)}"
            }

        data = {"api_version":"4","auth":bot.auth,"client":clients.android,"data_enc":bot.enc.encrypt(dumps(inData)),"method":"sendMessage"}
        return loads(bot.enc.decrypt(post(json=data,url=Bot._getURL()).json()["data_enc"]))
