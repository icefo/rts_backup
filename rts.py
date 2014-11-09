import json
from urllib.request import urlopen, urlretrieve
import bs4 as BeautifulSoup
import sys
def GetId (URL):
    html = urlopen(URL).read()
    soup = BeautifulSoup.BeautifulSoup(html)
    try:
        # dig in the source code if you don't get this one :
        # http://www.rts.ch/video/emissions/c-etait-mieux-avant/6226320-c-etait-mieux-avant-la-nourriture.html
        a = soup.find("param",attrs={"name":"flashVars"}).get("value")
        
        # swfReady=__player_swfReady1413...&id=6226320&jsReady=__player_jsReady1413...&volume=1
        a = a.split("&")
        # ['swfReady=__player_swfReady1413...', 'id=6226320', 'jsReady=__player_jsReady1413...', 'volume=1']
        a = {key:value for key, value in (element.split("=") for element in a)}
        # {'swfReady': '__player_swfReady1413...', 'id': '6226320', 'jsReady': '__player_jsReady1413...'}
        
        return(a["id"])
    except AttributeError as err:
        print("The main method failed, it's probably not a classic rts emission", file=sys.stderr)
        print(err, file=sys.stderr)
        try:
            # Used to get the id of infrarouge's podcasts
            # <div class="video-player-holder"     id="playerRTS"     data-video-id="4501725">
            a = soup.find("div",attrs={"id":"playerRTS"}).get("data-video-id")
            return(a)
        except Exception:
            print("The Infrarouge method failed", file=sys.stderr)
            print("this was the last avaible method so the script is going to self terminate")
            sys.exit(1)
    
    

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
    keysToTest["subtitle_url"] = ("video", "JSONinfo", "subtitles")
    
    Media_metadata = {}
    Media_metadata["VideoId"] = VideoId
    
    for key, value in keysToTest.items():
        try:
            if len(value) == 3:
                Media_metadata[key] = rawjson[value[0]][value[1]][value[2]]
            elif len(value) == 2:
                Media_metadata[key] = rawjson[value[0]][value[1]]
        except KeyError:
            print("Key '" + key + "' not present in json data", file=sys.stderr)
    

    try:
        baseUrl = rawjson["video"]["JSONinfo"].get("download")
    except KeyError:
        print("Key baseUrl not present in json data")
    try:
        MediaStreams = rawjson["video"]["JSONinfo"]["media"]
    except KeyError:
        print("Key mediaStreams not present in json data")
        
    
    return([MediaStreams, baseUrl, Media_metadata])

URL = "http://www.rts.ch/emissions/abe/6186119-gorgonzola-une-peur-bleue.html"
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
