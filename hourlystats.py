import mytools as m
import time
import pandas as pd
import sqlite3

def processFollowers(myfollowers):
    n = len(myfollowers)
    years = []
    months = []
    days = []
    hours = []
    minutes = []
    user = []
    idle = []
    mytime = time.time()
    tmptime = time.gmtime(mytime)
    for i in range(0,n):
        years.append(tmptime[0])
        months.append(tmptime[1])
        days.append(tmptime[2])
        hours.append(tmptime[3])
        minutes.append(tmptime[4])
        user.append(m.u_to_s(myfollowers[i]['name']))
        idle.append(mytime - myfollowers[i]['updated'])
    df = pd.DataFrame({'Year': years, 'Month': months, 'Day': days, 'Hour': hours, 'Minute': minutes, 'User': user, 'Idle': idle})
    return df

def toSqlite(filename, myinput):
    cnx = sqlite3.connect(filename)
    myinput.to_sql('data',cnx)
    cnx.close()