# Youtube Api Requests
# Author: Christoph Frey
# 25.6.2022
#
# Contains functions to query from the youtube api

# API Endpoints:
# 
#
#
#
#
#
#

import urllib.request
import re
import json
import datetime
from secret import youtubeKey as api_key
# PRIVATE
# channel ids:
# polymatter 'UCgNg3vwj3xt7QOrcIDaHdFg'
# abc news ind 'UCxcrzzhQDj5zKJbXfIscCtg'


url = "https://www.googleapis.com/youtube/v3/videos?&part=snippet" # the url to the api
#### END PRIVATE


def getVideoData(vide_id, api_key):
    url = "https://www.googleapis.com/youtube/v3/videos?"
    final_api_url = url+"id="+vide_id+"&key="+api_key#+"&part=snippet"
    contents = urllib.request.urlopen(final_api_url).read()
    # content is no a b'...' string
    # print(json.loads(contents))

def getChannelUploads(channel_id, api_key):
    pass

def getVideoIdFromUrl(url: str):#
    #     var regExp = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*/;
    #     var match = video_url.match(regExp);
    #     let id = (match&&match[7].length==11)? match[7] : false;
    expression = "^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#&?]*).*"
    matches = re.match(expression, url)
    try:
        video_id = matches[7]
    except:
        video_id = None
    return video_id

def getChannelId(channel_name: str, api_key):
    
    final_api_url = "https://www.googleapis.com/youtube/v3/channels?key="+api_key+"&forUsername="+channel_name+"&part=id"
    contents = urllib.request.urlopen(final_api_url).read()
    # content is no a b'...' string
    # print(json.loads(contents))
    
    return id

def youtubeSearchApi():
    url = "https://www.googleapis.com/youtube/v3/search?&part=snippet"
    contents = urllib.request.urlopen(final_api_url).read()
    # content is no a b'...' string
    # print(json.loads(contents))

def getChannelId(channel_id, api_key):
    url = "https://www.googleapis.com/youtube/v3/channels?part=snippet&id="
    final_api_url = url + channel_id+"&key="+api_key
    contents = urllib.request.urlopen(final_api_url).read()
    print(json.loads(contents))

def getChannelUploads(channel_id, api_key):
    url = "https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id="
    final_api_url = url + channel_id+"&key="+api_key
    contents = urllib.request.urlopen(final_api_url).read()
    # print(json.loads(contents))
    # 'uploads': 'UUgNg3vwj3xt7QOrcIDaHdFg'

    uploadList = 'UUgNg3vwj3xt7QOrcIDaHdFg'
    # url = "https://www.googleapis.com/youtube/v3/playlists?part=snippet&id="
    # final_api_url = url + uploadList+"&key="+api_key
    # contents = urllib.request.urlopen(final_api_url).read()
    # print(json.loads(contents))
    url = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId="
    final_api_url = url + uploadList+"&key="+api_key
    contents = urllib.request.urlopen(final_api_url).read()
    jcontent = json.loads(contents)
    # print(json.loads(contents))
    # [print(item['snippet']['title'], " ", item['snippet']['publishedAt']) for item in jcontent["items"]]

# check for 
def checkForUploads(uploadLists, lastChecked, api_key):
    # check wether there are any new videos since last check

    for uploadList in uploadLists:
        url = "https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId="
        final_api_url = url + uploadList+"&key="+api_key
        contents = urllib.request.urlopen(final_api_url).read()
        jcontent = json.loads(contents)
        videos.append(jcontent["items"])
    
    newVideos = []
    # check wether there are any new videos
    for video in videos:
        # check for new videos
        if video['snippet']['publishedAt'] > lastChecked:
            newVIdeos.append(video['snippet'])
    
    return newVideos

def isNew(time1, time2):
    # print("comparing")
    # print(time1)
    # print(datetime.datetime.fromisoformat(time2[:-1]))#+'+00:00'))
    # print(datetime.datetime.now())
    # t1 = datetime.datetime.fromisoformat(time2[:-1])#+'+00:00')
    # t2 = datetime.datetime.now()
    # print(t1 < t2)
    # exit()
    # print(time1)
    # # print(time2)
    # print(datetime.datetime.fromisoformat(time2[:-1]+"+00:00"))
    # print(time1.replace)
    # print(time2)
    # exit()

    if time1 is None:
        return True
    else:
        # assumes time1 is in 0001-01-01 00:00:00 format
        t1 = time1.replace(tzinfo=datetime.timezone.utc)
        # assumes that time2 is in isoformat i.e. 2022-07-04T17:05:00Z
        t2 = datetime.datetime.fromisoformat(time2[:-1]+"+00:00")
        return t2>t1

