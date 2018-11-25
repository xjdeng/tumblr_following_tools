import pytumblr as py
import pandas as pd
import time
import unicodedata
import http.client
import httplib2
import random
import socket
import sys
from selenium import webdriver
from path import Path as path
from PIL import Image
import piexif
import re
from urllib.parse import urlparse

usual_suspects = (IOError, http.client.HTTPException, httplib2.ServerNotFoundError, socket.error, socket.timeout)

default_timeout = 10;

def randdelay(a,b):
    time.sleep(random.uniform(a,b))

def getClient(credentials):
    df = pd.read_csv(credentials)
    client = py.TumblrRestClient(df['ConsumerKey'][0], df['ConsumerSecret'][0], df['OauthToken'][0], df['OauthSecret'][0])
    return client


def cleanup(myblog, mylist, fdays=50):
    newlist = []
    for i in mylist:
        try:
            tmp = myblog.blog_info(i.rstrip())
            updated = tmp['blog']['updated']
            tmptime = (time.time() - updated )/86400.0
            if tmptime < fdays:
                newlist.append(i)
        except KeyError:
            pass              
    return newlist

def isimage(myfile):
    try:
        Image.open(myfile)
        return True
    except IOError:
        return False
    
def name(myblog,blogNumber=0):
    goahead = False
    while goahead == False:
        try:
            minfo = myblog.info()
            minfo2 = minfo['user']['blogs'][blogNumber]
            targetBlog = u_to_s(minfo2['name'])
            goahead = True
        except usual_suspects:
            goahead = False
    return targetBlog   

def load_tumblr_csv(myfile):
    tmp = pd.read_csv(myfile, header=None).values.tolist()
    tmp2 = []
    for i in range(0,len(tmp)):
        tmp2.append(tmp[i][0])
    return tmp2

def save_tumblr_csv(myfile, mylist):
    tmp = pd.DataFrame(mylist)
    tmp.to_csv(myfile, index=False, header = False)

def bulk_scrape_users(myfile, browser = None):
    from . import scrape_users
    if browser is None:
        browser = webdriver.Firefox()
    tmp = set(load_tumblr_csv(myfile))
    everybody = []
    reblogged = []
    liked = []
    for i in tmp:
        try:
            (a,b,c) = scrape_users.runme(i,browser=browser)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            print(i)
            browser.close()
            return((list(set(everybody)),list(set(reblogged)),list(set(liked))))
        everybody += a
        reblogged += b
        liked += c
    browser.close()
    return((list(set(everybody)),list(set(reblogged)),list(set(liked))))

def tumblr_follow_html(mylist,outfile="followme.html"):
    n = len(mylist)
    f = open(outfile,'w')
    for i in range(0,n):
        myurl = strip_tumblr(mylist[i])
        mystr = "<p><a href=\"http://www.tumblr.com/follow/{}\" target=\"blank\">{}</a></p>\n".format(myurl,myurl)
        f.write(mystr)
    f.close()

def auto_unfollow(mylist, myclient, verbose=False, timeout = default_timeout):
    n = len(mylist)
    socket.setdefaulttimeout(timeout)
    for i in range(0,n):
        randdelay(1,3)
        if verbose == True:
            print("Trying blog #:{}".format(1+i))
        goahead = False
        while goahead == False:
            try:
                tmp = myclient.unfollow(mylist[i])
                goahead = True
                if verbose == True:
                    print("\n{}\n".format(tmp))
            except usual_suspects:
                goahead = False
    
def strip_tumblr(mystr):
    mystr = mystr.rstrip()
    if len(mystr) < 11:
        return mystr
    elif mystr[len(mystr)-11:] == ".tumblr.com":
        return mystr[0:len(mystr)-11]
    else:
        return mystr

def append_tumblr(mystr):
    mystr = mystr.rstrip()
    if len(mystr) < 11:
        return mystr + ".tumblr.com"
    elif mystr[len(mystr)-11:] == ".tumblr.com":
        return mystr
    else:
        return mystr + ".tumblr.com"

