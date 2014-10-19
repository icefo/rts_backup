import json
from urllib.request import urlopen, urlretrieve
from time import time
import bs4 as BeautifulSoup
import sys
def GetId (URL):
    html = urlopen(URL).read()
    soup = BeautifulSoup.BeautifulSoup(html)
    try:
        # dig in the source code if you don't get this one : http://www.rts.ch/video/emissions/c-etait-mieux-avant/6226320-c-etait-mieux-avant-la-nourriture.html
        a = soup.find("param",attrs={"name":"flashVars"}).get("value")
    except Exception:
        print("Impossible to find the video's id\nGood luck :-)", file=sys.stderr)
        sys.exit(1)
    
    # swfReady=__player_swfReady1413...&id=6226320&jsReady=__player_jsReady1413...&volume=1&autoPlay=true&showLargeButton=true&withSub=true
    a = a.split("&")
    # ['swfReady=__player_swfReady1413...', 'id=6226320', 'jsReady=__player_jsReady1413...', 'volume=1', 'autoPlay=true', 'showLargeButton=true', 'withSub=true']
    b = {key:value for key, value in (element.split("=") for element in a)}
    # {'swfReady': '__player_swfReady1413...', 'id': '6226320', 'jsReady': '__player_jsReady1413...', 'withSub': 'true', 'autoPlay': 'true', 'showLargeButton': 'true', 'volume': '1'}
    
    return(b["id"])

def MediasInfos (VideoId):
    html = urlopen("http://www.rts.ch/?format=json/video&id="+VideoId).read()
    soup = BeautifulSoup.BeautifulSoup(html).text
    rawjson = json.loads(soup)
    
    keysToTest = {}
    keysToTest["rawTitle"] = ("video", "rawTitle")
    #keysToTest["download_domain"] = ("video", "JSONinfo", "download")
    keysToTest["programName"] = ("video", "JSONinfo", "programName")
    keysToTest["broadcastDate"] = ("video", "JSONinfo", "broadcastDate")
    keysToTest["intro"] = ("video", "JSONinfo", "intro")
    keysToTest["preview_image_url"] = ("video", "JSONinfo", "preview_image_url")
    
    MediasInfos = {}
    MediasInfos["VideoId"] = VideoId
    
    for key, value in keysToTest.items():
        try:
            if len(value) == 3:
                MediasInfos[key] = rawjson[value[0]][value[1]][value[2]]
            elif len(value) == 2:
                MediasInfos[key] = rawjson[value[0]][value[1]]
            else:
                print("Something went wrong", file=sys.stderr)
                sys.exit(1)
        except KeyError:
            print("Key " + key + " not present in json data")
    

    try:
        baseUrl = rawjson["video"]["JSONinfo"].get("download")
        MediaStreams = rawjson["video"]["JSONinfo"]["media"]
    except KeyError:
        print("Key media not present in json data")
    
    return([MediaStreams, baseUrl, MediasInfos])

URL = "http://www.rts.ch/emissions/ttc/6095654-radars-a-qui-profite-le-flash.html"
mediaResults = MediasInfos(GetId(URL))

MediaUrl = mediaResults[0]
baseUrl = mediaResults[1]

MediaUrl = [media for media in MediaUrl if media.get("ext") == "mp4"]
bitrate = []
for media in MediaUrl:
    media["rate"] = int(media["rate"])
    bitrate.append(media["rate"])
MediaUrl = MediaUrl[bitrate.index(max(bitrate))]["url"].split("?")[0]
if not (MediaUrl.startswith('http://') or MediaUrl.startswith('https://')):
    MediaUrl = baseUrl + MediaUrl

print(MediaUrl)
    
urlretrieve(MediaUrl, mediaResults[2]["rawTitle"] + ".mp4")
