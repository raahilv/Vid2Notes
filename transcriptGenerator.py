"""
Input: URL - YouTube URL as a String
Output: textChunks - a list of strings
Take in a URL input, process and generate the transcript output, divided into approximately 5 min chunks
"""
import urllib.request
import json
import urllib
import pprint
from youtube_transcript_api import YouTubeTranscriptApi

test_URL = "https://www.youtube.com/watch?v=y1WYANJ7IPc&list=PLlwePzQY_wW8P_I8BFgm0-upywEwTKd8_&index=16" #Calc Continuity Lecture
#test_URL = "https://www.youtube.com/watch?v=r6sGWTCMz2k" #3Blue1Brown Fourier Series
#test_URL = "https://www.youtube.com/watch?v=9k97m8oWnaY" #Calc 3 Surface Integrals
#test_URL = "https://www.youtube.com/watch?v=WCwJNnx36Rk" #Ben Eater Bi-Stable 555 circuit video
#test_URL = "https://www.youtube.com/watch?v=kRlSFm519Bo" #Ben Eater Astable 555 circuit video
#test_URL = "https://www.youtube.com/watch?v=sQ0BJ3H-cZ8" #Calc 3 by Prof Leonard, HAS NO TRANSCRIPT!

"""
TO DO:
make chunk minimums such that if the time remaining in a video is below minTime, take some of the transcript from the previous X seconds
where X = minTime - actualTime
this results in an overlap b/n the 2nd last and last indicies
limit by word instead of time
"""

def generate_transcript(url):
    # get the transcript from Youtube API

    vid_id = get_video_id(url)

    try:
        response = YouTubeTranscriptApi.get_transcript(vid_id)
        #print(response)

        textChunks = []
        wordLimit = int(4000/3)
        minWords = int(1000/3)
        wordCount = 0
        slot = 0

        textChunks.append("")

        """
        response gives a list of dictionary as follows
        text: string
        start: float (in seconds)
        duration: float (in seconds)
        we want to read and store our transcript into 5 minute chunks
        """
        for dict in response:
            if(wordCount >= wordLimit):
                #reached word limit of chunk, make a new chunk
                wordCount = 0
                slot += 1
                textChunks.append("")
            else:
                # transcribe into chunk and count words
                transcriptClip = dict["text"] + " "
                textChunks[slot] += transcriptClip
                wordCount += get_word_count(transcriptClip)
        
        #check if last chunk is too short
        if(get_word_count(str(textChunks[-1])) <= minWords):
            #add words to the start of the string
            
            lastChunk = (textChunks[-1]).split()
            
            prevChunk = (textChunks[len(textChunks)-2]).split()
            #print(prevChunk)

            for k in range(len(prevChunk)):
                # i indicates the end of prevChunk
                #print("enter")               
                i = len(prevChunk) - k
                if(i >= (minWords - get_word_count(str(textChunks[-1])))):
                    #add these to the front of the textChunk
                    #print("append")
                    lastChunk.insert(0, prevChunk[i-1])

            # reconvert to a string and replace last chunk with new string
            #print(lastChunk)
            textChunks[-1] = lastChunk
        
        """   
        for dict in response:
            if(time >= maxRead):
                # when we have read 5ish minutes, make a new entry into textChunks
                time = 0
                slot += 1
                textChunks.append("")
                #print("new")
            else:
                # write the transcript segment into the current textChunks slot
                transcriptClip = dict["text"] + " "
                textChunks[slot] += transcriptClip
                time += dict["duration"]
            """
        #print(textChunks[0])
        #print(slot)
        #print(len(textChunks))
        #print(textChunks[-1])

        # insert title as first index
        textChunks.insert(0, get_title(vid_id))
        return textChunks
    except:
        print("ERROR CODE 1: NO TRANSCRIPT FOUND")
        return ""

def get_word_count(text):
    text_list = text.split()
    return len(text_list)


def get_video_id(url):
    v_id_pos = url.find("=")
    end_id_pos = url.find("&")
    vid_id = []

    #Get Video ID from url
    if(end_id_pos == -1):
        # no and sign, just remove LHS of url
        vid_id = url[v_id_pos+1::]
    else:
        vid_id = url[v_id_pos+1:end_id_pos]

    return vid_id

def get_title(vid_id):
    params = {"format": "json", "url": "https://www.youtube.com/watch?v=%s" % vid_id}
    url = "https://www.youtube.com/oembed"
    query_string = urllib.parse.urlencode(params)
    url = url + "?" + query_string

    with urllib.request.urlopen(url) as response:
        response_text = response.read()
        data = json.loads(response_text.decode())
        #pprint.pprint(data)
        #print(data['title'])
        return data['title']



"""
Debug:

"""
testOut = generate_transcript(test_URL)
print(str(testOut))