def same_tumblr(a,b):
    a2 = strip_tumblr(a)
    b2 = strip_tumblr(b)
    return (a2 == b2)

def find_tumblr(mykey,mylist):
    n = len(mylist)
    i = 0
    while i < n:
        if same_tumblr(mykey, mylist[i]):
            return True
        i += 1
    return False

def u_to_s(uni):
    return unicodedata.normalize('NFKD',uni).encode('ascii','ignore')

def blogname(myraw,i):
    return u_to_s(myraw[i]['uuid'])

def staleBlogs(myblog = None, myraw = None, days=50, verbose=False):
    if myraw == None:
        myraw = rawF(myblog.following, verbose = verbose)
    fdays = float(days)
    result = []
    for i in range(0,len(myraw)):
        tmptime = (time.time() - myraw[i]['updated'] )/86400.0
        if tmptime > fdays:
            result.append(myraw[i]['name'])
    return result
    

def rawF(myfunction, waittime = 1, autorestart = True, verbose = False, cutoff = None, timeout = default_timeout): #myfunction default: client.following
    socket.setdefaulttimeout(timeout)
    goahead = False
    while goahead == False:
        try:
            n = myfunction()['total_blogs']
            goahead = True
        except usual_suspects:
            goahead = False
    if cutoff != None:
        n = min(n,cutoff)
    m = 20
    rem = n % m
    cycles = int(n/m)
    result = []
    for i in range(0,cycles):
        if verbose == True:
            print("Trying Blogs {} to {}".format(m*i + 1, m*i + m))
        params = {'offset': m*i, 'limit': m}
        goahead = False
        while goahead == False:
            try:
                time.sleep(waittime)
                tmp = myfunction(**params)
                goahead = True
            except usual_suspects:
                goahead = False
        result = result + tmp['blogs']
    params = {'offset': m*cycles, 'limit': rem}
    if verbose == True:
        print("Finishing...")
    if rem != 0:
        goahead = False
        while goahead == False:
            try:
                time.sleep(waittime)
                tmp = myfunction(**params)
                goahead = True
            except usual_suspects:
                goahead = False
        result = result + tmp['blogs']
    return result

def getFollowers(myblog, waittime = 1, autorestart = True, verbose = False, cutoff = None, timeout = default_timeout, targetBlog = None, blogNumber=0):
    socket.setdefaulttimeout(timeout)
    goahead = False
    while goahead == False:
        try:
            minfo = myblog.info()
            minfo2 = minfo['user']['blogs'][blogNumber]
            if targetBlog == None:
                targetBlog = u_to_s(minfo2['name'])
            n = myblog.followers(targetBlog)['total_users']
            goahead = True
        except usual_suspects:
            goahead = False

    if cutoff != None:
        n = min(n,cutoff)
    m = 20
    rem = n % m
    cycles = n/m
    result = []    
    for i in range(0,cycles):
        if verbose == True:
            print("Trying Blogs {} to {}".format(m*i + 1, m*i + m))
        params = {'offset': m*i, 'limit': m}
        goahead = False
        while goahead == False:
            try:
                time.sleep(waittime)
                tmp = myblog.followers(targetBlog,**params)
                goahead = True
            except usual_suspects:
                goahead = False
        result = result + tmp['users']
    params = {'offset': m*cycles, 'limit': rem}
    if verbose == True:
        print("Finishing...")
    if rem != 0:
        goahead = False
        while goahead == False:
            try:
                time.sleep(waittime)
                tmp = myblog.followers(targetBlog,**params)
                goahead = True
            except usual_suspects:
                goahead = False
        result = result + tmp['users']
    return result
    