def newVideos(channel_list, last_time, api_key):
    """
    get the new videos for the channels in the list
    list should have the format (upload_id, channel_id, channel_name, last_checked)
    """
    new_videos = []
    for uploads, channel, channel_name, _ in channel_list:
        # get the uploads of the channel
        url = "https://www.googleapis.com/youtube/v3/playlistItems?key="+api_key+"&part=snippet&playlistId="
        final_api_url = url + uploads
        contents = urllib.request.urlopen(final_api_url).read()
        jcontent = json.loads(contents)
        # print(jcontent['items'])
        uploaded_videos = [item for item in jcontent['items']]
        
        # print(uploaded_video)
        new_ones = list(filter(lambda video: isNew(last_time, video['snippet']['publishedAt']) ,uploaded_videos))
        new_ones = [(item['snippet']['title'], item['id'], item['snippet']['channelId'], item['snippet']['publishedAt'], "https://www.youtube.com/watch?v="+item['snippet']['resourceId']['videoId']) 
        for item in new_ones] #(name text, video_id text, channel_id text, uploadTime text, url text)
        # print(uploaded_video)
        # print(new_ones)
        # [print(item['snippet']['title']) for item in jcontent['items']]
        # return jcontent
        if len(new_ones)!=0:
            new_videos.append((channel_name, new_ones))
    # print(new_videos)
    return new_videos

def getMultiplePlaylists(playlists, api_key):
    # does not work from playlist ID
    url = "https://www.googleapis.com/youtube/v3/playlistItems?key="+api_key+"&part=snippet&playlistId="
    for pl in playlists:
        url = url + pl + "," 
    final_api_url = url[:-1]
    # print(final_api_url)
    # exit()
    contents = urllib.request.urlopen(final_api_url).read()
    jcontent = json.loads(contents)
    print(jcontent['items'])

def getChannelAndUploadId(video_url, api_key):
    # from the given url to a video get:
    # the channel id (just query the video, take the channel id)
    # the uploadListId (query the channel)
    
    video_id = getVideoIdFromUrl(video_url)
    # print(video_id)

    # get the metadata of the video from youtube
    url = "https://www.googleapis.com/youtube/v3/videos?part=snippet&key="+api_key+"&id="
    final_api_url = url + video_id
    contents = urllib.request.urlopen(final_api_url).read()
    jcontent = json.loads(contents)
    # print(jcontent['items'][0]['snippet']['channelId'])

    # get channel id
    channel_id = jcontent['items'][0]['snippet']['channelId']

    # get the data from the channel
    url = "https://www.googleapis.com/youtube/v3/channels?part=contentDetails&key="+api_key+"&id="
    final_api_url = url + channel_id

    contents = urllib.request.urlopen(final_api_url).read()
    jcontent = json.loads(contents)
    # print(jcontent['items'][0]['contentDetails']['relatedPlaylists']['uploads'])

    upload_id = jcontent['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    url = "https://www.googleapis.com/youtube/v3/channels?part=snippet&key="+api_key+"&id="
    final_api_url = url + channel_id

    contents = urllib.request.urlopen(final_api_url).read()
    jcontent = json.loads(contents)
    # print(jcontent['items'][0]['snippet']['title'])

    channel_name = jcontent['items'][0]['snippet']['title']

    # returns upload id, channel id, and name
    return upload_id, channel_id, channel_name
    

if __name__ == "__main__":
    v_url = "https://www.youtube.com/watch?v=Vnwji5doAbs"
    #id = getVideoIdFromUrl(v_url)
    #getVideoData(id, api_key)
    c_url = "https://www.youtube.com/c/ABCNewsIndepth"
    channel_name = "ABCNewsIndepth"
    #getChannelId(channel_name, api_key)
    channel_id = 'UCgNg3vwj3xt7QOrcIDaHdFg'
    # getChannelUploads(channel_id, api_key)
    video_url = "https://www.youtube.com/watch?v=uAdmzyKagvE"
    # video_id = getVideoIdFromUrl(v_url)
    # print(video_id)
    
    # x = getChannelAndUploadId(video_url, api_key)
    watch_list = [('UUBa659QWEk1AI4Tg--mrJ2A', 'UCBa659QWEk1AI4Tg--mrJ2A', 'Tom Scott')]
    # new = newVideos(watch_list,None, api_key)
    # print(new)

    # get multiple upload lists at the same time
    pl1 = "UUR9X2tT0_WVfuYO17vqstlA"
    pl2 = "UU6n8I1UDTKP1IWjQMg6_TwA"
    getMultiplePlaylists([pl1, pl2], api_key)
