import pandas as pd
def loadFollowList(mylist):
    return pd.read_csv(mylist, header=None)