def getPosts(myblog, waittime = 1, autorestart = True, verbose = False, cutoff = None, timeout = default_timeout, targetBlog = None, blogNumber=0, blogtype=None, blogcutoff = None, dayscutoff = None):
    socket.setdefaulttimeout(timeout)
    goahead = False
    while goahead == False:
        try:
            minfo = myblog.info()
            goahead = True
        except usual_suspects:
            goahead = False
    minfo2 = minfo['user']['blogs'][blogNumber]
    n = minfo2['posts']
    if targetBlog == None:
        targetBlog = u_to_s(minfo2['name'])
    else:
        tmpinfo = myblog.blog_info(targetBlog)
        n = tmpinfo['blog']['posts']
    if cutoff != None:
        n = min(n,cutoff)
    m = 20
    rem = n % m
    cycles = round(n/m)
    result = []
    breakfor = False
    for i in range(0,cycles):
        if verbose == True:
            print("Trying Posts {} to {}".format(m*i + 1, m*i + m))
        params = {'offset': m*i, 'limit': m, 'reblog_info': True}
        if blogtype is not None:
            params['type'] = blogtype
        goahead = False
        while goahead == False:
            try:
                time.sleep(waittime)
                tmp = myblog.posts(targetBlog,**params)
                if blogcutoff is not None:
                    for t in tmp['posts']:
                        if t['id'] == blogcutoff:
                            breakfor = True
                if dayscutoff is not None:
                    for t in tmp['posts']:
                        if (time.time() - t['timestamp'])/86400.0 > dayscutoff:
                            breakfor = True
                goahead = True
            except usual_suspects:
                goahead = False
        try:
            result = result + tmp['posts']
        except KeyError:
            pass
        if breakfor:
            break
    params = {'offset': m*cycles, 'limit': rem, 'reblog_info': True}
    if blogtype is not None:
        params['type'] = blogtype
    if verbose == True:
        print("Finishing...")
    if rem != 0:
        goahead = False
        while goahead == False:
            try:
                time.sleep(waittime)
                tmp = myblog.posts(targetBlog,**params)
                goahead = True
            except usual_suspects:
                goahead = False
        result = result + tmp['posts']
    return result 

def getImagePosts(myblog, myposts = None, verbose=True, blogNumber=0, targetBlog = None, blogcutoff=None, ignore_reblogs = False, dayscutoff = None):
    if myposts is None:
        myposts = getPosts(myblog, waittime = 1, autorestart = True, verbose = verbose, cutoff = None, timeout = default_timeout, targetBlog = targetBlog, blogNumber=blogNumber, blogtype="photo", blogcutoff = blogcutoff, dayscutoff = dayscutoff)
    dates = []
    postURLs = []
    imageURLs = []
    notes = []
    reblog = []
    _id = []
    for p in myposts:
        if ((p['trail'] == []) or (ignore_reblogs == False)) & (p['type'] == 'photo'):
            dates.append(p['date'])
            postURLs.append(p['post_url'])
            imageURLs.append(p['photos'][0]['original_size']['url'])
            notes.append(p['note_count'])
            reblog.append(p['reblog_key'])
            _id.append(p['id'])
    results = pd.DataFrame()
    results['Date'] = dates
    results['Post URL'] = postURLs
    results['Image URL'] = imageURLs
    results['Notes'] = notes
    results['reblog_key'] = reblog
    results['id'] = _id
    return results
    
def getPostTitles(posts):
    titles = []
    for p in posts:
        try:
            mytitle = p['title']
            tmptitle = u_to_s(mytitle)
            if len(tmptitle) > 0:
                titles.append(tmptitle.replace("\r","").replace("\n",""))
        except TypeError:
            pass
        except KeyError:
            try:
                mytitle = p['summary']
                tmptitle = u_to_s(mytitle)
                if len(tmptitle) > 0:
                    titles.append(tmptitle.replace("\r","").replace("\n",""))
            except (TypeError, KeyError):
                pass
    return titles
                

def getF(myfunction=None, flist = None, waittime=1, myraw = None, cutoff = None, verbose = False, timeout = 10): #myfunction default: client.following
    if flist == None:
        if myraw == None:
            myraw = rawF(myfunction = myfunction, waittime = waittime,cutoff = cutoff, verbose = verbose, timeout = timeout)
        result = []
        for i in range(0,len(myraw)):
            result.append(blogname(myraw,i))
        return result
    else:
        return load_tumblr_csv(flist) 
#CSV Structure:
#Column 1: blog name
#Column 2: post id
#Column 3: reblog key
        
