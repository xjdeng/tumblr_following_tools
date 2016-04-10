import pytumblr as py
import pandas as pd
import time
import unicodedata

def getClient(credentials):
    df = pd.read_csv(credentials)
    client = py.TumblrRestClient(df['ConsumerKey'][0], df['ConsumerSecret'][0], df['OauthToken'][0], df['OauthSecret'][0])
    return client

def load_tumblr_csv(mylist):
    tmp = pd.read_csv(mylist, header=None).values.tolist()
    tmp2 = []
    for i in range(0,len(tmp)):
        tmp2.append(tmp[i][0])
    return tmp2

def tumblr_follow_html(mylist,outfile="followme.html"):
    n = len(mylist)
    f = open(outfile,'w')
    for i in range(0,n):
        myurl = mylist[i]
        mystr = "<p><a href=\"http://www.tumblr.com/follow/{}\" target=\"blank\">{}</a></p>\n".format(myurl,myurl)
        f.write(mystr)
    f.close()
        
    
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
    
def getF(myfunction, flist = None, offset0 = 0, waittime=1, autorestart = True): #myfunction default: client.following
    if flist == None:
        import httplib
        n = myfunction()['total_blogs']
        m = 20
        rem = n % m
        cycles = n/m
        cycle0 = offset0/m
        result = []
        for i in range(cycle0,cycles):
            time.sleep(waittime)
            params = {'offset': m*i, 'limit': m}
            try:
                tmp = myfunction(**params)
            except (IOError, httplib.HTTPException):
                if autorestart == False:
                    print "Warning! Error in retrieving followers! Partial list returned!"
                    print "List size: {}, Total size: {}, Rerun with offset0 = {}".format(len(result), n, offset0 + len(result))
                else:
                    print "Error. Autocorrecting"
                    myresult = getF(myfunction = myfunction, flist = flist, offset0 = offset0 + len(result), waittime = waittime, autorestart = autorestart)
                    result = result + myresult
                return result                
            for j in range(0,m):
                result.append(u_to_s(tmp['blogs'][j]['uuid']))
        params = {'offset': m*cycles, 'limit': rem}
        tmp = myfunction(**params)
        for j in range(0,rem):
            result.append(u_to_s(tmp['blogs'][j]['uuid']))
        return result                
    else:
        return load_tumblr_csv(flist)
        
def follow_wizard(target,myfollowing,maxfollow=200):
    if maxfollow > 200:
        maxfollow = 200
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
            