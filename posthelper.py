import pandas as pd
import time
import mytools as m
import sqlite3

def processPosts(myposts):
    n = len(myposts)
    years = []
    months = []
    days = []
    hours = []
    minutes = []
    minutesOfDay = []
    notes = []
    for i in range(0,n):
        if 'source_url' not in myposts[i]:
            tmptime = time.gmtime(myposts[i]['timestamp'])
            years.append(tmptime[0])
            months.append(tmptime[1])
            days.append(tmptime[2])
            hours.append(tmptime[3]-1)
            minutes.append(tmptime[4])
            minutesOfDay.append(tmptime[3]*60 + tmptime[4])
            notes.append(myposts[i]['note_count'])    
    df = pd.DataFrame({'Year': years, 'Month': months, 'Day': days, 'Hour': hours, 'Minute': minutes,
                       'MinuteOfDay': minutesOfDay, 'Notes': notes})
    return df

def dumpBlog(credentials):
    blog = m.getClient(credentials)
    myposts = m.getPosts(blog)
    return processPosts(myposts)
    
def toSqlite(filename, myinput):
    cnx = sqlite3.connect(filename)
    myinput.to_sql('posts',cnx)
    cnx.close()