def convert_url(url):
    tumblr = urlparse(url).hostname
    match0 = re.findall("(?<=post/)\d*", url)
    if len(match0) == 0:
        match = None
    else:
        match = match0[0]
    return tumblr, match

def getReblogKey(myblog, url, timeout = default_timeout):
    myblogname, mypost = convert_url(url)
    return getReblogKey_alt(myblog, myblogname, mypost, timeout)
        
def getReblogKey_alt(myblog, myblogname, mypost, timeout = default_timeout):
    socket.setdefaulttimeout(timeout)
    goahead = False
    output = None
    while goahead == False:
        try:
            output0 = myblog.posts(myblogname, id=mypost)
            output = output0['posts'][0]['reblog_key']
            goahead = True
        except usual_suspects:
            pass
        except KeyError:
            goahead = True
    return output
            
    

def mass_queue(myblog, myblogname, mycsv):
    myqueue = pd.read_csv(mycsv, header=None)
    for i in range(0,len(myqueue)):
        myblog.reblog(myblogname,id=myqueue.loc[i,1],reblog_key=myqueue.loc[i,2],state="queue")

def mass_reblog(myblog, myblogname, mycsv):
    myposts = pd.read_csv(mycsv, header=None)
    for i in range(0,len(myposts)):
        myblog.reblog(myblogname,id=myposts.loc[i,1],reblog_key=myposts.loc[i,2])
        
def queue_folder(myblog, myblogname, folder, tags=[]):
    myfolder = path(folder)
    for f in myfolder.files():
        if isimage(f) == True:
            try:
                piexif.remove(f)
            except piexif.InvalidImageDataError:
                pass
            myblog.create_photo(myblogname, state="queue", tags=tags, data=str(f))
            
def post_folder(myblog, myblogname, folder, tags = []):
    myfolder = path(folder)
    myfiles = []
    for f in myfolder.files():
        if isimage(f) == True:
            myfiles.append(f)
    if len(myfiles) > 10:
        random.shuffle(myfiles)
        myfiles = myfiles[0:10]
    myblog.create_photo(myblogname, state="post", tags=tags, data=myfiles)
            
def get_all_files(folder):
    f = path(folder)
    folders = f.dirs()
    files = f.files()
    result = files
    for i in folders:
        result += get_all_files(i)
    return result

def all_subdirs(tgt):
    """
Get a list of all subdirectories under and including tgt.
    """
    p = path(tgt)
    dirs = p.dirs()
    result = dirs + [tgt]
    if len(dirs) <= 1:
        return result    
    for d in dirs:
        result += all_subdirs(d)
    return list(set(result))

def get_random_images(folder, num):
    files = get_all_files(folder)
    random.shuffle(files)
    images = []
    i = 0
    while (len(images) < num) & (i < len(files)):
        test = files[i]
        i += 1
        if isimage(test) == True:
            images.append(test)
    return images

def get_random_images_alt(folder, num):
    subfolders = all_subdirs(folder)
    random.shuffle(subfolders)
    i = 0
    images = []
    while (len(images) < num) & (i < len(subfolders)):
        files = path(subfolders[i]).files()
        random.shuffle(files)
        j = 0
        goahead = False
        while (j < len(files)) & (len(images) < num) & (goahead == False):
            test = files[j]
            j += 1
            if isimage(test) == True:
                images.append(test)
                goahead = True
        i += 1
    return images
    
def copy_random_images(source, destination, num = 50, copier = get_random_images):
    images = copier(source, num)
    for i in images:
        f = path(i)
        try:
            piexif.remove(i)
        except (IOError, piexif.InvalidImageDataError):
            pass
        f.copy(destination + "/" + f.namebase + str(random.randint(1,1000000000)) + f.ext)      
        
def follow_wizard(target,myfollowing,maxfollow=200):
    targets = 0
    random.shuffle(target)
    n = len(target)
    i = 0
    result = []
    while (targets < maxfollow) & (i < n):
        finder = find_tumblr(target[i],myfollowing)
        if finder == False:
            targets += 1
            result.append(target[i].rstrip())
        i += 1
    return result
            