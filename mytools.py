import pytumblr as py
import pandas as pd
import time
import unicodedata
import httplib
import httplib2
import random
import socket

usual_suspects = (IOError, httplib.HTTPException, httplib2.ServerNotFoundError, socket.error, socket.timeout)

default_timeout = 10;

def randdelay(a,b):
    time.sleep(random.uniform(a,b))

def getClient(credentials):
    df = pd.read_csv(credentials)
    client = py.TumblrRestClient(df['ConsumerKey'][0], df['ConsumerSecret'][0], df['OauthToken'][0], df['OauthSecret'][0])
    return client

def blogExists(client, blog):
    a = client.blog_info(blog)
    try:
        tmp = a['blog']
        return True
    except KeyError:
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

def bulk_scrape_users(myfile):
    import scrape_users
    tmp = set(load_tumblr_csv(myfile))
    everybody = []
    reblogged = []
    liked = []
    for i in tmp:
        (a,b,c) = scrape_users.runme(i)
        everybody += a
        reblogged += b
        liked += c
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
            print "Trying blog #:{}".format(1+i)
        goahead = False
        while goahead == False:
            try:
                tmp = myclient.unfollow(mylist[i])
                goahead = True
                if verbose == True:
                    print "\n{}\n".format(tmp)
            except usual_suspects:
                goahead = False
    
def strip_tumblr(mystr):
    if len(mystr) < 11:
        return mystr
    elif mystr[len(mystr)-11:] == ".tumblr.com":
        return mystr[0:len(mystr)-11]
    else:
        return mystr

def append_tumblr(mystr):
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
            result.append(blogname(myraw,i))
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
    cycles = n/m
    result = []
    for i in range(0,cycles):
        if verbose == True:
            print "Trying Blogs {} to {}".format(m*i + 1, m*i + m)
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
        print "Finishing..."
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
            print "Trying Blogs {} to {}".format(m*i + 1, m*i + m)
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
        print "Finishing..."
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
    
def getPosts(myblog, waittime = 1, autorestart = True, verbose = False, cutoff = None, timeout = default_timeout, targetBlog = None, blogNumber=0):
    socket.setdefaulttimeout(timeout)
    goahead = False
    while goahead == False:
        try:
            minfo = myblog.info()
            goahead = True
        except usual_suspects:
            goahead = False
    minfo2 = minfo['user']['blogs'][blogNumber]
    if targetBlog == None:
        targetBlog = u_to_s(minfo2['name'])
    n = minfo2['posts']
    if cutoff != None:
        n = min(n,cutoff)
    m = 20
    rem = n % m
    cycles = n/m
    result = []
    for i in range(0,cycles):
        if verbose == True:
            print "Trying Posts {} to {}".format(m*i + 1, m*i + m)
        params = {'offset': m*i, 'limit': m}
        goahead = False
        while goahead == False:
            try:
                time.sleep(waittime)
                tmp = myblog.posts(targetBlog,**params)
                goahead = True
            except usual_suspects:
                goahead = False
        result = result + tmp['posts']
    params = {'offset': m*cycles, 'limit': rem}
    if verbose == True:
        print "Finishing..."
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
        
def follow_wizard(target,myfollowing,maxfollow=200):
    targets = 0
    n = len(target)
    i = 0
    result = []
    while (targets < maxfollow) & (i < n):
        finder = find_tumblr(target[i],myfollowing)
        if finder == False:
            targets += 1
            result.append(target[i])
        i += 1
    return result
            