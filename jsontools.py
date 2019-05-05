import json
import pandas as pd

def loadjson(tumblrjson):
    with open(tumblrjson) as json_file:  
        return json.load(json_file)  

def parsejson(myjson):
    if isinstance(myjson, str):
        myjson = loadjson(myjson)
    urls = []
    imgurls = []
    for post in myjson:
        try:
            imgurl = post['post_url']
            for im in post['photos']:
                try:
                    im2 = im['original_size']
                    if im2['width']*im2['height'] < 250000:
                        continue
                    url = im2['url']
                    urls.append(url)
                    imgurls.append(imgurl)
                except KeyError:
                    pass
        except KeyError:
            pass
    result = pd.DataFrame()
    result['url'] = urls
    result['imgurl'] = imgurls
    return result